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


def get_table_detail_per_problem(all_data):
    detail_data = {}
    for stat, max_data in all_data.items():
        detail_data[stat] = {}
        for domain, problems in max_data.items():
            row_stem = '{:<10}'.format(domain[:10]) + ':'
            for problem, algos in problems.items():
                row = row_stem + problem
                detail_data[stat][row] = {}
                for algo, val in algos.items():
                    detail_data[stat][row][algo] = max_data[domain][problem][algo]
    return detail_data


def get_detail_per_domain_data(all_data):
    # grouping data per domain
    detail_data = {}
    for stat, max_data in all_data.items():
        detail_data[stat] = {}
        for domain, problems in max_data.items():
            detail_data[stat][domain] = {}
            for problem, algos in problems.items():
                for algo, val in algos.items():
                    if algo not in detail_data[stat][domain]:
                        detail_data[stat][domain][algo] = 0
                    detail_data[stat][domain][algo] += val
    return detail_data


def get_table_detail_per_domain(all_data, problem_list):
    # grouping data per domain
    detail_data = {}
    for stat, max_data in all_data.items():
        detail_data[stat] = {}
        for domain, problems in max_data.items():
            row = domain + ' (' + str(len(problem_list[domain])) + ')'
            detail_data[stat][row] = {}
            for problem, algos in problems.items():
                for algo, val in algos.items():
                    if algo not in detail_data[stat][row]:
                        detail_data[stat][row][algo] = 0
                    detail_data[stat][row][algo] += val
    return detail_data


def get_table_total_per_algo(all_data):
    detail_data = {}
    for stat, data in all_data.items():
        detail_data[stat] = {}
        detail_data[stat]['total'] = {}
        for domain, problems in data.items():
            for problem, algos in problems.items():
                for algo, val_list in algos.items():
                    if algo not in detail_data[stat]['total']:
                        detail_data[stat]['total'][algo] = 0
                    detail_data[stat]['total'][algo] += data[domain][problem][algo]
    return detail_data


def print_data(all_data, stats_order, order, latex):
    if order is None:
        algo_order = []
    else:
        algo_order = order
    max_char = 0
    for stat, rows in all_data.items():
        for row_name, algos in rows.items():
            if len(algo_order) == 0:
                for algo in algos:
                    algo_order.append(algo)
                algo_order = sorted(algo_order)
            else:
                break
            for algo, val in algos.items():
                if isinstance(val, float):
                    max_char = max(max_char, len('{:.2f}'.format(val)))
                else:
                    max_char = max(max_char, len(str(val)))

    row_order = sorted(list(list(all_data.values())[0].keys()))
    if latex:
        s = ' '
        t = ' '
        for algo in algo_order:
            s += ' & ' + algo
            for stat in stats_order:
                t += ' & ' + stat
        print(s + ' \\\\')
        print(t + ' \\\\')

        for row in row_order:
            s = row
            for algo in algo_order:
                for stats in stats_order:
                    if isinstance(all_data[stats][row][algo], float):
                        s += ' & ' + '{:.2f}'.format(all_data[stats][row][algo])
                    else:
                        s += ' & ' + str(all_data[stats][row][algo])
            print(s + ' \\\\')
    else:
        old_max_char = max_char
        max_char = max(max_char, 15)
        col_len = max_char * len(all_data) + len(all_data) - 1
        while col_len >= 15 and max_char >= old_max_char:
            max_char -= 1
            col_len = max_char * len(all_data) + len(all_data) - 1

        max_row_len = 0
        for row in row_order:
            max_row_len = max(max_row_len, len(row))
        s = ('{:<' + str(max_row_len) + '}').format(' ')
        t = ('{:<' + str(max_row_len) + '}').format(' ')
        for algo in algo_order:
            s += ' ' + algo[:col_len].rjust(col_len)
            for stat in stats_order:
                t += ' ' + stat[:max_char].rjust(max_char)
        print(s)
        print(t)

        for row in row_order:
            s = ('{:<' + str(max_row_len) + '}').format(row)
            for algo in algo_order:
                for stat in stats_order:
                    if isinstance(all_data[stat][row][algo], float):
                        s += ' ' + ('{:.2f}'.format(all_data[stat][row][algo])).rjust(max_char)
                    else:
                        s += ' ' + str(all_data[stat][row][algo]).rjust(max_char)
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
        domain_table = get_table_detail_per_domain(data, problems)
        print_data(domain_table, stats, args.order, args.latex)
    if args.problem:
        problem_table = get_table_detail_per_problem(data)
        print_data(problem_table, stats, args.order, args.latex)
        # print_detail_per_problem(data, args.order, args.latex)
    total_table = get_table_total_per_algo(data)
    print_data(total_table, stats, args.order, args.latex)


if __name__ == '__main__':
    main()
