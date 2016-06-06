#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import stat
import random
import boto3
from botocore.exceptions import ClientError
from fabric.api import task, env
from configure import loadconfig


@task
def createrds(block_gb_size=12):
    """
    Spin up a new database backend with Amazon RDS.
    """
    loadconfig()
    client = boto3.client('rds')

    db_instance_id = "calaccessraw-{0}".format(
        random.choice(range(0, 99))
    )

    # check to see if there db instance already exists
    while True:
        try:
            client.describe_db_instances(
                DBInstanceIdentifier=db_instance_id
            )
        except ClientError as e:
            if 'DBInstanceNotFound' in e.message:
                break
        else:
            # if the db instance already exists, generate a new id
            db_instance_id = "calaccessraw-{0}".format(
                random.choice(range(0, 99))
            )

    print "- Reserving a database"

    # full list of kwargs:
    # http://boto3.readthedocs.io/en/latest/reference/services/rds.html#RDS.Client.create_db_instance # noqa
    db = client.create_db_instance(
        DBName='calaccess_raw',
        DBInstanceIdentifier=db_instance_id,
        AllocatedStorage=block_gb_size,
        DBInstanceClass='db.t1.micro',
        Engine='postgres',
        MasterUsername='cacivicdata',
        MasterUserPassword=env.DB_USER_PASSWORD,
        BackupRetentionPeriod=14,
        PreferredBackupWindow='22:30-23:00',
        Port=5432,
        MultiAZ=False,
        EngineVersion='9.4.5',
        PubliclyAccessible=True,
        StorageType='gp2',
        StorageEncrypted=False,
    )

    # Check up on its status every so often
    print '- Waiting for instance {0} to start'.format(db_instance_id)
    waiter = client.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=db_instance_id)

    db = client.describe_db_instances(
        DBInstanceIdentifier=db_instance_id)

    return db['DBInstances'][0]['Endpoint']['Address']


@task
def createserver(ami='ami-978dd9a7', block_gb_size=100):
    """
    Spin up a new Ubuntu 14.04 server on Amazon EC2.
    Returns the id and public address.
    """
    loadconfig()

    ec2 = boto3.resource('ec2')

    # full list of kwargs:
    # http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#EC2.ServiceResource.create_instances # noqa
    new_instance = ec2.create_instances(
        ImageId='ami-978dd9a7',
        MinCount=1,
        MaxCount=1,
        InstanceType=env.EC2_INSTANCE_TYPE,
        SecurityGroups=[env.AWS_SECURITY_GROUP],
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'VolumeSize': block_gb_size,
                },
            },
        ],
        KeyName=env.key_name,
    )[0]

    new_instance.create_tags(Tags=[{"Key": "Name", "Value": "calaccess"}])

    print '- Waiting for instance to start'
    new_instance.wait_until_running()

    print "- Provisioned at: {0}".format(new_instance.public_dns_name)

    return (new_instance.id, new_instance.public_dns_name)


@task
def createkeypair():
    """
    Creates an EC2 key pair and saves it to a .pem file
    """
    loadconfig()
    client = boto3.client('ec2')

    key_file_dir = os.path.expanduser("~/.ec2/")

    os.path.exists(key_file_dir) or os.makedirs(key_file_dir)

    try:
        key_pair = client.create_key_pair(KeyName=env.key_name)
    except ClientError as e:
        if 'InvalidKeyPair.Duplicate' in e.message:
            print "A key with named {0} already exists".format(env.key_name)
        else:
            raise e
    else:
        print "- Saving to {0}".format(env.key_filename[0])
        with open(env.key_filename[0], 'w') as f:
            f.write(key_pair['KeyMaterial'])

        os.chmod(env.key_filename[0], stat.S_IRUSR)

    