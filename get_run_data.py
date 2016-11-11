import argparse
import json


def read_json_file(json_file, attr, unsolvable_only, domain, problem, algo, query):
    """
    Returns a dictionary in the following format: dict[domain][problem][algo] = [list of experiment data]
    the algo must have format "algo_name%d" where %d is an integer representing run_id for this algorithm
    """
    print('Reading file ...')
    with open(json_file) as data_file:
        data = json.load(data_file)

    print('Querying ...')
    q_data = {}
    for idx, val in data.items():
        if unsolvable_only and not val['unsolvable']:
            continue
        if algo is not None and not val['id'][0].startswith(algo):
            continue
        if domain is not None and not val['id'][1] == domain:
            continue
        if problem is not None and not val['id'][2] == problem:
            continue
        passed = True
        for qattr, qval in query:
            if val[qattr] != qval:
                passed = False
                break
        if passed:
            q_data[idx] = val[attr]
    return q_data

def parse_query(query_string):
    single = query_string.split('&')
    query = []
    for q in single:
        attr = q.split('=')[0]
        val = q.split('=')[1]
        try:
            val = int(val)
        except ValueError:
            pass
        query.append((attr, val))
    return query


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument('--domain', '-d', help='domain name')
    parser.add_argument('--problem', '-p', help='problem name')
    parser.add_argument('--algo-start', '-al', help='algorithm name starts with')
    parser.add_argument("--query", "-q", help="the query")
    parser.add_argument("--attribute", "-at", help="attribute to show")
    parser.add_argument("--unsolvable-only", "-u", help="only count the unsolvable instances", dest='unsolvable_only',
                        action='store_true')
    parser.set_defaults(unsolvable_only=False)

    args = parser.parse_args()
    query = parse_query(args.query)

    data = read_json_file(args.json_file, args.attribute, args.unsolvable_only, args.domain, args.problem, args.algo_start, query)
    for idx, val in data.items():
        print(idx, val)


if __name__ == '__main__':
    main()
