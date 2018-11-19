from functools import wraps

import boto3
from botocore.exceptions import ClientError

from logger import log, get_logger

logger = get_logger(__name__)


def dry_run(func):
    @wraps(func)
    def wrapped(*args, **kwargs):
        """Do a dryrun first to verify permissions."""
        try:
            return func(dry_run=True, *args, **kwargs)
        except ClientError as e:
            if 'DryRunOperation' in str(e):
                return func(*args, **kwargs)
            else:
                # If not permissions
                raise
    return wrapped


class EC2InstanceManager:
    def __init__(self, image_id, instance_type):
        self.image_id = image_id
        self.instance_type = instance_type
        self.ec2 = boto3.resource('ec2')

    @property
    def instances(self):
        return list(self.ec2.instances.all())

    def scale_to(self, count):
        if count:
            self.check(needed=count)
        else:
            self.terminate_instances()

    def check(self, needed):
        """Checks if instances are needed."""
        exist = len(self.instances)
        if needed > exist:
            difference = needed - exist
            self.create_instances(count=difference)
        else:
            # Если инстанстов больше/достаточно то мы ничего не делаем
            logger.debug(f"Instances is enough")

    @log(params=False)
    @dry_run
    def terminate_instances(self, dry_run=False):
        """Terminate all instances"""
        # TODO: Убивать только свои инстансы
        # TODO: Убивать инстансы одним запросом
        # Плата за остановленный экземпляр не взимается
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.stop
        return self.ec2.instances.all().terminate(DryRun=dry_run)

    @log()
    @dry_run
    def create_instances(self, count, dry_run=False):
        """Creates the required count of instances."""
        instances = self.ec2.create_instances(
            ImageId=self.image_id, InstanceType=self.instance_type,
            MinCount=count, MaxCount=count, DryRun=dry_run)
        return instances
