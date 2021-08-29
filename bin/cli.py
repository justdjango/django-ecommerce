import click
import os
import subprocess
import sys

from shared import verify_environment
from commands import (
    settings_command,
    create_server_command,
    azure_firewall_command,
    get_local_ip_firewall_command,
    create_db_command,
    connect_details_command
)


def get_settings_command():
    verify_environment()
    SETTINGS_KEYS = (
        'SECRET_KEY',
        'POSTGRES_SERVER_NAME',
        'POSTGRES_ADMIN_USER',
        'POSTGRES_ADMIN_PASSWORD',
        'POSTGRES_HOST',
        'APP_DB_NAME',
        'DJANGO_SETTINGS_MODULE',
        'AZ_STORAGE_ACCOUNT_NAME',
        'AZ_STORAGE_CONTAINER',
        'AZ_STORAGE_KEY',
    )
    settings_pairs = ['{}={}'.format(k, os.getenv(k)) for k in SETTINGS_KEYS]
    return settings_command + settings_pairs


@click.command()
@click.option("--check-env", default=False, help="List environment variables.")
@click.option("--deploying", default=False, help="Deploying to Azure.")
def main(check_env, deploying):
    """CLI for working with data and deployment"""
    if os.getenv("DJANGO_SETTINGS_MODULE") == 'market.azure':
        security_check = input(
            'You are currently accessing the Azure environment. Is this what you want to do? [y/n]: ')
        if security_check == 'n':
            print("Exiting")
            exit()

    # if check_env:
        # subprocess.call("grep -v '^#' .env | xargs")

    migrate = input("Migrate the database? [y/n]: ")
    if migrate == 'y':
        process_migrate = subprocess.check_call(
            ['python', 'manage.py', 'migrate'])

    prepopulate = input("Prepopulate the database? [y/n]: ")
    # TODO: this should be done by default in the migration step
    if prepopulate == 'y':
        process_makesuper = subprocess.check_call(
            ['python', 'manage.py', 'prepopulate'])

    makesuper = input("Create the admin user? [y/n]: ")
    if makesuper == 'y':
        process_makesuper = subprocess.check_call(
            ['python', 'manage.py', 'makesuper'])

    if deploying:
        REQUIRED_ENV_VARS = (
            'AZ_GROUP',
            'AZ_LOCATION',
            'POSTGRES_SERVER_NAME',
            'POSTGRES_ADMIN_USER',
            'POSTGRES_ADMIN_PASSWORD',
            'APP_DB_NAME',
        )

        missing = []
        for v in REQUIRED_ENV_VARS:
            if v not in os.environ:
                missing.append(v)
        if missing:
            print("Required Environment Variables Unset:")
            print("\t" + "\n\t".join(missing))
            print("Exiting.")
            exit()

        create_server = input('Create PostgreSQL server? [y/n]: ')
        if create_server == 'y':
            print("Creating PostgreSQL server...")
            subprocess.check_call(create_server_command)

        create_rule = input('Create firewall rules? [y/n]: ')
        local_ip_firewall_command = get_local_ip_firewall_command()
        if create_rule == 'y':
            print("Allowing access from Azure...")
            subprocess.check_call(azure_firewall_command)
            print("Allowing access from local IP...")
            subprocess.check_call(local_ip_firewall_command)

        create_app_db = input('Create App DB? [y/n]: ')
        if create_app_db == 'y':
            print("Creating App DB...")
            subprocess.check_call(create_db_command)

        print("Getting access details...")
        subprocess.check_call(connect_details_command)

        # Connect to Azure using connection string format (to force SSL)
        # psql "host=$POSTGRES_HOST sslmode=require port=5432 user=$POSTGRES_ADMIN_USER@$POSTGRES_SERVER_NAME dbname=postgres" -W

    update_azure_env = input("Update the azure environment? [y/n]: ")
    if update_azure_env == 'y':
        print("Updating App Settings... ")
        sys.stdout.flush()
        command = get_settings_command()
        process_update_env = subprocess.check_call(command)
        print("Finished updating app settings")

    print("Exiting...")
    sys.exit()


if __name__ == '__main__':
    main()
