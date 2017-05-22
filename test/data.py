from data import Data, DataType
import unittest
import os
import random


class TestDataClass(unittest.TestCase):
    def setUp(self):
        self.some_tests = [
            {
                DataType.ALGO: 'base_unsat',
                DataType.PROBLEM: 'bag-barman-prob02.pddl',
                DataType.DOMAIN: 'bag-barman',
                DataType.ATTRIBUTE: 'unsolvable',
                'value': 1
            },
            {
                DataType.ALGO: 'base_unsat',
                DataType.PROBLEM: 'bag-barman-prob01.pddl',
                DataType.DOMAIN: 'bag-barman',
                DataType.ATTRIBUTE: 'unsolvable',
                'value': 0
            },
            {
                DataType.ALGO: 'base_unsat',
                DataType.PROBLEM: 'bag-barman-prob01.pddl',
                DataType.DOMAIN: 'bag-barman',
                DataType.ATTRIBUTE: 'dummy_attr',
                'value': 1
            },
            {
                DataType.ALGO: 'rave',
                DataType.PROBLEM: 'bag-gripper-prob01.pddl',
                DataType.DOMAIN: 'bag-gripper',
                DataType.ATTRIBUTE: 'unsolvable',
                'value': 1
            },
        ]

    @staticmethod
    def _read_data(grouping):
        test_dir = os.path.dirname(os.path.realpath(__file__)) + '/../test_data'
        temp = Data.from_file(test_dir + '/simple_report_data.json')
        return temp.group_data(grouping)

    def test_read_data(self):
        test_exists = {
            DataType.ALGO: ['base_unsat', 'rave'],
            DataType.ATTRIBUTE: ['unsolvable', 'var_count', 'dummy_attr'],
            DataType.DOMAIN: ['bag-barman', 'bag-gripper'],
            DataType.PROBLEM: ['bag-barman-prob01.pddl', 'bag-barman-prob02.pddl', 'bag-gripper-prob01.pddl'],
        }
        test_data = self._read_data([])
        for data_type, vals in test_exists.items():
            for val in vals:
                self.assertEqual(test_data.has(data_type, val), True,
                                 'test data does not have ' + str(data_type) + ' ' + val)
        for data_type in DataType:
            self.assertEqual(test_data.has(data_type, 'x'), False, 'test data has ' + str(data_type) + ' ' + val)

        order = [DataType.ALGO, DataType.DOMAIN, DataType.PROBLEM, DataType.ATTRIBUTE]
        for test in self.some_tests:
            data = test_data
            idx = ''
            for item in order:
                data = data[test[item]]
                idx = test[item] + ' '
            self.assertEqual(data, test['value'], 'wrong data at ' + idx)

    def test_grouping(self):
        random.seed(1)
        order = [DataType.ALGO, DataType.DOMAIN, DataType.PROBLEM, DataType.ATTRIBUTE]
        for i in range(10):
            temp_grouping = order.copy()
            random.shuffle(temp_grouping)
            temp_data = self._read_data(temp_grouping)
            for test in self.some_tests:
                data = temp_data
                idx = ''
                for item in temp_grouping:
                    data = data[test[item]]
                    idx = test[item] + ' '
                self.assertEqual(data, test['value'], 'wrong data at ' + idx)

    def test_common_attributes(self):
        test_common = {
            DataType.ALGO: ['base_unsat', 'rave'],
            DataType.ATTRIBUTE: ['unsolvable', 'var_count', 'dummy_attr'],
            DataType.DOMAIN: ['bag-barman', 'bag-gripper'],
            DataType.PROBLEM: ['bag-barman-prob01.pddl', 'bag-barman-prob02.pddl', 'bag-gripper-prob01.pddl'],
        }
        pass
