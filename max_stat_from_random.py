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

    if print_detail_per_problem:
        algo_order = []
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

    if print_detail_per_domain:
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
                    s += ' ' + '{:<15}'.format(algo[:15])
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
    for algo in algo_order:
        s = '{:<25}'.format(algo[:25])
        print('%s:%d\t%d' % (s, print_data[algo]['unsolvable'], print_data[algo]['solvable']))
    return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument("--domain-detail", "-d", help="print the detailed per domain data", dest='domain',
                        action='store_true')
    parser.add_argument("--problem-detail", "-p", help="print the detailed per problem data", dest='problem',
                        action='store_true')
    parser.add_argument("--filter", "-f", help="filter the intersection domains and problems only", dest='filter',
                        action='store_true')
    parser.set_defaults(domain=False)
    parser.set_defaults(problem=False)
    parser.set_defaults(filter=False)
    args = parser.parse_args()
    data = read_json_file(args.json_file, args.filter)
    print_summary(data, args.domain, args.problem)


if __name__ == '__main__':
    main()
