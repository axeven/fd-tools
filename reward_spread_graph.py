#!/usr/bin/env python3

import argparse
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import re

from common import get_file_list
from PIL import Image, ImageDraw


class Node:
    def __init__(self, vars):
        self.vars = vars
        self.init_reward = 0
        self.reward = 0
        self.children = set()
        self.parents = set()
        self.duplicate = 0
        self.simulation_count = 0
        self.init_time = 0
        self.sim_begin = 0
        self.sim_end = 0

    def __eq__(self, other):
        return self.vars == other.vars

    def __hash__(self):
        return hash(self.vars)

    def add_child(self, node):
        self.children.add(node)
        node.parents.add(self)

    def update_reward(self, reward):
        if self.simulation_count == 0:
            self.init_reward = reward
        self.reward = self.reward * self.simulation_count + reward
        self.simulation_count += 1
        self.reward /= self.simulation_count
        # if self.reward > 0:
        #     print(self.vars, self.reward)
        update_vals = {}
        for par in self.parents:
            update_vals[par] = 1
        queue = self.parents
        while len(queue) > 0:
            next_update_vals = {}
            next_queue = []
            for node in queue:
                # print('updating', node.vars, 'by', update_vals[node], 'times', reward)
                node.reward = node.reward * node.simulation_count + update_vals[node] * reward
                node.simulation_count += update_vals[node]
                node.reward /= node.simulation_count
                for par in node.parents:
                    if par not in next_update_vals:
                        next_update_vals[par] = 0
                        next_queue.append(par)
                    next_update_vals[par] += 1
            update_vals = next_update_vals
            queue = next_queue


class MinMaxColor:
    def __init__(self, min_value, max_value, min_color, max_color):
        self.min_value = min_value
        self.max_value = max_value
        self.min_color = min_color
        self.max_color = max_color

    def get_color(self, value):
        if self.min_value < self.max_value:
            intp_value = (value - self.min_value) / (self.max_value - self.min_value)
        else:
            intp_value = 0
        intp_color = [0] * len(self.min_color)
        for i in range(len(self.min_color)):
            intp_color[i] = int(self.min_color[i] + intp_value * (self.max_color[i] - self.min_color[i]))
        return tuple(intp_color)


def get_parents(existing_nodes, child_id):
    parents = []
    for var in child_id:
        parent_id = set(child_id)
        parent_id.remove(var)
        frozen_id = frozenset(parent_id)
        if frozen_id in existing_nodes:
            parents.append(existing_nodes[frozen_id])
    return parents


def construct_tree_from_log_file(location):
    print('reconstructing tree ..')
    id_pattern = re.compile(r'merged variables \{([\d\s]*)\}')
    reward_pattern = re.compile(r'Reward for this simulation: (\d+\.*\d*)')
    patterns = [
        re.compile(r't=(\d+\.*\d*)s \(Before recomputing FTS\)'),
        re.compile(r't=(\d+\.*\d*)s \(After recomputing FTS\)'),
        re.compile(r't=(\d+\.*\d*)s \(Time after simulation\)')
    ]
    root = Node(frozenset())
    existing_nodes = {frozenset([0]): root}
    min_reward = float('inf')
    max_reward = 0
    reward_match = False
    matches = [None] * len(patterns)
    max_depth = 0
    with open(location, 'r') as f:
        for line in f:
            if not reward_match:
                reward_match = reward_pattern.search(line)
                for i in range(len(patterns)):
                    match = patterns[i].search(line)
                    if match:
                        matches[i] = match
                        break
            else:
                id_match = id_pattern.search(line)
                if id_match:
                    ids = id_match.group(1).strip().split(' ')
                    id_set = set([])
                    for i in ids:
                        id_set.add(int(i))
                    frozen_id = frozenset(id_set)
                    if frozen_id not in existing_nodes:
                        reward = float(reward_match.group(1))
                        min_reward = min(min_reward, reward)
                        max_reward = max(max_reward, reward)
                        if len(frozen_id) == 2:
                            parents = [root]
                        else:
                            parents = get_parents(existing_nodes, frozen_id)
                        child = Node(frozen_id)
                        existing_nodes[frozen_id] = child
                        for par in parents:
                            par.add_child(child)
                        if reward > 1:
                            print(line, reward)
                            return

                        child.update_reward(reward)
                        child.init_time = float(matches[0].group(1))
                        child.sim_begin = float(matches[1].group(1))
                        child.sim_end = float(matches[2].group(1))
                        if len(frozen_id) - 1 > max_depth:
                            max_depth += 1
                            print('depth', max_depth, 'reached')
                    reward_match = False

    return root, min_reward, max_reward


def print_node(node, prefix=''):
    print(prefix + str(node.vars), str(node.reward), str(node.simulation_count))
    for child in node.children:
        print_node(child, prefix + ' ')


