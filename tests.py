import unittest

from startup import ec2, create_instances


# [Тестируемый метод]_[Сценарий]_[Ожидаемое поведение]

class TestEC2CreateInstances(unittest.TestCase):

    def tearDown(self):
        ec2.instances.filter(InstanceIds=self.instance_ids).terminate()

    def test_instances_list_returned(self):
        instanses = create_instances(count=1)
        self.instance_ids = [i.id for i in instanses]
        self.assertTrue(all([i for i in instanses]))




class TestCalc(unittest.TestCase):
    pass


class TestGetQueueLen(unittest.TestCase):
    pass

