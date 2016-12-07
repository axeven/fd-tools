import json
import os
import matplotlib.pyplot as plt
import argparse

from matplotlib.legend_handler import HandlerLine2D
from matplotlib.font_manager import FontProperties
from common import read_json_file, check_attribute_exists

def get_generator_function(gen_name):
    if gen_name == 'max':
        def func(a, b):
            return max(a, b)
    else:
        def func(a, b):
            return a + b
    return func


def generate_new_data(old_data, gen_func, attr1, attr2, new_attr):
    used = False
    for id, val in old_data.items():
        if attr1 in val and val[attr1] is not None and attr2 in val and val[attr2] is not None:
            used = True
            val[new_attr] = gen_func(val[attr1], val[attr2])
        else:
            val[new_attr] = None
    if not used:
        print('No value generated for the new attribute')
    return old_data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument("--outfile", "-o", help="output file", default="output")
    parser.add_argument("--attribute-1", "-a1", help="attribute to join", default="max_abstraction_states")
    parser.add_argument("--attribute-2", "-a2", help="attribute to join", default="computation_time")
    parser.add_argument("--attribute-new", "-an", help="new attribute name", default="new_attribute")
    parser.add_argument("--function", "-f", help="function to generate new attribute")

    args = parser.parse_args()

    print('Reading file ...')
    with open(args.json_file) as data_file:
        data = json.load(data_file)
    print('Generating new attribute ...')
    gen_func = get_generator_function(args.function)
    data = generate_new_data(data, gen_func, args.attribute_1, args.attribute_2, args.attribute_new)
    print('Writing file ...')
    with open(args.outfile, 'w') as f:
        json.dump(data, f)

if __name__ == '__main__':
    main()