def visualize_reward_distribution(node, min_reward, max_reward, bin_count, max_y, no_sim, output_folder='./'):
    print('visualizing ...')
    node_at_depth = []
    queue = [(node, 0)]
    added_to_queue = set()
    added_to_queue.add(node.vars)
    while len(queue) != 0:
        next_queue = []
        for cur_node, depth in queue:
            if depth == len(node_at_depth):
                node_at_depth.append(set())
            node_at_depth[depth].add(cur_node)
            if len(cur_node.children) != 0:
                for child_i in cur_node.children:
                    if child_i.vars not in added_to_queue:
                        next_queue.append((child_i, depth + 1))
                        added_to_queue.add(child_i.vars)
        queue = next_queue

    for i in range(len(node_at_depth)):
        dat_file = output_folder + 'hist_at_' + str(i) + '.dat'
        dat = open(dat_file, 'w')
        dat.write('reward count simcount initcount\n')
        plt.clf()
        bin_size = (max_reward - min_reward) / bin_count
        bins = [min_reward + bin_size * i for i in range(bin_count)]
        n = [0] * bin_count
        n_init = [0] * bin_count
        for v in node_at_depth[i]:
            n[min(
                max(0, int(math.ceil((v.reward - min_reward) / bin_size))),
                bin_count - 1)] += 1
            n_init[min(
                max(0, int(math.ceil((v.init_reward - min_reward) / bin_size))),
                bin_count - 1)] += 1
        bin_size = bins[1] - bins[0]
        child_hist = [0] * bin_count
        if i > 0 and not no_sim:
            child_x = [bins[0] + i * bin_size for i in range(bin_count)]
            for nd in node_at_depth[i]:
                if bin_size == 0:
                    idx = 0
                else:
                    idx = min(
                        max(int(math.ceil(((nd.reward - bins[0]) / bin_size))), 0),
                        bin_count - 1)
                child_hist[idx] += nd.simulation_count
            plt.bar(child_x, child_hist, bin_size, color='yellow', alpha=1)
        for j in range(bin_count):
            dat.write("{:.6f} {:d} {:d} {:d}\n".format(bin_size * j, n[j], child_hist[j], n_init[j]))
        dat.write("{:.6f} {:d} {:d} {:d}".format(bin_size * bin_count, n[j], child_hist[j], n_init[j]))
        plt.bar(bins, n, bin_size, color='blue', alpha=0.5)
        plt.xlim([min_reward, max_reward])
        plt.ylim([0, max_y])
        plt.grid(True)
        plt.savefig(output_folder + 'hist_at_' + str(i) + '.png')
        dat.close()

    avg_reward_at = []
    avg_sim_at = []
    avg_init_at = []
    for depth in range(len(node_at_depth)):
        unsorted = []
        sum = 0
        sum_sim = 0
        sum_init = 0
        for node in node_at_depth[depth]:
            unsorted.append((len(node.children), node))
            sum += node.reward
            sum_sim += node.sim_end - node.init_time
            sum_init += node.sim_begin - node.init_time
        avg_reward_at.append((sum / len(node_at_depth[depth]), len(node_at_depth[depth])))
        avg_sim_at.append(sum_sim / len(node_at_depth[depth]))
        avg_init_at.append(sum_init / len(node_at_depth[depth]))
        unsorted = sorted(unsorted, key=lambda x: x[0])
        child_count_file = output_folder + 'children_at_' + str(depth) + '.child'
        with open(child_count_file, 'w') as f:
            for count, node in reversed(unsorted):
                f.write(str(count) + ';' + str(node.vars) + '\n')

    avg_reward_file = output_folder + 'avg_stats_per_depth.out'
    with open(avg_reward_file, 'w') as f:
        f.write('depth nodecount avgreward avgsim avginit\n')
        for i in range(len(avg_reward_at)):
            f.write("{:d} {:d} {:.6f} {:.6f} {:.6f}\n".format(i, avg_reward_at[i][1], avg_reward_at[i][0],
                                                              avg_sim_at[i], avg_init_at[i]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="file or folder containing the log data")
    parser.add_argument('output_folder', help="output folder to save the images", default='./')
    parser.add_argument('--min_reward', '-miny', help='minimum in x axis', default=0, type=float)
    parser.add_argument('--max_reward', '-maxx', help='maximum in x axis', default=1, type=float)
    parser.add_argument('--bin_count', '-bin', help='histogram bin count', default=50, type=int)
    parser.add_argument('--max_y', '-maxy', help='maximum in y axis', default=100, type=int)
    parser.add_argument('--no-sim', '-ns', help='do not draw the simulation', action='store_true', dest='no_sim')
    parser.set_defaults(no_sim=False)
    args = parser.parse_args()

    if os.path.isfile(args.input_file):
        input_files = [args.input_file]
    elif os.path.exists(args.input_file):
        input_files = get_file_list(args.input_file, ext='.log')
    if len(input_files) == 0:
        print(args.input_file, 'does not exist')
        return
    output_folder = args.output_folder
    if not output_folder.endswith('/'):
        output_folder += '/'
    for file in input_files:
        print('processing', file, '...')
        tree_root, min_reward, max_reward = construct_tree_from_log_file(file)
        # print_node(tree_root)
        if len(input_files) == 1:
            out = output_folder
        elif len(input_files) > 1:
            out = output_folder + '/' + file[len(args.input_file):] + '/'
        if not os.path.exists(out):
            os.makedirs(out)
        visualize_reward_distribution(tree_root, args.min_reward, args.max_reward, args.bin_count, args.max_y,
                                      args.no_sim,
                                      output_folder=out)


if __name__ == '__main__':
    main()
