#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
import boto3
from fabric.colors import green
from fabric.api import task, env
from botocore.exceptions import ClientError
from configure import loadconfig, setconfig, ConfigTask


@task(task_class=ConfigTask)
def createrds(
    instance_name,
    database_name="calaccess_website",
    database_user="cacivicdata",
    database_port=5432,
    block_gb_size=100,
    instance_type='db.t2.large'
):
    """
    Spin up a new database backend with Amazon RDS.
    """
    # Connect to boto
    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION
    )
    client = session.client('rds')

    print "- Reserving a database"
    db = client.create_db_instance(
        DBName=database_name,
        DBInstanceIdentifier=instance_name,
        AllocatedStorage=int(block_gb_size),
        DBInstanceClass=instance_type,
        Engine='postgres',
        MasterUsername=database_user,
        MasterUserPassword=env.DB_PASSWORD,
        BackupRetentionPeriod=14,
        PreferredBackupWindow='22:30-23:00',
        Port=database_port,
        MultiAZ=False,
        EngineVersion='9.4.5',
        PubliclyAccessible=True,
        StorageType='gp2',
        StorageEncrypted=False,
        DBParameterGroupName='fewer-checkpoints',
    )

    # Check up on its status every so often
    print '- Waiting for instance {0} to start'.format(instance_name)
    waiter = client.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=instance_name)

    # Once it's there pass back the address of the instance
    db = client.describe_db_instances(DBInstanceIdentifier=instance_name)
    host = db['DBInstances'][0]['Endpoint']['Address']

    # Add the new server's host to the configuration file
    setconfig('RDS_HOST', host)
    print(green("Success!"))


@task(task_class=ConfigTask)
def createec2(
    instance_name="calaccess_website",
    block_gb_size=100,
    instance_type='c3.large',
    ami='ami-978dd9a7'
):
    """
    Spin up a new Ubuntu 14.04 server on Amazon EC2.
    Returns the id and public address.
    """
    # Connect to boto
    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION
    )
    ec2 = session.resource('ec2')

    # Create the instance
    new_instance = ec2.create_instances(
        ImageId=ami,
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'VolumeSize': block_gb_size,
                },
            },
        ],
        KeyName=env.KEY_NAME,
    )[0]

    # Name the instance
    new_instance.create_tags(Tags=[{"Key": "Name", "Value": instance_name}])

    # Wait for it start running
    print '- Waiting for instance to start'
    new_instance.wait_until_running()

    # Add the new server's host to the configuration file
    env.EC2_HOST = new_instance.public_dns_name
    setconfig('EC2_HOST', env.EC2_HOST)

    # Print out where it was created
    print "- Provisioned at: {0}".format(env.EC2_HOST)


@task(task_class=ConfigTask)
def createkey(name):
    """
    Creates an EC2 key pair and saves it to a .pem file
    """
    # Make sure the key directory is there
    os.path.exists(env.key_file_dir) or os.makedirs(env.key_file_dir)

    # Connect to boto
    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION
    )
    client = session.client('ec2')

    # Create the key
    try:
        key_pair = client.create_key_pair(KeyName=name)
    except ClientError as e:
        if 'InvalidKeyPair.Duplicate' in e.message:
            print "A key with named {0} already exists".format(name)
            return False
        else:
            raise e

    # Save the key name to the configuration file
    setconfig('KEY_NAME', name)

    # Reboot the env
    loadconfig()

    # Save the key
    with open(env.key_filename[0], 'w') as f:
        f.write(key_pair['KeyMaterial'])
    # Set it to tight permissions
    os.chmod(env.key_filename[0], stat.S_IRUSR)

    print(green("Success!"))
    print("Key created at {}".format(env.key_filename[0]))
