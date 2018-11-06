import logging

import boto3
import requests
from requests.exceptions import RequestException

# QUESTION: 

# TODO: Calculate automatically
# Amazone AWS backtest calculation time 
BACKTEST_CALC_TIME = 15

logger = logging.getLogger(__name__)


def get_backtests_count():
    """Request a backtest count."""
    try:
        response = requests.get('https://pastebin.com/raw/bKdgMA3N').json()
    except RequestException as e:
        logger.debug(f"Request for number of backtests failed!")
        # QUESTION: При ошибке запроса убиваем машины, ждем следующего 
        # запуска скрипта или еще что-то?
        return 
    else: 
        return response['count']


def main():
    pass


if __name__ == '__main__':
    main()
