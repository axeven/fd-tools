import json
import os
import argparse


def read_json_simple(json_file, unsolvable_only, exclude=[]):
    print('Reading file ...')
    with open(json_file) as data_file:
        data = json.load(data_file)
    print('Grouping data ...')
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


def create_histogram_per_algo(grouped_data, rangelist, attr):
    print('Processing data ...')

    # processing data
    val_data = {}
    for domain, problems in grouped_data.items():
        for problem, algos in problems.items():
            for algo, val_list in algos.items():
                if algo not in val_data:
                    val_data[algo] = []
                val_data[algo].append(val_list[attr])
                assert val_list['unsolvable'] == 1
    graph_data = {}
    for algo, vals in val_data.items():
        graph_data[algo] = [0] * (len(rangelist) + 1)
        for val in vals:
            added = False
            for i in range(len(rangelist)):
                if val < rangelist[i]:
                    graph_data[algo][i] += 1
                    added = True
                    break
            if not added:
                graph_data[algo][len(rangelist)] += 1

    for algo, data in graph_data.items():
        print(algo)
        for i in range(len(rangelist)):
            print('<', rangelist[i], ':', data[i])
        print('>=', rangelist[i], ':', data[len(rangelist)])


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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument("--attribute", "-a", help="attribute to use", default="max_abstraction_states")
    parser.add_argument("--unsolvable-only", "-u", help="only count the unsolvable instances", dest='unsolvable_only',
                        action='store_true')
    parser.add_argument("--range", help="histogram range (int)", nargs='+')
    parser.set_defaults(unsolvable_only=False)
    args = parser.parse_args()

    rangelist = [int(i) for i in args.range]

    data, problems = read_json_simple(args.json_file, args.unsolvable_only)
    if check_attribute_exists(data, args.attribute):
        create_histogram_per_algo(data, rangelist, args.attribute)


if __name__ == '__main__':
    main()
