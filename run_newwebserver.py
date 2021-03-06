import os
import pprint
import subprocess
import time

import boto3
from tqdm import tqdm

# Declaring EC2 variable
ec2 = boto3.resource('ec2')


# Function to tell the user when they can do things
def countdown(n):
    pprint.pprint('This will now go for more seconds...')
    while n >= 0:
        print(n, end='...')
        time.sleep(1)
        n -= 1
    print('Next step \n')


# This for extra stuff because i don't like the look of countdown
def progress(m):
    pbar = tqdm(total=m)
    for i in range(m):
        time.sleep(1)
        pbar.update(1)
    pbar.close()


# Creates a new instance
def create_instance():
    # Ask the user to give the new instance a name
    instancename = input('Please give your new instance a name: ')
    # List files in current directory
    source = os.getcwd()
    print('Files in folder: \n ')
    for fn in os.listdir(source):
        if os.path.isfile(fn):
            print(fn)
    key = input('\nPlease type in the key you would like to use: ')
    tags = [{'Key': 'Name', 'Value': instancename}]
    tag_spec = [{'ResourceType': 'instance', 'Tags': tags}]

    # try/except so the script will not crash
    try:
        instance = ec2.create_instances(
            ImageId='ami-0c21ae4a3bd190229',
            MinCount=1,
            MaxCount=1,
            InstanceType='t2.micro',
            KeyName=key,
            TagSpecifications=tag_spec,
            SecurityGroupIds=['sg-0d2d781ed4f0610db'],  # replace with your security group id
            # UserData that will be executed on creation of the instance
            UserData='''#!/bin/bash
                     yum -y update
                     yum -y install python3
                     amazon-linux-extras install nginx1.12 -y
                     service nginx start
                     chkconfig nginx on
                     touch home/ec2-user/testFile''')

        print("An EC2 instance with ID", instance[0].id, "has been created.\n")

        progress(10)

        instance[0].reload()
        print("Public IP address:", instance[0].public_ip_address)

        # Suppress the new host key confirmation prompt and allow SSH remote command execution
        cmd = "ssh -o StrictHostKeyChecking=no -i devops.pem ec2-user@" + instance[0].public_ip_address + " 'pwd'"
        print(20 * '-', 'ssh set up', 20 * '-')

        # Changed this to 20 one time and it was all broken
        progress(60)
        output = subprocess.run(cmd, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pprint.pprint(output)

        # SCP the check_webserver.py file to the instance
        cmd_scp = "scp -i devops.pem check_webserver.py ec2-user@" + instance[0].public_ip_address + ":."
        output = subprocess.run(cmd_scp, check=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        pprint.pprint(output)
        print(10 * '-', 'please wait 2 minutes before running the next step', 10 * '-')

        progress(15)

        # countdown(15)
        # Wait to let everything get set up
    except Exception as error:
        print(error)


# Define a main() function
def main():
    create_instance()


# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
