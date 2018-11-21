from math import ceil

import requests
from requests.exceptions import RequestException

from .instance import EC2InstanceManager
from logger import log, get_logger

logger = get_logger(__name__)


class EC2ScalingManager(EC2InstanceManager):
    def __init__(self, calc_time, done_time, vcpu_count, image_id, 
                 instance_type, instance_tag, max_instances):
        self.calc_time = calc_time
        self.done_time = done_time
        self.vcpu_count = vcpu_count
        logger.debug(
            f"EC2ScalingManager created with {{vcpu_count={vcpu_count}, "
            f"done_time={done_time}, calc_time={calc_time}}}")
        super().__init__(image_id, instance_type, instance_tag, max_instances)

    @log(result=False, params=False)
    def run(self):
        queue_len = self.get_queue_len()
        needed = self.calc_needed_instances(queue_len)
        logger.info(f"{needed} instances required")

        self.scale_to(needed)

    @log(params=False)
    def get_queue_len(self):
        result = self.request_queue_len().json()
        return result['count']

    @staticmethod
    def request_queue_len():
        """Request a qty. of backtests."""
        try:
            return requests.get('https://pastebin.com/raw/bKdgMA3N')
        except RequestException:
            raise

    @log()
    def calc_needed_instances(self, queue_len):
        """Count no. of instances needed to complete a queue in done time."""
        needed = queue_len * self.calc_time / self.done_time / self.vcpu_count
        return ceil(needed)

    @log(result=False)
    def scale_to(self, n):
        """Scale number of instances to n."""
        if n:
            diff = self.calc_diff(needed=n)
            if diff:
                self.create_instances(count=diff)
            else:
                logger.info(f"Instances is enough")
        else:
            self.terminate_instances()

    @log()
    def calc_diff(self, needed):
        """Counts number of instances to add."""
        exist = self.count_instances()
        return needed - exist
