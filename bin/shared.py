#!/usr/bin/env python3
import os
import subprocess
import sys

# # pass in shell=True if on windows (Note security hazard)
# with open('cli-log.txt', 'w') as f:
#     process = subprocess.run(['ls', '-la'], stdout=f, text=True)

# process2 = subprocess.run(
#     ['ls', '-la'], capture_output=True, text=True, check=True)

# process3 = subprocess.run(['ls', 'la', 'dne'], stderr=subprocess.DEVNULL)

# process4 = subprocess.run(['grep', '-n', 'cli-log'],
#                           capture_output=True, text=True, input=process3.stdout)

# print(process.args)  # arguments
# print(process.returncode)  # 0 means successful
# print(process.stdout)
# print(process.stdout.decode()) # if we don't pass text as an argument


REQUIRED_ENV_VARS = (
    'AZ_GROUP',
    'AZ_LOCATION',
    'APP_SERVICE_APP_NAME',
    'POSTGRES_SERVER_NAME',
    'POSTGRES_ADMIN_USER',
    'POSTGRES_ADMIN_PASSWORD',
    'APP_DB_NAME',
)


def verify_environment():
    missing = []
    for v in REQUIRED_ENV_VARS:
        if v not in os.environ:
            missing.append(v)
    if missing:
        print("Required Environment Variables Unset:")
        print("\t" + "\n\t".join(missing))
        print("Exiting.")
        exit()


if __name__ == '__main__':
    verify_environment()
