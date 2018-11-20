from time import sleep
from traceback import format_exc

from managers.scaling import EC2ScalingManager
from gracefulkiller import GracefulKiller
from settings import (
    PAUSE, CALC_TIME, DONE_TIME, VCPU_COUNT, IMAGE_ID, 
    INSTANCE_TYPE, INSTANCE_TAG)
from logger import log, get_logger

logger = get_logger(__name__)

# TODO: Автоматический высчитывать экономику инстансов - судя по всему это труднаа
# TODO: Получать no. vCPU из типа инстанса

# TODO: Добавить лимиты для инстанса скейлера 
# TODO: Раскидать логгер прямо


@log(result=False, params=False)
def start():
    killer = GracefulKiller()
    manager = EC2ScalingManager(
        calc_time=CALC_TIME, done_time=DONE_TIME, 
        vcpu_count=VCPU_COUNT, image_id=IMAGE_ID, 
        instance_type=INSTANCE_TYPE, instance_tag=INSTANCE_TAG)

    while killer.pardoned:
        try:
            manager.run()
        except BaseException:
            logger.error(f"{format_exc()}")
        finally:
            logger.debug(f"Pause {PAUSE} sec.")
            sleep(PAUSE)
    else:
        manager.terminate_instances()
        logger.info(f"He lived without fear and died without fear!")
        # При SIGTERM'e убиваем инстансы? 


if __name__ == '__main__':
    # start()
    manager = EC2ScalingManager(
        calc_time=CALC_TIME, done_time=DONE_TIME,
        vcpu_count=VCPU_COUNT, image_id=IMAGE_ID,
        instance_type=INSTANCE_TYPE, instance_tag=INSTANCE_TAG)
    manager.create_instances(1)
    manager.terminate_instances()