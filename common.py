import glob
import json
import os
import re

SUITE_TOO_LARGE = ['bag-barman']
SUITE_TRIVIAL = ['bottleneck']
SUITE_NONTRIVIAL_UNSOLVABLE = []
SUITE_SOLVABLE = []
SUITE_UNKNOWN = []
# bag-gripper
for i in range(1, 26):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('bag-gripper:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 6):
    SUITE_SOLVABLE.append('bag-gripper:satprob' + ('%02d' % i) + '.pddl')
# bag-transport
for i in [2, 5, 11, 20, 21]:
    SUITE_NONTRIVIAL_UNSOLVABLE.append('bag-transport:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 30):
    SUITE_SOLVABLE.append('bag-transport:satprob' + ('%02d' % i) + '.pddl')
# cave-diving
for i in range(1, 26):
    if i != 5:
        SUITE_NONTRIVIAL_UNSOLVABLE.append('cave-diving:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 6):
    SUITE_SOLVABLE.append('cave-diving:satprob' + ('%02d' % i) + '.pddl')
# chessboard-pebbling
for i in range(3, 26):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('chessboard-pebbling:prob' + ('%02d' % i) + '.pddl')
# diagnosis
for i in [4, 5, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
    SUITE_NONTRIVIAL_UNSOLVABLE.append('diagnosis:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 124):
    SUITE_SOLVABLE.append('diagnosis:satprob' + ('%02d' % i) + '.pddl')
# document-transfer
for i in [1, 2, 3, 5, 7, 8, 10, 11, 13, 14, 18, 19]:
    SUITE_NONTRIVIAL_UNSOLVABLE.append('document-transfer:prob' + ('%02d' % i) + '.pddl')
for i in [1, 2, 3, 4, 5, 10]:
    SUITE_SOLVABLE.append('document-transfer:satprob' + ('%02d' % i) + '.pddl')
for i in range(1, 10):
    SUITE_UNKNOWN.append('document-transfer:unknownprob' + ('%02d' % i) + '.pddl')
# over-nomystery
for i in range(3, 25):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('over-nomystery:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 6):
    SUITE_SOLVABLE.append('over-nomystery:satprob' + ('%02d' % i) + '.pddl')
# over-rovers
for i in [4, 6, 7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]:
    SUITE_NONTRIVIAL_UNSOLVABLE.append('over-rovers:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 7):
    SUITE_SOLVABLE.append('over-rovers:satprob' + ('%02d' % i) + '.pddl')
# over-tpp
for i in range(1, 31):
    if i != 2 and i != 3:
        SUITE_NONTRIVIAL_UNSOLVABLE.append('over-tpp:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 5):
    SUITE_SOLVABLE.append('over-tpp:satprob' + ('%02d' % i) + '.pddl')
# pegsol
for i in range(9, 31):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('pegsol:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 6):
    SUITE_SOLVABLE.append('pegsol:satprob' + ('%02d' % i) + '.pddl')
# pegsol-row5
for i in range(4, 16):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('pegsol-row5:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 6):
    SUITE_SOLVABLE.append('pegsol-row5:satprob' + ('%02d' % i) + '.pddl')
# sliding-tiles
for i in range(1, 21):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('sliding-tiles:prob' + ('%02d' % i) + '.pddl')
for i in range(1, 6):
    SUITE_SOLVABLE.append('sliding-tiles:satprob' + ('%02d' % i) + '.pddl')
# tetris
for i in range(6, 21):
    SUITE_NONTRIVIAL_UNSOLVABLE.append('tetris:prob' + ('%02d' % i) + '.pddl')


def read_json_file(json_file, filter_data, unsolvable_only, filter_suite=None):
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

    if filter_suite is not None:
        domain_to_del = []
        for domain, problems in grouped_data.items():
            prob_to_del = []
            for prob, algos in problems.items():
                if domain + ':' + prob not in filter_suite:
                    prob_to_del.append(prob)
            for prob in prob_to_del:
                del problems[prob]
            if len(problems) == 0:
                domain_to_del.append(domain)
        for domain in domain_to_del:
            del grouped_data[domain]
    existing_problems = {}
    for domain, problems in grouped_data.items():
        existing_problems[domain] = set()
        for problem, algos in problems.items():
            existing_problems[domain].add(problem)
    return grouped_data, existing_problems


def check_attribute_exists(grouped_data, attr):
    attrs = []
    for domain, problems in grouped_data.items():
        for problem, algos in problems.items():
            for algo, runs in algos.items():
                for run in runs:
                    attrs = run.keys()
                    break
                break
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


def get_file_list(folder, ext=None):
    """
    Get the file list recursively with a certain extension of the folder
    """
    files = []
    if ext is None:
        dir = folder + '/**/*'
    else:
        dir = folder + '/**/*' + ext
    for sub in glob.glob(dir, recursive=True):
        if os.path.isfile(sub):
            files.append(folder + str(sub)[len(folder):])
    return files
