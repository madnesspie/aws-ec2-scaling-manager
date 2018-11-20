from functools import wraps

import boto3
from botocore.exceptions import ClientError

from logger import log, get_logger

logger = get_logger(__name__)


def dry_run(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        """Do a dryrun to verify permissions."""
        try:
            return func(dry_run=True, *args, **kwargs)
        except ClientError as e:
            if 'DryRunOperation' in str(e):
                return func(*args, **kwargs)
            else:
                # Нужно ли что-нибудь делать, если изменились настройки доступа?
                logger.error(f"You don't have permission to {func.__name__}")
                raise

    return wrapped


class EC2InstanceManager:
    
    TAG_NAME = 'Use'

    def __init__(self, image_id, instance_type, instance_tag, max_instances):
        self.ec2 = boto3.resource('ec2')
        self.max_instances = self.get_max_instances(max_instances)
        self.image_id = image_id
        self.instance_type = instance_type
        
        self.tag = {'Key': self.TAG_NAME, 'Value': instance_tag}
        self.tag_filter = {'Name': f'tag:{self.TAG_NAME}',
                           'Values': [instance_tag]}
        
        logger.debug(
            f"EC2InstanceManager created with {{image_id='{image_id}', "
            f"instance_type='{instance_type}', instance_tag='{instance_tag}', "
            f"max_instances={self.max_instances}}}")

    @log()
    def get_max_instances(self, n):
        """Return maximum number of instances for the manager.
        
        If it is not specified by the user or is greater than the maximum
        available for the account, then maximum number of instances for 
        account is used.
        """
        account_max_instances = self.get_account_max_instances()
        if n and n < account_max_instances:
            return n
        else:
            return account_max_instances

    @log(params=False)
    def get_account_max_instances(self):
        """Request maximum number of instances per account."""
        response = self.ec2.meta.client.describe_account_attributes(
            AttributeNames=['max-instances'])
        attribute = response['AccountAttributes'][-1]
        value = attribute['AttributeValues'][-1]
        max_instances = int(value['AttributeValue'])
        return max_instances

    @property
    def instances(self):
        """Return instances created by manager."""
        return self.ec2.instances.filter(Filters=[self.tag_filter])

    @log(params=False)
    def count_instances(self):
        """Return number of instances created by the manager."""
        return len(list(self.instances))

    @log(params=False)
    @dry_run
    def terminate_instances(self, dry_run=False):
        """Terminate instances created by manager."""
        # https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/TroubleshootingInstancesShuttingDown.html
        # TODO: обработать ошибки остановки
        terminated_instances = self.instances.terminate(DryRun=dry_run)
        logger.info(f"Terminated {len(terminated_instances)} instances")
        return terminated_instances

    @log()
    @dry_run
    def create_instances(self, count, dry_run=False):
        """Create the required count of instances.""" 
        # TODO: Ловить ClientError (InstanceLimitExceeded)
        instances = self.ec2.create_instances(
            ImageId=self.image_id, InstanceType=self.instance_type,
            MinCount=count, MaxCount=count, DryRun=dry_run, 
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [self.tag]
                }]
        )
        logger.info(f"Created {count} instances")
        return instances
