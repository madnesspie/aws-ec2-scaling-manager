import os
import signal
import unittest
from unittest.mock import patch, Mock, PropertyMock
from time import sleep

import boto3
from moto import mock_ec2
# from moto.ec2 import ec2_backend
from requests.exceptions import RequestException

from managers.instance import EC2InstanceManager
from managers.scaling import EC2ScalingManager
from settings import (
    PAUSE, CALC_TIME, DONE_TIME, VCPU_COUNT, IMAGE_ID, INSTANCE_TYPE,
    INSTANCE_TAG, MAX_INSTANCES, REGION_NAME, SPOT_MARKET)

# TODO: Создание инстансов при > очереди
# TODO: Удаление инстансов при 0 очереди
# TODO: 2 инстанса программы 


def create_scaling_manager(max_instances=MAX_INSTANCES):
    manager = EC2ScalingManager(
        calc_time=CALC_TIME, done_time=DONE_TIME, vcpu_count=VCPU_COUNT,
        image_id=IMAGE_ID, instance_type=INSTANCE_TYPE,
        instance_tag=INSTANCE_TAG, max_instances=max_instances,
        region_name=REGION_NAME, spot_market=SPOT_MARKET)
    return manager


def create_instance_manager(instance_tag=INSTANCE_TAG):
    manager = EC2InstanceManager(
        image_id=IMAGE_ID, instance_type=INSTANCE_TYPE,
        instance_tag=instance_tag, region_name=REGION_NAME,
        spot_market=SPOT_MARKET)
    return manager


class TestRequestQueueLen(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manager = create_scaling_manager()

    @patch('managers.scaling.requests.get')
    def test_request_queue_len(self, mock_get):
        mock_get.return_value.json.return_value = {"count": 123}
        mock_get.return_value.status_code = 200
        response = self.manager.request_queue_len()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 123)

    @patch('managers.scaling.EC2ScalingManager.request_queue_len', 
           side_effect=RequestException)
    def test_request_exception(self, mock_request_queue_len):
        with self.assertRaises(RequestException):
            self.manager.run()


@mock_ec2
class TestEC2CreateInstancesLimits(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.max_instances = 3
        cls.manager = create_scaling_manager(max_instances=cls.max_instances)

    @patch('managers.scaling.requests.get')
    def test_create_instances_limit(self, mock_get):
        # Приходится мокать get(), т.к. с @mock_ec2 метод падает с ошибкой
        mock_get.return_value.json.return_value = {"count": 9999999}
        self.manager.run()
        self.assertEqual(self.manager.count_instances, self.max_instances)

    @patch('managers.scaling.EC2ScalingManager.quota', 
           new_callable=PropertyMock)
    @patch('managers.scaling.requests.get')
    def test_create_instances_quota(self, mock_get, mock_quota):
        mock_get.return_value.json.return_value = {"count": 9999999}
        mock_quota.return_value = 0
        self.manager.run()
        self.assertFalse(self.manager.count_instances)

    def tearDown(self):
        self.manager.terminate_instances()


@mock_ec2
class TestTwoEC2InstanceManagers(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.first_count = 2
        cls.second_count = 3
        cls.first_manager = create_instance_manager(instance_tag='test1')
        cls.second_manager = create_instance_manager(instance_tag='test2')
        
    def setUp(self):
        self.first_manager.create_instances(self.first_count)
        self.second_manager.create_instances(self.second_count)

    def test_creation(self):
        self.assertEqual(self.first_manager.count_instances, self.first_count)
        self.assertEqual(self.second_manager.count_instances, self.second_count)

    def test_terminate_instances_of_first(self):
        self.first_manager.terminate_instances()
        self.assertFalse(self.first_manager.count_instances)
        self.assertEqual(self.second_manager.count_instances, self.second_count)

    def test_terminate_instances_of_second(self):
        self.second_manager.terminate_instances()
        self.assertFalse(self.second_manager.count_instances)
        self.assertEqual(self.first_manager.count_instances, self.first_count)

    def tearDown(self):
        self.first_manager.terminate_instances()
        self.second_manager.terminate_instances()


if __name__ == "__main__":
    unittest.main()




# class TestRun(unittest.TestCase):
#     pass
    

# class TestGracefulKiller(unittest.TestCase):
#     @patch('startup.GracefulKiller')
#     def test_handle_signal(self, MockGracefulKiller):
#         killer = MockGracefulKiller()


# class TestEC2CreateInstances(unittest.TestCase):

#     def tearDown(self):
#         ec2.instances.filter(InstanceIds=self.instance_ids).terminate()

#     def test_instances_list_returned(self):
#         instanses = create_instances(count=1)
#         self.instance_ids = [i.id for i in instanses]
#         self.assertTrue(all([i for i in instanses]))



# class TestCalc(unittest.TestCase):
#     pass
