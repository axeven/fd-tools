import json
import re


def read_json_file(json_file, filter_data,  unsolvable_only):
    """
    Returns a dictionary in the following format: dict[domain][problem][algo] = [list of experiment data]
    the algo must have format "algo_name%d" where %d is an integer representing run_id for this algorithm
    """
    print('Reading file ...')
    with open(json_file) as data_file:
        data = json.load(data_file)

    print('Grouping data ...')

    # grouping data
    grouped_data = {}
    existing_problems = {}
    pattern = re.compile(r'(\d+)')
    for idx, val in data.items():
        if val['id'][1] not in grouped_data:
            existing_problems[val['id'][1]] = set()
            if not unsolvable_only or val['unsolvable'] == 1:
                grouped_data[val['id'][1]] = {}
        if val['id'][1] in grouped_data and val['id'][2] not in grouped_data[val['id'][1]]:
            existing_problems[val['id'][1]].add(val['id'][2])
            if not unsolvable_only or val['unsolvable'] == 1:
                grouped_data[val['id'][1]][val['id'][2]] = {}
        if unsolvable_only and val['unsolvable'] == 0:
            continue
        match = pattern.search(val['id'][0])
        if match:
            run_str = match.group(1)
            algo = val['id'][0][0:len(val['id'][0]) - len(run_str)]
            if algo == 'perfect-random' or algo == 'perfect-general-random':
                algo = 'general-random'
            if algo == 'perfect-linear-random':
                algo = 'linear-random'
            if algo == 'linear-random-relevant' or algo == 'perfect-linear-relevant':
                algo = 'linear-relevant-random'
            if algo == 'perfect-dfp-random':
                algo = 'dfp-random'
            if algo not in grouped_data[val['id'][1]][val['id'][2]]:
                grouped_data[val['id'][1]][val['id'][2]][algo] = []
            grouped_data[val['id'][1]][val['id'][2]][algo].append(val)
        else:
            grouped_data[val['id'][1]][val['id'][2]][val['id'][0]] = [val]

    if filter_data:
        print('Filtering base unsat only data ...')

        counter = {}
        for domain, problems in grouped_data.items():
            counter[domain] = {}
            for problem, algos in problems.items():
                if problem not in counter[domain]:
                    counter[domain][problem] = 0
                counter[domain][problem] += len(algos)
        to_del = []
        for domain, problems in grouped_data.items():
            for problem, algos in problems.items():
                if counter[domain][problem] <= 1:
                    to_del.append((domain, problem))
        for domain, problem in to_del:
            del grouped_data[domain][problem]
        to_del = []
        for domain, problems in grouped_data.items():
            if len(grouped_data[domain]) == 0:
                to_del.append(domain)
        for domain in to_del:
            del grouped_data[domain]
        existing_problems = {}
        for domain, problems in grouped_data.items():
            existing_problems[domain] = set()
            for problem, algos in problems.items():
                existing_problems[domain].add(problem)
    return grouped_data, existing_problems
