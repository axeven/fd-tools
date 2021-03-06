"""

param: attribute, separator, index, json_file

show latex table of selected attribute based on the data in json_file
the order of columns are determined by the value of run's id at index after
the id is split by separator

"""
import argparse
import json


def read_json_simple(json_file, exclude=[]):
    print('Reading file ...')
    with open(json_file) as data_file:
        data = json.load(data_file)
    print('Grouping data ...')
    excluded = 0
    grouped_data = {}
    existing_problems = {}
    for idx, val in data.items():
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


def algo_order_by_sub_name(data, separator, index, cast, order=[]):
    algo_list = []
    for domain, problems in data.items():
        for problem, algos in problems.items():
            for algo, val_list in algos.items():
                algo_list.append((cast(algo.split(separator)[index]), algo))
            break
        break
    if len(order) == 0:
        algo_list.sort(key=lambda tup: tup[0])
        return [alg for key, alg in algo_list]
    else:
        # assumes order and algo_list has bijection relation
        res = []
        for o in order:
            for id, alg in algo_list:
                if id.startswith(o):
                    res.append(alg)
        return res


def get_table_detail_per_domain(all_data, attr, problem_list):
    # grouping data per domain
    detail_data = {}
    for domain, problems in all_data.items():
        row = domain + ' (' + str(len(problem_list[domain])) + ')'
        detail_data[row] = {}
        for problem, algos in problems.items():
            for algo, val in algos.items():
                if algo not in detail_data[row]:
                    detail_data[row][algo] = 0
                detail_data[row][algo] += val[attr]
    return detail_data


def print_data(all_data, order, separator, index):
    max_char = 0
    for row_name, algos in all_data.items():
        for algo, val in algos.items():
            if isinstance(val, float):
                max_char = max(max_char, len('{:.2f}'.format(val)))
            else:
                max_char = max(max_char, len(str(val)))

    row_order = sorted(list(all_data.keys()))
    s = ' '
    for alg in order:
        s += ' & ' + alg.split(separator)[index]
    print(s + ' \\\\')

    sum = {}
    for row in row_order:
        s = row
        for alg in order:
            if isinstance(all_data[row][alg], float):
                s += ' & ' + '{:.2f}'.format(all_data[row][alg])
            else:
                s += ' & ' + str(all_data[row][alg])
            if alg not in sum:
                sum[alg] = 0
            sum[alg] += all_data[row][alg]

        print(s + ' \\\\')

    s = 'Total '
    for alg in order:
        if isinstance(sum[alg], float):
            s += ' & ' + '{:.2f}'.format(sum[alg])
        else:
            s += ' & ' + str(sum[alg])
    print(s + ' \\\\')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="file or folder containing the log data")
    parser.add_argument("--col_split", help="substring algorithm name splitter", default='-')
    parser.add_argument("--col_split_id", help="index of split algorithm name used for id", default=0, type=int)
    parser.add_argument("--col_split_cast", help="cast for the column id", default='str')
    parser.add_argument("--attr", help="attribute to show", default='unsolvable')
    parser.add_argument("--col_order", help="the order of (algorithm) columns (comma separated)")
    parser.add_argument('--exclude', '-e', help='excluded algorithms (comma separated)')
    args = parser.parse_args()

    if args.exclude is None:
        args.exclude = []
    else:
        args.exclude = args.exclude.split(',')

    if args.col_order is None:
        args.col_order = []
    else:
        args.col_order = args.col_order.split(',')

    known_types = {'str': str, 'int': int, 'float': float}
    if args.col_split_cast not in known_types:
        print('Unknown type for casting column id')
        exit(1)

    data, problems = read_json_simple(args.input_file, exclude=args.exclude)
    algo_order = algo_order_by_sub_name(data, args.col_split, args.col_split_id, known_types[args.col_split_cast],
                                        args.col_order)
    table_data = get_table_detail_per_domain(data, args.attr, problems)
    print_data(table_data, algo_order, args.col_split, args.col_split_id)


if __name__ == '__main__':
    main()
