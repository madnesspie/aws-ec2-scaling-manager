from math import ceil

import requests
from requests.exceptions import RequestException

from .instance import EC2InstanceManager
from logger import log, get_logger

logger = get_logger(__name__)


class EC2ScalingManager(EC2InstanceManager):
    def __init__(self, calc_time, done_time, vcpu_count,
                 image_id, instance_type, instance_tag):
        self.calc_time = calc_time
        self.done_time = done_time
        self.vcpu_count = vcpu_count
        logger.debug(
            f"EC2ScalingManager created with {{vcpu_count={vcpu_count}, "
            f"done_time={done_time}, calc_time={calc_time}}}")
        super().__init__(image_id, instance_type, instance_tag)

    def run(self):
        queue_len = self.get_queue_len()
        needed = self.calc_needed_instances(queue_len)
        self.scale_to(needed)

    @log(params=False)
    def get_queue_len(self):
        result = self.request_queue_len().json()
        return result['count']

    @staticmethod
    def request_queue_len():
        """Request a number of backtest."""
        try:
            return requests.get('https://pastebin.com/raw/bKdgMA3N')
        except RequestException:
            logger.warning(f"Request for number of backtests failed!")
            raise

    @log()
    def calc_needed_instances(self, queue_len):
        """Count no. of instances needed to complete a queue in done time."""
        needed = queue_len * self.calc_time / self.done_time / self.vcpu_count
        return ceil(needed)

    def scale_to(self, count):
        if count:
            self.check(needed=count)
        else:
            self.terminate_instances()

    def check(self, needed):
        """Checks if instances are needed."""
        exist = len(list(self.ec2.instances.all()))
        if needed > exist:
            difference = needed - exist
            self.create_instances(count=difference)
        else:
            # Если инстанстов больше/достаточно то мы ничего не делаем
            logger.debug(f"Instances is enough")
