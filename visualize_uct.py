#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import numpy as np
import re

from PIL import Image, ImageDraw


class Node:
    def __init__(self, vars, reward):
        self.vars = vars
        self.child_id = 0
        self.reward = reward
        self.last_reward = reward
        self.children = []

    def __eq__(self, other):
        return self.vars == other.vars

    def add_child(self, node):
        if not self.vars.issubset(node.vars):
            return False
        elif self == node:
            self.last_reward = node.reward
            return True
        added = False
        for child in self.children:
            added = added or child.add_child(node)
        if not added:
            node.child_id = len(self.children)
            self.children.append(node)
            return True
        return True


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


def construct_tree_from_log_file(location):
    id_pattern = re.compile(r'merged variables \{([\d\s]*)\}')
    reward_pattern = re.compile(r'reward (\d+\.*\d*)')
    root = Node(set([]), 0)
    min_reward = float('inf')
    max_reward = 0
    with open(location, 'r') as f:
        for line in f:
            match = id_pattern.search(line)
            if match:
                ids = match.group(1).strip().split(' ')
                id_set = set([])
                for i in ids:
                    id_set.add(int(i))
                match = reward_pattern.search(line)
                reward = float(match.group(1))
                min_reward = min(min_reward, reward)
                max_reward = max(max_reward, reward)
                root.add_child(Node(id_set, reward))
    return root, min_reward, max_reward


def print_node(node, prefix=''):
    print(prefix + str(node.vars), str(node.reward), str(node.last_reward))
    for child in node.children:
        print_node(child, prefix + ' ')


def visualize_node(node, min_reward, max_reward, scale=1, hist_bucket=0.1):
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
    im.save('out.png', 'PNG')

    for i in range(len(rows)):
        plt.clf()
        rewards = [v[0].reward for v in rows[i]]
        n, bins, patches = plt.hist(rewards, 50, facecolor='green', alpha=0.75)
        unit = bins[1] - bins[0]
        if i > 0:
            child_hist = [0] * 51
            child_x = [bins[0] + i * unit + 0.5 * unit for i in range(51)]
            for nd, pt in rows[i]:
                child_hist[int((nd.reward - bins[0]) / unit)] += len(nd.children)
            plt.plot(child_x, child_hist, 'red')
        plt.grid(True)
        plt.savefig('hist_at_' + str(i) + '.png')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", help="file containing the log data")
    # parser.add_argument("--unsolvable-only", "-u", help="only count the unsolvable instances", dest='unsolvable_only',
    #                    action='store_true')
    # parser.set_defaults(unsolvable_only=False)

    args = parser.parse_args()
    tree_root, min_reward, max_reward = construct_tree_from_log_file(args.input_file)
    # print_node(tree_root)
    visualize_node(tree_root, min_reward, max_reward, 3)


if __name__ == '__main__':
    main()
