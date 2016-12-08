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

    passed_count = [0, 0, 0, 0]
    for idx, val in data.items():
        if unsolvable_only and not val['unsolvable']:
            continue
        passed_count[0] += 1
        if algo is not None and not val['id'][0].startswith(algo):
            continue
        passed_count[1] += 1
        if domain is not None and not val['id'][1] == domain:
            continue
        passed_count[2] += 1
        if problem is not None and not val['id'][2] == problem:
            continue
        passed_count[3] += 1
        passed = True
        for qattr, comparator, qval in query:
            if qattr in val:
                if not comparator(val[qattr], qval):
                    passed = False
                    break
        if passed:
            q_data[idx] = val[attr]
    if passed_count[0] == 0:
        print('No unsolvable data found')
    elif passed_count[1] == 0:
        print('algo', algo, 'not found')
    elif passed_count[2] == 0:
        print('domain', domain, 'not found')
    elif passed_count[3] == 0:
        print('problem', problem, 'not found')

    return q_data


def equal(a, b):
    return a == b


def lte(a, b):
    return a <= b


def gte(a, b):
    return a >= b


def parse_query(query_string):
    single = query_string.split('&')
    query = []
    for q in single:
        if '<=' in q:
            qs = q.split('<=')
        elif '>=' in q:
            qs = q.split('>=')
        elif '=' in q:
            qs = q.split('=')
        attr = qs[0]
        val = qs[1]
        try:
            val = int(val)
        except ValueError:
            pass
        if '<=' in q:
            query.append((attr, lte, val))
        elif '>=' in q:
            query.append((attr, gte, val))
        elif '=' in q:
            query.append((attr, equal, val))
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

    data = read_json_file(args.json_file, args.attribute, args.unsolvable_only, args.domain, args.problem,
                          args.algo_start, query)
    for idx, val in data.items():
        print(idx, val)


if __name__ == '__main__':
    main()
