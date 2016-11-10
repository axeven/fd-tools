import argparse

from common import read_json_file


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


def print_detail_per_problem(max_data, order, latex):
    if order is None:
        algo_order = []
    else:
        algo_order = order
    header_printed = False
    for domain in sorted(max_data.keys()):
        problems = max_data[domain]
        for problem, algos in problems.items():
            if len(algo_order) == 0:
                for algo in algos:
                    algo_order.append(algo)
            if not header_printed:
                if latex:
                    s = 'Domain:problem'
                    for algo in algos:
                        s += ' & ' + algo
                    print(s + ' \\\\')
                else:
                    s = '{:<25}'.format('domain')
                    for algo in algos:
                        s += ' ' + '{:<15}'.format(algo[:15])
                    print(s)
                header_printed = True
            if latex:
                s = '{:<15}'.format(domain[:15])
                s += '{:<10}'.format(problem[:10])
                for algo in algo_order:
                    s += ' & ' + str(max_data[domain][problem][algo])
                print(s + ' \\\\')
            else:
                s = '{:<15}'.format(domain[:15])
                s += '{:<10}'.format(problem[:10])
                for algo in algo_order:
                    s += ' ' + str(max_data[domain][problem][algo]).rjust(15)
                print(s)


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


def print_total_per_algo(max_data, order, latex):
    if order is None:
        algo_order = []
    else:
        algo_order = order
    print_data = {}
    for domain, problems in max_data.items():
        for problem, algos in problems.items():
            if len(algo_order) == 0:
                for algo in algos:
                    algo_order.append(algo)
            for algo, val_list in algos.items():
                if algo not in print_data:
                    print_data[algo] = 0
                print_data[algo] += max_data[domain][problem][algo]
    if latex:
        s = ' '
        for algo in algo_order:
            s += ' & ' + algo
        print(s + ' \\\\')
        s = 'total'
        for algo in algo_order:
            s += ' & ' + str(print_data[algo])
        print(s + ' \\\\')
    else:
        s = '{:<15}'.format(' ')
        for algo in algos:
            s += ' ' + '{:<15}'.format(algo[:15])
        print(s)
        s = '{:<15}'.format('total')
        for algo in algo_order:
            s += ' ' + str(print_data[algo]).rjust(15)
        print(s)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument('--order', '-o',
                        help='space separated string, the order of the algorithm column shown in the table',
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
    if args.problem:
        print_detail_per_problem(max_data, args.order, args.latex)
    print_total_per_algo(max_data, args.order, args.latex)


if __name__ == '__main__':
    main()
