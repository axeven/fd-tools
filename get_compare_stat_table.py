import json
import os
import argparse


def read_json_simple(json_file, unsolvable_only, exclude=[]):
    # print('Reading file ...')
    with open(json_file) as data_file:
        data = json.load(data_file)
    # print('Grouping data ...')
    excluded = 0
    grouped_data = {}
    existing_problems = {}
    for idx, val in data.items():
        if unsolvable_only and val['unsolvable'] == 0:
            continue
        if val['id'][1] not in grouped_data:
            existing_problems[val['id'][1]] = set()
            grouped_data[val['id'][1]] = {}
        if val['id'][1] in grouped_data and val['id'][2] not in grouped_data[val['id'][1]]:
            existing_problems[val['id'][1]].add(val['id'][2])
            grouped_data[val['id'][1]][val['id'][2]] = {}
        if val['id'][0] not in exclude:
            grouped_data[val['id'][1]][val['id'][2]][val['id'][0]] = val
        else:
            excluded += 1

    if excluded == 0 and len(exclude) > 0:
        print('Warning: no data excluded for exclude=', str(exclude))

    # print('Filtering intersection only data ...')

    counter = {}
    max_counter = 0
    for domain, problems in grouped_data.items():
        counter[domain] = {}
        for problem, algos in problems.items():
            counter[domain][problem] = len(algos)
            max_counter = max(len(algos), max_counter)
    to_del = []
    for domain, problems in grouped_data.items():
        for problem, algos in problems.items():
            if counter[domain][problem] < max_counter:
                to_del.append((domain, problem))
    for domain, problem in to_del:
        del grouped_data[domain][problem]
    to_del = []
    for domain, problems in grouped_data.items():
        if len(grouped_data[domain]) == 0:
            to_del.append(domain)
    for domain in to_del:
        del grouped_data[domain]

    # filtering unused instances

    domain_to_del = []
    for domain, problems in grouped_data.items():
        prob_to_del = []
        for problem, algos in problems.items():
            if len(algos) == 0:
                prob_to_del.append(problem)
        for p in prob_to_del:
            del problems[p]
            existing_problems[domain].remove(p)
        if len(problems) == 0:
            domain_to_del.append(domain)
    for d in domain_to_del:
        del grouped_data[d]
        del existing_problems[d]

    return grouped_data, existing_problems


def print_stats(grouped_data, algorithms, attr, max_val):
    # print('Processing data ...')

    # processing data
    val_data = {}
    for domain, problems in grouped_data.items():
        for problem, algos in problems.items():
            for algo, val_list in algos.items():
                if algo in algorithms:
                    if algo not in val_data:
                        val_data[algo] = []
                    if val_list['unsolvable'] == 0:
                        val_data[algo].append(max_val)
                    else:
                        val_data[algo].append(val_list[attr])
    total_data = 0
    for alg in algorithms:
        if total_data == 0:
            total_data = len(val_data[alg])
        else:
            assert len(val_data[alg]) == total_data

    s = ''
    for alg in algorithms:
        s += alg + ' '
    print(s)
    for i in range(total_data):
        s = ''
        for alg in algorithms:
            s += str(val_data[alg][i]) + ' '
        print(s)


def create_dirs_if_necessary(graph_data, OUTDIR):
    for domain, problems in graph_data.items():
        if not os.path.exists(OUTDIR + '/' + domain):
            os.makedirs(OUTDIR + '/' + domain)


def check_attribute_exists(grouped_data, attr):
    attrs = []
    for domain, problems in grouped_data.items():
        for problem, algos in problems.items():
            for algo, runs in algos.items():
                attrs = runs.keys()
            break
        break
    if attr in attrs:
        return True
    else:
        print('Attribute ' + attr + ' doesn\'t exists.')
        print('Available attributes are:')
        attrs = sorted(attrs)
        for a in attrs:
            print(a)
        return False


def check_algorithm_exists(grouped_data, alg):
    attrs = []
    for domain, problems in grouped_data.items():
        for problem, algos in problems.items():
            algs = algos.keys()
        break
    if alg in algs:
        return True
    else:
        print('Algorithm ' + alg + ' doesn\'t exists.')
        print('Algorithm attributes are:')
        algs = sorted(algs)
        for a in algs:
            print(a)
        return False


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument("--attribute", "-a", help="attribute to use", default="max_abstraction_states")
    parser.add_argument("--unsolvable-only", "-u", help="only count the unsolvable instances", dest='unsolvable_only',
                        action='store_true')
    parser.add_argument("--max", '-m', help="maximum default value if it is fail", default='0')
    parser.add_argument("--algos", help="histogram range (int)", nargs='+')
    parser.set_defaults(unsolvable_only=False)
    args = parser.parse_args()

    data, problems = read_json_simple(args.json_file, args.unsolvable_only)
    if check_attribute_exists(data, args.attribute):
        for alg in args.algos:
            if not check_algorithm_exists(data, alg):
                return
        print_stats(data, args.algos, args.attribute, args.max)


if __name__ == '__main__':
    main()
