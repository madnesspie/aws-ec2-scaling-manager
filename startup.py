from time import sleep
from traceback import format_exc

from managers.scaling import EC2ScalingManager
from gracefulkiller import GracefulKiller
from logger import log, get_logger

logger = get_logger(__name__)

# TODO: Инстансы спотогого типа, посмотреть/применить
# TODO: Автоматический высчитывать экономику инстансов
# TODO: Добавить документацию

PAUSE = 45

@log(result=False, params=False)
def start():
    killer = GracefulKiller()
    manager = EC2ScalingManager(
        calc_time=15, done_time=300, vcpu_count=2, 
        image_id='ami-14fb1073', instance_type='t2.micro')
    # TODO: переменные окр.
    
    while killer.pardoned:
        try:
            manager.run()
        except BaseException:
            logger.error(f"{format_exc()}")
        finally:
            sleep(PAUSE)

    logger.critical(f"He lived without fear and died without fear!")


if __name__ == '__main__':
    start()


