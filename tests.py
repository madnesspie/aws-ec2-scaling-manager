import os
import signal
import unittest
from unittest.mock import patch
from time import sleep

import boto3
from moto import mock_ec2

from config import CALC_TIME, DONE_TIME, VCPU_COUNT
from startup import (
    create_instances, terminate_instances, run, GracefulKiller, 
    calc_needed_instances, request_queue_len, get_queue_len)


class TestGetQueueLen(unittest.TestCase):

    @patch('startup.requests.get')
    def test_request_queue_len(self, mock_get):
        mock_get.return_value.json.return_value = {"count": 123}
        mock_get.return_value.status_code = 200
        response = request_queue_len()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 123)


class TestCalcNeededInstances(unittest.TestCase):
    def test_complete_in_done_time(self):
        queue_len = 1000
        instances = calc_needed_instances(queue_len)
        need_time = queue_len * CALC_TIME / (instances * VCPU_COUNT)
        self.assertGreaterEqual(DONE_TIME, need_time)


@mock_ec2
class TestEC2CreateInstances(unittest.TestCase):
    def test_create_instances(self):
        # TODO: Fix PendingDeprecationWarning
        instances = create_instances(2)
        is_instances = [i.image_id == 'ami-14fb1073' for i in instances]
        self.assertTrue(all(is_instances))


if __name__ == "__main__":
    unittest.main()

# class TestEC2TerminateInstances(unittest.TestCase):
#     def test_terminate_instances(self):
#         ec2 = boto3.resource('ec2')
#         instance = create_instances(1)[0]
#         print(ec2.create_instances.call_count)
        # terminate_instances()
        # self.assertFalse(instance.state['Name'] == 'terminated')





# class TestRun(unittest.TestCase):
#     pass
    

# class MockGracefulKiller(GracefulKiller):
#     def __init__(self):
#         signal.signal(signal.SIGALRM, self.exit_gracefully)
#         super()


# class TestGracefulKiller(unittest.TestCase):
#     @patch('startup.GracefulKiller', side_effect=MockGracefulKiller)
#     def test_handle_signal(self, MockGracefulKiller):
#         killer = MockGracefulKiller()
#         signal.alarm(1)
#         sleep(1.1)
#         self.assertTrue(killer.kill_now)
#         self.assertTrue(killer.exit_gracefully.assert_called_once())


# class TestEC2CreateInstances(unittest.TestCase):

#     def tearDown(self):
#         ec2.instances.filter(InstanceIds=self.instance_ids).terminate()

#     def test_instances_list_returned(self):
#         instanses = create_instances(count=1)
#         self.instance_ids = [i.id for i in instanses]
#         self.assertTrue(all([i for i in instanses]))



# class TestCalc(unittest.TestCase):
#     pass
