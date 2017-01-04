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
        self.child_id = 0
        self.initial_reward = 0
        self.reward = 0
        self.children = []
        self.parents = []
        self.duplicate = 0
        self.simulation_count = 0

    def __eq__(self, other):
        return self.vars == other.vars

    def add_child(self, node):
        self.children.append(node)
        node.parents.append(self)

    def update_reward(self, reward):
        if self.simulation_count == 0:
            self.initial_reward = reward
        self.reward = self.reward * self.simulation_count + reward
        self.simulation_count += 1
        self.reward /= self.simulation_count
        for par in self.parents:
            par.update_reward(reward)


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
    id_pattern = re.compile(r'merged variables \{([\d\s]*)\}')
    reward_pattern = re.compile(r'Reward for this simulation: (\d+\.*\d*)')
    root = Node(set([]))
    existing_nodes = {frozenset([0]): root}
    min_reward = float('inf')
    max_reward = 0
    reward_match = False
    with open(location, 'r') as f:
        for line in f:
            if not reward_match:
                reward_match = reward_pattern.search(line)
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
                        child.update_reward(reward)
                    reward_match = False

    return root, min_reward, max_reward


def print_node(node, prefix=''):
    print(prefix + str(node.vars), str(node.reward), str(node.simulation_count))
    for child in node.children:
        print_node(child, prefix + ' ')


def visualize_node(node, min_reward, max_reward, scale=1, hist_bucket=0.1, output_folder='./'):
    reward_color = MinMaxColor(min_reward, max_reward, (0, 0, 255), (255, 0, 0))
    rows = []
    queue = [(node, 0, ())]
    while len(queue) != 0:
        next_queue = []
        for cur_node, depth, parent in queue:
            if depth == len(rows):
                rows.append([])
            rows[depth].append((cur_node, parent))
            if len(cur_node.children) != 0:
                next_queue.append((cur_node.children[0], depth + 1, (depth, len(rows[depth]) - 1)))
                for i in range(1, len(cur_node.children)):
                    next_queue.append((cur_node.children[i], depth + 1, ()))
        queue = next_queue

    width = 0
    row_padding = 100
    for i in range(len(rows)):
        width = max(len(rows[i]), width)

    im = Image.new('RGB', (scale * width, scale * (len(rows) * (row_padding + 1) - 1)), (255, 255, 255))

    draw = ImageDraw.Draw(im)
    for i in range(1, len(rows)):
        for j in range(len(rows[i])):
            cnode, parent = rows[i][j]
            color = reward_color.get_color(cnode.reward)
            x = scale * j
            y = scale * i * (row_padding + scale)
            draw.rectangle([x, y, x + scale, y + scale], color, color)
            if len(parent) != 0:
                pi, pj = parent
                px = scale * pj
                py = scale * pi * (row_padding + scale)
                draw.line([x, y - 1, px, py + 1], (0, 0, 0))
    del draw
    im.save(output_folder + 'out.png', 'PNG')

    for i in range(len(rows)):
        plt.clf()
        rewards = [v[0].reward for v in rows[i]]
        n, bins, patches = plt.hist(rewards, 50, facecolor='blue', alpha=0.75)
        plt.clf()
        unit = bins[1] - bins[0]
        if i > 0:
            child_hist = [0] * 50
            child_x = [bins[0] + i * unit for i in range(50)]
            for nd, pt in rows[i]:
                if unit == 0:
                    idx = 0
                else:
                    idx = min(int(math.floor(((nd.reward - bins[0]) / unit))), 49)
                child_hist[idx] += nd.simulation_count
            plt.bar(child_x, child_hist, unit, color='yellow', alpha=1)
        n, bins, patches = plt.hist(rewards, 50, facecolor='blue', alpha=0.5)
        plt.grid(True)
        plt.savefig(output_folder + 'hist_at_' + str(i) + '.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="file or folder containing the log data")
    parser.add_argument('output_folder', help="output folder to save the images", default='./')
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
        visualize_node(tree_root, min_reward, max_reward, 3, output_folder=out)


if __name__ == '__main__':
    main()
