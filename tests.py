import unittest
from unittest.mock import patch
import moto

from startup import create_instances

# [Тестируемый метод]_[Сценарий]_[Ожидаемое поведение]

# class TestEC2CreateInstances(unittest.TestCase):

#     def tearDown(self):
#         ec2.instances.filter(InstanceIds=self.instance_ids).terminate()

#     def test_instances_list_returned(self):
#         instanses = create_instances(count=1)
#         self.instance_ids = [i.id for i in instanses]
#         self.assertTrue(all([i for i in instanses]))




# class TestCalc(unittest.TestCase):
#     pass


class TestGetQueueLen(unittest.TestCase):
    @patch('startup.get_queue_len', return_value=100)
    def test_get_queue_len(self, get_queue_len):
        queue_len = get_queue_len()
        self.assertIsNotNone(queue_len)
        self.assertIsInstance(queue_len, int)

