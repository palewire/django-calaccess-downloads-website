import time
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

    db_instance_identifier = "calaccessraw-{0}".format(
        random.choice(range(0, 99))
    )

    # check to see if there db instance already exists
    while True:
        try:
            client.describe_db_instances(
                DBInstanceIdentifier=db_instance_identifier
            )
        except ClientError as e:
            if 'DBInstanceNotFound' in e.message:
                break
        else:
            # if the db instance already exists, generate a new id 
            db_instance_identifier = "calaccessraw-{0}".format(
                random.choice(range(0, 99))
            )

    print "- Reserving a database"
    db = client.create_db_instance(
        DBName='calaccess_raw',
        DBInstanceIdentifier=db_instance_identifier,
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
        # An error occurred (InvalidParameterCombination) when calling the 
        # CreateDBInstance operation: DB Security Groups can only be associated 
        # with VPC DB Instances using API versions 2012-01-15 through 2012-09-17.
        # DBSecurityGroups=[env.AWS_SECURITY_GROUP],
        
        # An error occurred (InvalidParameterValue) when calling the CreateDBInstance
        # operation: Character sets not supported on create for engine: 
        # postgres and version9.4.5
        # CharacterSetName='UTF-8',
        
        # not required?
        # AvailabilityZone=env.AWS_REGION,
        # VpcSecurityGroupIds=[
        #     'string',
        # ],
        # DBSubnetGroupName='string',
        # PreferredMaintenanceWindow='string',
        # DBParameterGroupName='string',
        # AutoMinorVersionUpgrade=True,
        # LicenseModel='string',
        # Iops=123,
        # OptionGroupName='string',
        # Tags=[
        #     {
        #         'Key': 'string',
        #         'Value': 'string'
        #     },
        # ],
        # DBClusterIdentifier='string',
        # TdeCredentialArn='string',
        # TdeCredentialPassword='string',
        # KmsKeyId='string',
        # Domain='string',
        # CopyTagsToSnapshot=True|False,
        # MonitoringInterval=123,
        # MonitoringRoleArn='string',
        # DomainIAMRoleName='string',
        # PromotionTier=123,   
    )

    # Check up on its status every so often
    print '- Waiting for instance {0} to start'.format(db_instance_identifier)
    waiter = client.get_waiter('db_instance_available')
    waiter.wait(DBInstanceIdentifier=db_instance_identifier)

    db = client.describe_db_instances(DBInstanceIdentifier=db_instance_identifier)

    return db['DBInstances'][0]['Endpoint']['Address']


@task
def createserver(
    ami='ami-978dd9a7',
    block_gb_size=100
):
    """
    Spin up a new Ubuntu 14.04 server on Amazon EC2.
    Returns the id and public address.
    """
    loadconfig()

    ec2 = boto3.resource('ec2')

    new_instance = ec2.create_instances(
        ImageId='ami-978dd9a7',
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[
            'default',
        ],
    )[0]

    new_instance.create_tags(Tags=[{"Key": "Name", "Value": "calaccess"}])
    
    print '- Waiting for instance to start'
    waiter = boto3.client('ec2').get_waiter('instance_running')
    waiter.wait(InstanceIds=[new_instance.id])

    print "- Provisioned at: {0}".format(new_instance.public_dns_name)

    return (new_instance.id, new_instance.public_dns_name)
