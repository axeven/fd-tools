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


def get_avg_data(grouped_data, attr):
    avg_data = {}
    for domain, problems in grouped_data.items():
        avg_data[domain] = {}
        for problem, algos in problems.items():
            avg_data[domain][problem] = {}
            for algo, val_list in algos.items():
                temp = 0
                for val in val_list:
                    temp += val[attr]
                avg_data[domain][problem][algo] = temp * 1.0 / len(val_list)
    return avg_data


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


def print_total_per_algo(all_data, stats_order, order, latex):
    if order is None:
        algo_order = []
    else:
        algo_order = order
    print_data = {}
    max_char = 0
    for stat, data in all_data.items():
        print_data[stat] = {}
        for domain, problems in data.items():
            for problem, algos in problems.items():
                if len(algo_order) == 0:
                    for algo in algos:
                        algo_order.append(algo)
                for algo, val_list in algos.items():
                    if algo not in print_data[stat]:
                        print_data[stat][algo] = 0
                    print_data[stat][algo] += data[domain][problem][algo]
        for algo, val in print_data[stat].items():
            if isinstance(val, float):
                max_char = max(max_char, len('{:.2f}'.format(val)))
            else:
                max_char = max(max_char, len(str(val)))
    if latex:
        s = ' '
        t = ' '
        for algo in algo_order:
            s += ' & ' + algo
            for stat in stats_order:
                t += ' & ' + stat
        print(s + ' \\\\')
        print(t + ' \\\\')
        s = 'total'
        for algo in algo_order:
            for stats in stats_order:
                if isinstance(print_data[stats][algo], float):
                    s += ' & ' + '{:.2f}'.format(print_data[stats][algo])
                else:
                    s += ' & ' + str(print_data[stats][algo])
        print(s + ' \\\\')
    else:
        old_max_char = max_char
        max_char = max(max_char, 15)
        col_len = max_char*len(all_data)+len(all_data)-1
        while col_len >= 15 and max_char >= old_max_char:
            max_char -= 1
            col_len = max_char * len(all_data) + len(all_data) - 1
        s = ('{:<'+str(len('total'))+'}').format(' ')
        t = ('{:<'+str(len('total'))+'}').format(' ')
        for algo in algo_order:
            s += ' ' + algo[:col_len].rjust(col_len)
            for stat in stats_order:
                t += ' ' + stat[:max_char].rjust(max_char)
        print(s)
        print(t)

        s = 'total'
        for algo in algo_order:
            for stat in stats_order:
                if isinstance(print_data[stat][algo], float):
                    s += ' ' + ('{:.2f}'.format(print_data[stat][algo])).rjust(max_char)
                else:
                    s += ' ' + str(print_data[stat][algo]).rjust(max_char)
        print(s)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument('--order', '-o',
                        help='space separated string, the order of the algorithm column shown in the table',
                        type=str)
    parser.add_argument('--attribute', '-a',
                        help='the attribute to be computed and shown')
    parser.add_argument('--stats', '-s',
                        help='the statistics to be shown. use & for multiple stats like max&avg', required=True)
    parser.add_argument("--domain-detail", "-d", help="print the detailed per domain data", dest='domain',
                        action='store_true')
    parser.add_argument("--problem-detail", "-p", help="print the detailed per problem data", dest='problem',
                        action='store_true')
    parser.add_argument("--filter", "-f", help="filter the intersection domains and problems only", dest='filter',
                        action='store_true')
    parser.add_argument("--latex", "-l", help="use latex output format", dest='latex',
                        action='store_true')
    parser.set_defaults(domain=False, problem=False, filter=False, latex=False)
    args = parser.parse_args()

    supported = {
        'max': get_max_data,
        'avg': get_avg_data
    }
    stats = args.stats.split('&')
    for s in stats:
        if s not in supported:
            print(s + ' is not supported.')
            print('the supported stats are as follows:')
            print(list(supported.keys()))
            return

    if args.order is not None:
        args.order = args.order.split(' ')

    raw_data, problems = read_json_file(args.json_file, args.filter, False)
    data = {}
    for s, f in supported.items():
        if s in stats:
            data[s] = f(raw_data, args.attribute)
    if args.domain:
        print_detail_per_domain(data, problems, args.order, args.latex)
    if args.problem:
        print_detail_per_problem(data, args.order, args.latex)
    print_total_per_algo(data, stats, args.order, args.latex)


if __name__ == '__main__':
    main()
