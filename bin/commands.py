import os
import urllib.request


# App service settings

# https://docs.microsoft.com/en-us/cli/azure/webapp/config/appsettings?view=azure-cli-latest#az-webapp-config-appsettings-set
settings_command = [
    'az', 'webapp', 'config', 'appsettings', 'set',
    '--name', os.getenv('APP_SERVICE_APP_NAME'),
    '--resource-group', os.getenv('AZ_GROUP'),
    '--settings',
]

# Database server

# Ref: https://docs.microsoft.com/en-gb/cli/azure/postgres/server?view=azure-cli-latest#az-postgres-server-create
# SKUs: https://docs.microsoft.com/en-us/azure/postgresql/concepts-pricing-tiers
#       {pricing tier}_{compute generation}_{vCores}
create_server_command = [
    'az', 'postgres', 'server', 'create',
    '--resource-group', os.getenv('AZ_GROUP'),
    '--location', os.getenv('AZ_LOCATION'),
    '--name', os.getenv('POSTGRES_SERVER_NAME'),
    '--admin-user', os.getenv('POSTGRES_ADMIN_USER'),
    '--admin-password', os.getenv('POSTGRES_ADMIN_PASSWORD'),
    '--sku-name', 'B_Gen5_1',
]

# Firewall

# Ref: https://docs.microsoft.com/en-gb/cli/azure/postgres/server/firewall-rule?view=azure-cli-latest#az-postgres-server-firewall-rule-create
azure_firewall_command = [
    'az', 'postgres', 'server', 'firewall-rule', 'create',
    '--resource-group', os.getenv('AZ_GROUP'),
    '--server-name', os.getenv('POSTGRES_SERVER_NAME'),
    '--start-ip-address', '0.0.0.0',
    '--end-ip-address', '0.0.0.0',
    '--name', 'AllowAllAzureIPs',
]


def get_local_ip_firewall_command():
    with urllib.request.urlopen('http://ip.42.pl/raw') as f:
        my_ip = f.read()
        local_ip_firewall_command = [
            'az', 'postgres', 'server', 'firewall-rule', 'create',
            '--resource-group', os.getenv('AZ_GROUP'),
            '--server-name', os.getenv('POSTGRES_SERVER_NAME'),
            '--start-ip-address', my_ip,
            '--end-ip-address', my_ip,
            '--name', 'AllowMyIP',
        ]
        return local_ip_firewall_command


# Database

create_db_command = [
    'az', 'postgres', 'db', 'create',
    '--resource-group', os.getenv('AZ_GROUP'),
    '--server-name', os.getenv('POSTGRES_SERVER_NAME'),
    '--name', os.getenv('APP_DB_NAME'),
]

connect_details_command = [
    'az', 'postgres', 'server', 'show',
    '--resource-group', os.getenv('AZ_GROUP'),
    '--name', os.getenv('POSTGRES_SERVER_NAME'),
]


# TODO: add a Storage CLI command
