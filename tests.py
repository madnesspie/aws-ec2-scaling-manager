import os
import signal
import unittest
from unittest.mock import patch
from time import sleep

import moto

from config import CALC_TIME, DONE_TIME, VCPU_COUNT
from startup import (
    create_instances, run, GracefulKiller, calc_needed_instances,
    request_queue_len, get_queue_len)


class TestGetQueueLen(unittest.TestCase):
    # @patch('startup.get_queue_len', return_value=100)
    def test_get_queue_len(self):
        queue_len = get_queue_len()
        self.assertIsNotNone(queue_len)
        self.assertIsInstance(queue_len, int)

    def test_request_queue_len(self):
        response = request_queue_len()
        self.assertEqual(response.status_code, 200)


class TestCalcNeededInstances(unittest.TestCase):
    def test_complete_in_done_time(self):
        queue_len = 1000
        instances = calc_needed_instances(queue_len)
        need_time = queue_len * CALC_TIME / (instances * VCPU_COUNT)
        self.assertGreaterEqual(DONE_TIME, need_time)


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

