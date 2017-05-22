import json

from enum import Enum


class DataType(Enum):
    ALGO = 'algo'
    DOMAIN = 'dom'
    PROBLEM = 'prob'
    ATTRIBUTE = 'attr'


class Data:
    def __init__(self, data={}, grouping_rule=[], algo_counter={}, domain_counter={}, problem_counter={},
                 attr_counter={}):
        self._data = data
        self._counters = {
            DataType.ALGO: algo_counter,
            DataType.DOMAIN: domain_counter,
            DataType.ATTRIBUTE: attr_counter,
            DataType.PROBLEM: problem_counter
        }
        self._grouping_rule = grouping_rule

    def __getitem__(self, item):
        return self._data[item]

    def group_data(self, grouping_rule=[]):

        def initialize_group_id(grouping, parent_data, algo_, dom_, prob_, attr_):
            if grouping == DataType.ALGO:
                if algo_ not in parent_data:
                    parent_data[algo_] = {}
                return algo_
            if grouping == DataType.DOMAIN:
                if dom_ not in parent_data:
                    parent_data[dom_] = {}
                return dom_
            if grouping == DataType.PROBLEM :
                if prob_ not in parent_data:
                    parent_data[prob_] = {}
                return prob_
            if grouping == DataType.ATTRIBUTE :
                if attr_ not in parent_data:
                    parent_data[attr_] = {}
                return attr_

        if len(self._grouping_rule) > 0:
            print("Error: data has been grouped before")
            exit(1)

        if len(grouping_rule) == 0:
            grouping_rule = [DataType.ALGO, DataType.DOMAIN, DataType.PROBLEM, DataType.ATTRIBUTE]
        if len(grouping_rule) != 4:
            print("Error: length of grouping rule has to be 4")
            exit(1)

        data = self._data
        grouped_data = {}
        algorithm_counter = {}
        domain_counter = {}
        problem_counter = {}
        attr_counter = {}
        for idx, run in data.items():
            algo = run['id'][0]
            dom = run['id'][1]
            prob = run['id'][1] + '-' + run['id'][2]
            if algo not in algorithm_counter:
                algorithm_counter[algo] = 0
            if dom not in domain_counter:
                domain_counter[dom] = 0
            if prob not in problem_counter:
                problem_counter[prob] = 0
            algorithm_counter[algo] += 1
            domain_counter[dom] += 1
            problem_counter[prob] += 1
            for attr, val in run.items():
                lvl = [''] * len(grouping_rule)
                for i in range(len(grouping_rule)):
                    parent = grouped_data
                    for j in range(i):
                        parent = parent[lvl[j]]
                    lvl[i] = initialize_group_id(grouping_rule[i], parent, algo, dom, prob, attr)
                parent = grouped_data
                for i in range(len(grouping_rule) - 1):
                    parent = parent[lvl[i]]
                parent[lvl[len(grouping_rule) - 1]] = val
                if attr not in attr_counter:
                    attr_counter[attr] = 0
                attr_counter[attr] += 1

        return Data(grouped_data, grouping_rule, algorithm_counter, domain_counter, problem_counter, attr_counter)

    def has(self, data_type, value):
        return value in self._counters[data_type]

    @staticmethod
    def from_file(json_file):
        with open(json_file) as data_file:
            data = json.load(data_file)
        return Data(data)
