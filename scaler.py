from time import sleep
from traceback import format_exc

from requests.exceptions import RequestException
from botocore.exceptions import ClientError

from managers.scaling import EC2ScalingManager
from gracefulkiller import GracefulKiller
from settings import (
    PAUSE, CALC_TIME, DONE_TIME, VCPU_COUNT, IMAGE_ID, 
    INSTANCE_TYPE, INSTANCE_TAG, MAX_INSTANCES)
from logger import log, get_logger

logger = get_logger(__name__)

# Плата за остановленный экземпляр не взимается
# https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ec2.html#EC2.ServiceResource.stop
# Плата взымается только за тома Elastic Block Storage
# https://aws.amazon.com/ru/ec2/faqs/

# https://aws.amazon.com/ru/ec2/faqs/#compute-optimized
# Для вертикального могут подойти оптимизированные для вычислений
# Микроинстансы тоже могут подойти


# Мб позже:
# TODO: Автоматический высчитывать экономику инстансов
# TODO: Получать no. vCPU из типа инстанса (хз можно ли)
# TODO: Добавить остановку инстансов
# TODO: Документация

# Обязательно:
# TODO: Инстансы спотогого типа применить
# TODO: Тесты


@log(result=False, params=False)
def start():
    killer = GracefulKiller()
    manager = EC2ScalingManager(
        calc_time=CALC_TIME, done_time=DONE_TIME, vcpu_count=VCPU_COUNT, 
        image_id=IMAGE_ID, instance_type=INSTANCE_TYPE, 
        instance_tag=INSTANCE_TAG, max_instances=MAX_INSTANCES)

    while killer.pardoned:
        try:
            # manager.run()
            # manager.terminate_instances()
            # manager.create_instances(6)
            manager.create_spot_instances()
        except RequestException:
            logger.warning(f"Request for number of backtests failed!")
        except ClientError as e:
            logger.critical(f"Critical client error: {e}")
            break
        except BaseException:
            # Что делать если необработанная ошибка? 
            logger.critical(f"Critical unhandled error:\n{format_exc()}")
            break
        finally:
            return
            logger.debug(f"Pause {PAUSE} sec.")
            sleep(PAUSE)
    else:
        manager.terminate_instances()
        logger.info(f"Caught signal SIGTERM. Program correctly stopped")

    logger.critical("The error caused the program to stop!")

if __name__ == '__main__':
    start()
