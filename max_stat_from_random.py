import json
import re
import os
import matplotlib.pyplot as plt
import argparse

from matplotlib.legend_handler import HandlerLine2D


def read_json_file(json_file):
    print('Reading file ...')
    with open(json_file) as data_file:
        data = json.load(data_file)

    print('Grouping data ...')

    # grouping data
    grouped_data = {}
    pattern = re.compile(r'(\d+)')
    for idx, val in data.items():
        if val['id'][1] not in grouped_data:
            grouped_data[val['id'][1]] = {}
        if val['id'][2] not in grouped_data[val['id'][1]]:
            grouped_data[val['id'][1]][val['id'][2]] = {}

        match = pattern.search(val['id'][0])
        if match:
            run_str = match.group(1)
            algo = val['id'][0][0:len(val['id'][0]) - len(run_str)]

            if algo not in grouped_data[val['id'][1]][val['id'][2]]:
                grouped_data[val['id'][1]][val['id'][2]][algo] = []
            grouped_data[val['id'][1]][val['id'][2]][algo].append(val)
        else:
            grouped_data[val['id'][1]][val['id'][2]][val['id'][0]] = [val]
    return grouped_data


def print_summary(grouped_data, print_detail):
    print('Processing data ...')

    # processing data
    max_data = {}
    for domain, problems in grouped_data.items():
        max_data[domain] = {}
        for problem, algos in problems.items():
            max_data[domain][problem] = {}
            for algo, val_list in algos.items():
                temp = {'unsolvable': 0, 'solvable': 0}
                for val in val_list:
                    temp['unsolvable'] = max(temp['unsolvable'], val['unsolvable'])
                    temp['solvable'] = max(temp['solvable'], val['solvable'])
                max_data[domain][problem][algo] = temp

    if print_detail:
        detail_data = {}
        for domain, problems in max_data.items():
            detail_data[domain] = {}
            for problem, algos in problems.items():
                for algo, attrs in algos.items():
                    if algo not in detail_data[domain]:
                        detail_data[domain][algo] = {'unsolvable': 0, 'solvable': 0}
                    detail_data[domain][algo]['unsolvable'] += attrs['unsolvable']
                    detail_data[domain][algo]['solvable'] += attrs['solvable']
        algo_order = []
        for domain, algos in detail_data.items():
            if len(algo_order) == 0:
                s = '{:<15}'.format('domain')
                for algo in algos:
                    algo_order.append(algo)
                    s += ' ' +  '{:<15}'.format(algo[:15])
                print(s)
            s = '{:<15}'.format(domain[:15])
            for algo in algo_order:
                s += ' ' + str(detail_data[domain][algo]['unsolvable']).rjust(15)
            print(s)

    print_data = {}
    for domain, problems in max_data.items():
        for problem, algos in problems.items():
            for algo, val_list in algos.items():
                if algo not in print_data:
                    print_data[algo] = {'unsolvable': 0, 'solvable': 0}
                print_data[algo]['unsolvable'] += max_data[domain][problem][algo]['unsolvable']
                print_data[algo]['solvable'] += max_data[domain][problem][algo]['solvable']

    # printing
    for algo, data in print_data.items():
        print('%s\t:%d\t%d' % (algo, data['unsolvable'], data['solvable']))
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument("--detail", "-d", help=".json file containing the lab data", default=True)
    args = parser.parse_args()
    data = read_json_file(args.json_file)
    print_summary(data, args.detail)

if __name__ == '__main__':
    main()
