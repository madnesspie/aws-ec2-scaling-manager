from time import sleep
from traceback import format_exc

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


# Если нужно:
# TODO: Автоматический высчитывать экономику инстансов
# TODO: Получать no. vCPU из типа инстанса (хз можно ли)
# TODO: Документация

# Обязательно:
# TODO: Добавить остановку инстансов
# TODO: Инстансы спотогого типа, посмотреть/применить
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
            manager.run()
        except BaseException:
            logger.error(f"{format_exc()}")
            # TODO: Падение с ошибкой если нет прав доступа
            # break
        finally:
            logger.debug(f"Pause {PAUSE} sec.")
            sleep(PAUSE)
    else:
        manager.terminate_instances()
        logger.info(f"He lived without fear and died without fear!")


if __name__ == '__main__':
    start()
