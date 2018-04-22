#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from datetime import datetime
import stat
import boto3
from fabric.colors import green
from fabric.api import task, env
from botocore.exceptions import ClientError
from .configure import loadconfig, setconfig, ConfigTask


@task(task_class=ConfigTask)
def createrds(
    instance_name,
    port=5432,
    block_gb_size=100,
    instance_type='db.t2.large',
    engine='postgres',
):
    """
    Spin up a new database backend with Amazon RDS.
    """
    # Connect to boto
    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION_NAME
    )
    client = session.client('rds')

    print("- Reserving a database")
    db = client.create_db_instance(
        DBName=env.DB_NAME,
        DBInstanceIdentifier=instance_name,
        AllocatedStorage=int(block_gb_size),
        DBInstanceClass=instance_type,
        Engine=engine,
        MasterUsername=env.DB_USER,
        MasterUserPassword=env.DB_PASSWORD,
        BackupRetentionPeriod=14,
        PreferredBackupWindow='22:30-23:00',
        Port=int(port),
        MultiAZ=False,
        # EngineVersion='9.4.5',
        PubliclyAccessible=True,
        StorageType='gp2',
        StorageEncrypted=False,
        # DBParameterGroupName='fewer-checkpoints',
    )

    # Check up on its status every so often
    print('- Waiting for instance {0} to start'.format(instance_name))
    waiter = client.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=instance_name)

    # Once it's there pass back the address of the instance
    db = client.describe_db_instances(DBInstanceIdentifier=instance_name)
    host = db['DBInstances'][0]['Endpoint']['Address']

    # Add the new server's host to the configuration file
    setconfig('DB_HOST', host)
    print(green("Success!"))


@task(task_class=ConfigTask)
def createec2(
    instance_name="calaccess_website",
    block_gb_size=50,
    instance_type='m3.medium',
    ami='ami-ca89eeb2'
):
    """
    Spin up a new Ubuntu 14.04 server on Amazon EC2.
    Returns the id and public address.
    """
    # Connect to boto
    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION_NAME
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
    print('- Waiting for instance to start')
    new_instance.wait_until_running()

    # Add the new server's host to the configuration file
    env.EC2_HOST = new_instance.public_dns_name
    setconfig('EC2_HOST', env.EC2_HOST)

    # Print out where it was created
    print("- Provisioned at: {0}".format(env.EC2_HOST))


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
        region_name=env.AWS_REGION_NAME
    )
    client = session.client('ec2')

    # Create the key
    try:
        key_pair = client.create_key_pair(KeyName=name)
    except ClientError as e:
        if 'InvalidKeyPair.Duplicate' in e.message:
            print("A key with named {0} already exists".format(name))
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


@task
def copydb(src_db_instance_id, dest_db_instance_id, make_snapshot=False):
    """
    Copy the most recent snapshot on the source AWS RDS instance to the
    destination RDS instance.
    """
    # Connect to boto
    loadconfig()
    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION_NAME
    )
    client = session.client('rds')

    if make_snapshot:
        client.create_db_snapshot(
            DBSnapshotIdentifier='{0}-{1}'.format(
                src_db_instance_id,
                datetime.now().strftime('%Y-%m-%d-%H-%M'),
            ),
            DBInstanceIdentifier=src_db_instance_id,
        )
        print('- Creating snapshot of {0}'.format(src_db_instance_id))
        # wait until snapshot completes
        waiter = client.get_waiter('db_snapshot_completed')
        waiter.wait(DBInstanceIdentifier=src_db_instance_id)

    # get all the snapshots
    snapshots = client.describe_db_snapshots(
        DBInstanceIdentifier=src_db_instance_id
    )['DBSnapshots']

    # get the most recent completed snapshot
    last_snapshot = sorted(
        [s for s in snapshots if s['PercentProgress'] == 100],
        key=lambda k: k['SnapshotCreateTime'],
        reverse=True,
    )[0]

    # delete the current rds instance with the destination id (if it exists)
    try:
        client.delete_db_instance(
            DBInstanceIdentifier=dest_db_instance_id,
            SkipFinalSnapshot=True,
        )
    except ClientError as e:
        if 'DBInstanceNotFound' in e.message:
            pass
        # if some other ClientError, just raise it
        else:
            raise
    else:
        print('- Deleting current {0} instance'.format(dest_db_instance_id))
        # wait until existing destination instance is deleted
        waiter = client.get_waiter('db_instance_deleted')
        waiter.wait(DBInstanceIdentifier=dest_db_instance_id)

    # restore destination instance from last snapshot of source
    client.restore_db_instance_from_db_snapshot(
        DBInstanceIdentifier=dest_db_instance_id,
        DBSnapshotIdentifier=last_snapshot['DBSnapshotIdentifier']
    )

    print('- Restoring {0} from last snapshot of {1}'.format(
            dest_db_instance_id,
            src_db_instance_id,
        ))
    # wait until restored destination instance becomes available
    waiter = client.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=dest_db_instance_id)

    print(green("Success!"))


@task
def copys3(src_bucket, dest_bucket):
    """
    Copy objects in the source AWS S3 bucket to the destination S3 bucket.

    Ignores source bucket objects with the same name as objects already in the
    destination bucket.
    """
    loadconfig()

    session = boto3.Session(
        aws_access_key_id=env.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=env.AWS_SECRET_ACCESS_KEY,
        region_name=env.AWS_REGION_NAME
    )
    client = session.client('s3')
    s3 = boto3.resource('s3')
    src = s3.Bucket(src_bucket)
    dest = s3.Bucket(dest_bucket)

    src_objects = [
        obj.key for obj
        in src.objects.all()
    ]

    dest_objects = [
        obj.key for obj
        in dest.objects.all()
    ]

    objs_to_copy = [obj for obj in src_objects if obj not in dest_objects]

    for obj in objs_to_copy:
        print('- Copying {0} from {1} to {2}'.format(
                obj,
                src_bucket,
                dest_bucket,
            )
        )
        copy_source = {
            'Bucket': src_bucket,
            'Key': obj
        }
        client.copy(
            copy_source,
            dest_bucket,
            obj,
        )

    print(green("Success!"))
