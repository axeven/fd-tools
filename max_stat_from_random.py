import argparse

from common import read_json_file


def print_summary(grouped_data, print_detail_per_domain, print_detail_per_problem):
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

    algo_order = []
    if print_detail_per_problem:
        for domain, problems in max_data.items():
            for problem, algos in problems.items():
                if len(algo_order) == 0:
                    s = '{:<25}'.format('domain')
                    for algo in algos:
                        algo_order.append(algo)
                        s += ' ' + '{:<15}'.format(algo[:15])
                    print(s)
                s = '{:<15}'.format(domain[:15])
                s += '{:<10}'.format(problem[:10])
                for algo in algo_order:
                    s += ' ' + str(max_data[domain][problem][algo]['unsolvable']).rjust(15)
                print(s)

    print_data = {}
    for domain, problems in max_data.items():
        for problem, algos in problems.items():
            if len(algo_order) == 0:
                for algo in algos:
                    algo_order.append(algo)
            for algo, val_list in algos.items():
                if algo not in print_data:
                    print_data[algo] = {'unsolvable': 0, 'solvable': 0}
                print_data[algo]['unsolvable'] += max_data[domain][problem][algo]['unsolvable']
                print_data[algo]['solvable'] += max_data[domain][problem][algo]['solvable']

    # printing
    for algo in algo_order:
        s = '{:<25}'.format(algo[:25])
        print('%s:%d\t%d' % (s, print_data[algo]['unsolvable'], print_data[algo]['solvable']))
    return


def get_max_data(grouped_data, attr):
    max_data = {}
    for domain, problems in grouped_data.items():
        max_data[domain] = {}
        for problem, algos in problems.items():
            max_data[domain][problem] = {}
            for algo, val_list in algos.items():
                temp = 0
                for val in val_list:
                    temp = max(temp, val[attr])
                max_data[domain][problem][algo] = temp
    return max_data


def print_detail_per_domain(max_data, problem_list, order, latex):
    # grouping data per domain
    detail_data = {}
    for domain, problems in max_data.items():
        detail_data[domain] = {}
        for problem, algos in problems.items():
            for algo, val in algos.items():
                if algo not in detail_data[domain]:
                    detail_data[domain][algo] = 0
                detail_data[domain][algo] += val
    if order is None:
        algo_order = []
    else:
        algo_order = order
    header_printed = False
    for domain in sorted(detail_data.keys()):
        algos = detail_data[domain]
        if len(algo_order) == 0:
            for algo in algos:
                algo_order.append(algo)
        if not header_printed:
            if latex:
                s = 'Domain (\# instances)'
                for algo in algo_order:
                    s += ' & ' + algo
                print(s + ' \\\\')
            else:
                s = '{:<15}'.format('domain')
                for algo in algos:
                    s += ' ' + '{:<15}'.format(algo[:15])
                print(s)
            header_printed = True
        if latex:
            s = domain + ' ({:d})'.format(len(problem_list[domain]))
            for algo in algo_order:
                s += ' & ' + str(detail_data[domain][algo])
            print(s + ' \\\\')
        else:
            s = '{:<15}'.format(domain[:15])
            for algo in algo_order:
                s += ' ' + str(detail_data[domain][algo]).rjust(15)
            print(s)


def print_summary_latex_format(grouped_data, problem_list, order, print_detail_per_domain, print_detail_per_problem):
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

    if order is None:
        algo_order = []
    else:
        algo_order = order
    if print_detail_per_problem:
        for domain in sorted(max_data.keys()):
            problems = max_data[domain]
            for problem, algos in problems.items():
                if len(algo_order) == 0:
                    s = 'Domain:problem'
                    for algo in algos:
                        algo_order.append(algo)
                        s += ' & ' + algo
                    print(s + ' \\\\')
                s = '{:<15}'.format(domain[:15])
                s += '{:<10}'.format(problem[:10])
                for algo in algo_order:
                    s += ' & ' + str(max_data[domain][problem][algo]['unsolvable'])
                print(s + ' \\\\')

    print_data = {}
    for domain, problems in max_data.items():
        for problem, algos in problems.items():
            if len(algo_order) == 0:
                for algo in algos:
                    algo_order.append(algo)
            for algo, val_list in algos.items():
                if algo not in print_data:
                    print_data[algo] = {'unsolvable': 0, 'solvable': 0}
                print_data[algo]['unsolvable'] += max_data[domain][problem][algo]['unsolvable']
                print_data[algo]['solvable'] += max_data[domain][problem][algo]['solvable']

    # printing
    for algo in algo_order:
        s = '{:<25}'.format(algo[:25])
        print('%s:%d\t%d' % (s, print_data[algo]['unsolvable'], print_data[algo]['solvable']))
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument('--order', '-o', help='space separated string, the order of the algorithm column shown in the table',
                        type=str)
    parser.add_argument('--attribute', '-a',
                        help='the attribute to be computed and shown')
    parser.add_argument("--domain-detail", "-d", help="print the detailed per domain data", dest='domain',
                        action='store_true')
    parser.add_argument("--problem-detail", "-p", help="print the detailed per problem data", dest='problem',
                        action='store_true')
    parser.add_argument("--filter", "-f", help="filter the intersection domains and problems only", dest='filter',
                        action='store_true')
    parser.add_argument("--latex", "-l", help="use latex output format", dest='latex',
                        action='store_true')
    parser.set_defaults(domain=False)
    parser.set_defaults(problem=False)
    parser.set_defaults(filter=False)
    parser.set_defaults(latex=False)
    args = parser.parse_args()

    if args.order is not None:
        args.order = args.order.split(' ')

    data, problems = read_json_file(args.json_file, args.filter, False)
    max_data = get_max_data(data, args.attribute)
    if args.domain:
        print_detail_per_domain(max_data, problems, args.order, args.latex)
    if args.latex:
        print_summary_latex_format(data, problems, args.order, args.domain, args.problem)
    else:
        print_summary(data, args.domain, args.problem)


if __name__ == '__main__':
    main()
