from time import sleep

import boto3
import requests
from requests.exceptions import RequestException
from botocore.exceptions import ClientError

from logger import log, get_logger

# TODO: Calculate automatically
# Amazone AWS backtest calculation time 
CALC_TIME = 15
# Estimated time to complete all backtests in the queue
DONE_TIME = 180
# Pause between runs
PAUSE = 60

ec2 = boto3.resource('ec2')
logger = get_logger(__name__)


@log(show_params=False, show_result=True)
def get_queue_len():
    """Request a number of backtest."""
    try:
        response = requests.get('https://pastebin.com/raw/bKdgMA3N').json()
    except RequestException as e:
        logger.warning(f"Request for number of backtests failed!")
        return 
    else: 
        return response['count']


def calc_needed_instances(queue_len, 
                          calc_time=CALC_TIME, 
                          done_time=DONE_TIME):
    """Count number of instances needed to complete a queue in 5 minutes."""
    return queue_len * calc_time / done_time



@log(show_result=True)
def create_instances(count, dry_run=False):
    instances = ec2.create_instances(
        ImageId='ami-14fb1073', InstanceType='t2.micro',
        MinCount=count, MaxCount=count, DryRun=dry_run)
    return instances


def main():
    n_current_instances = 0
    while True: 
        queue_len = get_queue_len()
        if queue_len == 0:
            # TODO: Stop all instances
            pass

        n_needed_instances = calc_needed_instances(queue_len)
        if n_needed_instances > n_current_instances:
            # TODO: Add new instances
            pass
        else:
            # QUESTION: Если инстанстов больше/достаточно то мы 
            # ничего не делаем?
            pass 

        sleep(PAUSE) 


@log(show_result=True)
def deb():  
    # return ec2.meta.client.describe_images(
    #     Owners=['amazon'], Filters=[
    #         {
    #             'Name': 'platform',
    #             'Values': [
    #                 'ubuntu',
    #             ]
    #         },
    #     ],
    # )
    # return ec2.meta.client.describe_instance_status()
    return create_instances(1)


@log(show_result=True, show_params=False)
def terminate_instances():
    return ec2.instances.all().terminate()


if __name__ == '__main__':
    insts = create_instances(1)
    tp = [type(i) is ec2.Instance for i in insts]
    print(tp)
    terminate_instances()
    pass


# def dry_start_instances(func):
#     @wraps(func)
#     def wrapped(*args, **kwargs):
#         try:
#             ec2.start_instances(InstanceIds=[instance_id], DryRun=True)
#         except ClientError as e:
#             if 'DryRunOperation' not in str(e):
#                 raise
#         return func(*args, **kwargs)
#     return wrapped


# @dry_start_instances
# def start_instances():
#     try:
#         response = ec2.start_instances(InstanceIds=[instance_id], DryRun=False)
#         print(response)
#     except ClientError as e:
#         print(e)
