import subprocess

import boto3

# Declaring EC2 variable
ec2 = boto3.resource('ec2')

try:
    # Retrieving a List of instances
    for instance in ec2.instances.all():
        print(instance.id, instance.state, instance.public_ip_address)

    cmd = "ssh -i <pemfile> ec2-user@" + instance.public_ip_address + " 'python3 check_webserver.py'"

    (status, output) = subprocess.getstatusoutput(cmd)
    print(output)

except Exception as error:
    print(error)