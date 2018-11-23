import os
import signal
import unittest
from unittest.mock import patch, Mock
from time import sleep

import boto3
from moto import mock_ec2
# from moto.ec2 import ec2_backend
from requests.exceptions import RequestException

from managers.instance import EC2InstanceManager
from settings import (
    PAUSE, CALC_TIME, DONE_TIME, VCPU_COUNT, IMAGE_ID,
    INSTANCE_TYPE, INSTANCE_TAG, MAX_INSTANCES)


@mock_ec2
class TestEC2CreateInstances(unittest.TestCase):
    def test_create_instances(self):
        manager = EC2InstanceManager( 
            image_id=IMAGE_ID, instance_type=INSTANCE_TYPE,
            instance_tag=INSTANCE_TAG)
        r = manager.create_instances(1)
        self.assertTrue(r)

# class TestRequestQueueLen(unittest.TestCase):
#     @patch('startup.requests.get')
#     def test_request_queue_len(self, mock_get):
#         mock_get.return_value.json.return_value = {"count": 123}
#         mock_get.return_value.status_code = 200
#         response = request_queue_len()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['count'], 123)

#     @patch('startup.request_queue_len', side_effect=RequestException)
#     def test_request_exception(self, mock_request_queue_len):
#         with self.assertRaises(RequestException):
#             mock_request_queue_len()


# @mock_ec2
# class TestEC2TerminateInstances(unittest.TestCase):
#     def setUp(self):
#         self.ec2 = boto3.resource('ec2')
#         self.ec2.create_instances(
#             ImageId='ami-14fb1073', InstanceType='t2.micro',
#             MinCount=2, MaxCount=2)
    
#     def test_terminate_instances(self):
#         instances = terminate_instances()
#         statuses = [i.state['Name'] == 'terminated'
#                     for i in self.ec2.instances.all()]
#         self.assertTrue(all(statuses))



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
