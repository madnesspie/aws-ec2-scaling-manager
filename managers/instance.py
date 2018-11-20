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
                logger.error(f"You don't have permission to {func.__name__}")
                raise
    return wrapped


class EC2InstanceManager:
    
    TAG_NAME = 'Use'

    def __init__(self, image_id, instance_type, instance_tag):
        self.image_id = image_id
        self.instance_type = instance_type
        self.tag = {'Key': self.TAG_NAME, 'Value': instance_tag}
        self.tag_filter = {'Name': f'tag:{self.TAG_NAME}',
                           'Values': [instance_tag]}
        self.ec2 = boto3.resource('ec2')
        logger.debug(
            f"EC2InstanceManager created with {{image_id='{image_id}', "
            f"instance_type='{instance_type}', instance_tag='{instance_tag}'}}")

    @property
    def instances(self):
        return self.ec2.instances.filter(Filters=[self.tag_filter])

    @log()
    def count_instances(self):
        return len(list(self.instances))

    @log()
    @dry_run
    def terminate_instances(self, dry_run=False):
        """Terminate all instances."""
        # Плата за остановленный экземпляр не взимается
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.stop
        # Плата взымается только за тома Elastic Block Storage
        # https://aws.amazon.com/ru/ec2/faqs/
        # TODO: Останавливать, если это нужно

        # https://docs.aws.amazon.com/en_us/AWSEC2/latest/UserGuide/TroubleshootingInstancesShuttingDown.html
        # TODO: обработать ошибки остановки

        # Судя по логам через ресурс убивается так-же одним запросом:
        # Calling ec2:terminate_instances with {'InstanceIds': ['i-0468292426afb2f2c', 'i-053584efb6c1ad5f0', 'i-066a03a0b02275a1a'], 'DryRun': False}
        return self.instances.terminate(DryRun=dry_run)

    @log()
    @dry_run
    def create_instances(self, count, dry_run=False):
        """Creates the required count of instances."""
        # TODO: Инстансы спотогого типа, посмотреть/применить
        # TODO: лимитировать квотой аккаунта

        # https://aws.amazon.com/ru/ec2/faqs/#general
        # 'Вопрос. Сколько инстансов можно запускать в Amazon EC2?'
        # В этом вопросе указана квота аккаунта в 20 инстансов.
        # Нужно масштабироваться вертикально?
        # TODO: Попробовать создать 30 инстансов
        # https://aws.amazon.com/ru/ec2/autoscaling/faqs/
        # А здесь есть фраза "Тысяч инстансов" О_о

        # Инстанс может выйти из строя, группы и автоскелинг в помощь

        # https://aws.amazon.com/contact-us/ec2-request/
        # Здесь можно запросить + к кол-ву инстансов для акк. ec2

        # https://aws.amazon.com/ru/ec2/faqs/#compute-optimized
        # Для вертикального могут подойти оптимизированные для вычислений
        # Микроинстансы тоже могут подойти

        instances = self.ec2.create_instances(
            ImageId=self.image_id, InstanceType=self.instance_type,
            MinCount=count, MaxCount=count, DryRun=dry_run, 
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [self.tag]
                }]
        )
        return instances
