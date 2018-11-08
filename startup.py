import signal
from time import sleep
from math import ceil
from traceback import format_exc
from functools import wraps

import boto3
import requests
from requests.exceptions import RequestException
from botocore.exceptions import ClientError

from config import CALC_TIME, DONE_TIME, VCPU_COUNT, PAUSE
from logger import log, get_logger

ec2 = boto3.resource('ec2')
logger = get_logger(__name__)


class GracefulKiller:
    def __init__(self):
        self.pardoned = True
        signal.signal(signal.SIGTERM, self.exit_gracefully)

    def exit_gracefully(self, signum, frame):
        self.pardoned = False


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


@log(params=False)
def get_queue_len():
    """Request a number of backtest."""
    try:
        response = requests.get('https://pastebin.com/raw/bKdgMA3N').json()
    except RequestException:
        logger.warning(f"Request for number of backtests failed!")
        raise 
    else: 
        return response['count']


@log()
def calc_needed_instances(queue_len, 
                          calc_time=CALC_TIME, 
                          done_time=DONE_TIME,
                          vCPU_count=VCPU_COUNT):
    """Count number of instances needed to complete a queue in 5 minutes."""
    return ceil(queue_len * calc_time / done_time / vCPU_count)


@log()
@dry_run
def create_instances(count, dry_run=False):
    """Creates the required count of instances."""
    instances = ec2.create_instances(
        ImageId='ami-14fb1073', InstanceType='t2.micro',
        MinCount=count, MaxCount=count, DryRun=dry_run)
    return instances


@log(result=False)
def check_instances(queue_len):
    """Checks if instances are needed."""
    needed = calc_needed_instances(queue_len)
    current = len(ec2.instances.all())
    if needed > current:
        difference = needed - current
        create_instances(count=difference)
    else:
        # Если инстанстов больше/достаточно то мы ничего не делаем
        pass


@log(params=False)
@dry_run
def terminate_instances():
    """Terminate all instances"""
    # Можно не убивать, а останавливать машины, позже включать. 
    # Пока не смотрел будет ли профит с этого.
    return ec2.instances.all().terminate()


@log(result=False, params=False)
def run():
    queue_len = get_queue_len()
    if queue_len == 0:
        terminate_instances()
    else:
        check_instances(queue_len)


@log(result=False, params=False)
def start():
    killer = GracefulKiller()
    # import os
    # print(os.getpid())
    while killer.pardoned:
        try:
            # run()
            pass
        except BaseException:
            logger.error(f"{format_exc}")
        finally:
            sleep(PAUSE)

    logger.critical(f"He lived without fear and died without fear!")


if __name__ == '__main__':
    # start()
    print(111111)
    insts = create_instances(2)
    terminate_instances()


