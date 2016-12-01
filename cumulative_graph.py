import json
import re
import os
import matplotlib.pyplot as plt
import argparse

from matplotlib.legend_handler import HandlerLine2D
from matplotlib.font_manager import FontProperties
from common import read_json_file


def create_cumulative_graph(grouped_data, OUTDIR, ATTR):
    print('Processing data ...')

    # processing data
    graph_data = {}
    for domain, problems in grouped_data.items():
        graph_data[domain] = {}
        for problem, algos in problems.items():
            graph_data[domain][problem] = {}
            unsorted = []
            for algo, val_list in algos.items():
                for val in val_list:
                    unsorted.append((val[ATTR], algo, 0))
            sorted_data = sorted(unsorted, key=lambda pair: pair[0])
            for algo in algos:
                graph_data[domain][problem][algo] = {'x': [], 'y': []}
            i = len(sorted_data) - 1
            while i >= 0:
                j = i - 1
                while j >= 0:
                    if sorted_data[j][0] != sorted_data[i][0]:
                        break
                    j -= 1
                for k in range(j + 1, i + 1):
                    sorted_data[k] = (sorted_data[k][0], sorted_data[k][1], i + 1)
                i = j
            for (x, algo, y) in sorted_data:
                graph_data[domain][problem][algo]['x'].append(x)
                graph_data[domain][problem][algo]['y'].append(y)

    print('Creating graphs ...')

    # plotting
    fontP = FontProperties()
    fontP.set_size('small')

    for domain, problems in graph_data.items():
        if not os.path.exists(OUTDIR + '/' + domain):
            os.makedirs(OUTDIR + '/' + domain)
        for problem, algos in problems.items():
            fig = plt.figure()
            subplt = fig.add_subplot(111)
            subplt.set_xlabel(ATTR)
            subplt.set_ylabel('Cumulative count')
            for algo, xy_data in algos.items():
                x = xy_data['x']
                y = xy_data['y']
                x = [x[0]] + x
                y = [0] + y
                if algo == 'base_unsat':
                    subplt.plot(x, y, label=algo, linewidth=2)
                else:
                    subplt.plot(x, y, label=algo)
                if len(str(x[0])) > 5:
                    plt.setp(subplt.get_xticklabels(), rotation=30, horizontalalignment='right')
                subplt.grid(b=True, which='major', color='gray', linestyle='-')
                subplt.minorticks_on()
                subplt.grid(b=True, which='minor', color='gray')
                subplt.get_xaxis().get_major_formatter().set_useOffset(False)
                subplt.get_xaxis().get_major_formatter().set_scientific(False)
                subplt.margins(0.05)
            plt.legend(handler_map={subplt: HandlerLine2D(numpoints=1)}, prop=fontP, loc='upper left')
            plt.savefig(OUTDIR + '/' + domain + '/' + problem + '.png')
            plt.close()
            print('Created graph for ' + domain + ' ' + problem)
    return


def get_cumulative_data_per_problem(grouped_data, ATTR):
    print('Getting cumulative data per problem ...')

    # processing data
    max_y = 0
    cumu_data = {}
    for domain, problems in grouped_data.items():
        cumu_data[domain] = {}
        for problem, algos in problems.items():
            cumu_data[domain][problem] = {}
            for algo, val_list in algos.items():
                unsorted = []
                for val in val_list:
                    if ATTR in val:
                        unsorted.append(val[ATTR])
                if len(unsorted) > 0:
                    sorted_data = sorted(unsorted)
                    cumu = 1
                    cumu_data[domain][problem][algo] = {'x': [sorted_data[0]], 'y': [cumu]}
                    for x in sorted_data:
                        if cumu_data[domain][problem][algo]['x'][-1] == x:
                            cumu_data[domain][problem][algo]['y'][-1] = cumu
                        else:
                            cumu_data[domain][problem][algo]['x'].append(x)
                            cumu_data[domain][problem][algo]['y'].append(cumu)
                        cumu += 1
                    max_y = max(cumu, max_y)
    return cumu_data, max_y


def get_plot_data_from_cumu(cumu_data, max_y):
    graph_data = {}
    for domain, problems in cumu_data.items():
        graph_data[domain] = {}
        for problem, algos in problems.items():
            graph_data[domain][problem] = {}
            for algo, xy_data in algos.items():
                x = xy_data['x']
                y = xy_data['y']
                x = [x[0]] + x
                y = [0] + y
                if algo == 'base_unsat':
                    y[len(y) - 1] = max_y
                graph_data[domain][problem][algo] = {'x': x, 'y': y}
    return graph_data


def create_dirs_if_necessary(graph_data, OUTDIR):
    for domain, problems in graph_data.items():
        if not os.path.exists(OUTDIR + '/' + domain):
            os.makedirs(OUTDIR + '/' + domain)


def create_cumulative_graph_from_plot_data(graph_data, OUTDIR, ATTR, xlog_scale):
    print('Creating graphs ...')

    # plotting
    fontP = FontProperties()
    fontP.set_size('small')

    for domain, problems in graph_data.items():
        for problem, algos in problems.items():
            fig = plt.figure()
            subplt = fig.add_subplot(111)
            subplt.set_xlabel(ATTR)
            subplt.set_ylabel('Cumulative count')
            for algo, xy_data in algos.items():
                if algo == 'base_unsat':
                    subplt.plot(xy_data['x'], xy_data['y'], label=algo, linestyle='--', linewidth=2)
                else:
                    subplt.plot(xy_data['x'], xy_data['y'], label=algo)
                subplt.grid(b=True, which='major', color='gray', linestyle='-')
                subplt.minorticks_on()
                subplt.grid(b=True, which='minor', color='gray')
                subplt.margins(0.05)
                if xlog_scale:
                    subplt.set_xscale('log')
                else:
                    subplt.set_xscale('linear')
                    subplt.get_xaxis().get_major_formatter().set_useOffset(False)
                    subplt.get_xaxis().get_major_formatter().set_scientific(False)
                    if len(str(xy_data['x'][0])) > 5:
                        plt.setp(subplt.get_xticklabels(), rotation=30, horizontalalignment='right')
                subplt.margins(0.05)
            plt.legend(handler_map={subplt: HandlerLine2D(numpoints=1)}, prop=fontP, loc='upper left')
            plt.savefig(OUTDIR + '/' + domain + '/' + problem + '.png')
            plt.close()
            print('Created graph for ' + domain + ' ' + problem)
    return


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


def print_plot_data(graph_data, algo_order):
    for domain in sorted(graph_data.keys()):
        problems = graph_data[domain]
        for problem in sorted(problems.keys()):
            algos = problems[problem]
            print()
            print(domain, problem)
            if algo_order is None:
                algo_order = []
                for algo in algos:
                    algo_order.append(algo)
            for algo in algo_order:
                if algo not in algos:
                    continue
                xy_data = algos[algo]
                s = algo + ':'
                for i in range(len(xy_data['x'])):
                    if isinstance(xy_data['x'][i], float):
                        s += ' ({:.2f}, '.format(xy_data['x'][i])
                    else:
                        s += ' ({:d}, '.format(xy_data['x'][i])
                    if isinstance(xy_data['y'][i], float):
                        s += ' {:.2f})'.format(xy_data['y'][i])
                    else:
                        s += ' {:d})'.format(xy_data['y'][i])
                print(s)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("json_file", help=".json file containing the lab data")
    parser.add_argument("--outfolder", "-o", help="output folder", default="output")
    parser.add_argument("--attribute", "-a", help="attribute to use", default="max_abstraction_states")
    parser.add_argument("--unsolvable-only", "-u", help="only count the unsolvable instances", dest='unsolvable_only',
                        action='store_true')
    parser.add_argument("--log", "-l", help='use log scaling on x axis', dest='log', action='store_true')
    parser.add_argument("--filter", "-f", help="filter the intersection domains and problems only", dest='filter',
                        action='store_true')
    parser.add_argument("--latex", "-ltx", help="print the data in latex", dest='latex',
                        action='store_true')
    parser.add_argument('--order', '-ord',
                        help='space separated string, the order of the algorithm column shown in the table',
                        type=str)
    parser.set_defaults(log=False, unsolvable_only=False, latex=False)
    args = parser.parse_args()
    if args.order is not None:
        args.order = args.order.split(' ')

    data, problems = read_json_file(args.json_file, args.filter, args.unsolvable_only)
    if check_attribute_exists(data, args.attribute):
        data, max_y = get_cumulative_data_per_problem(data, args.attribute)
        data = get_plot_data_from_cumu(data, max_y)
        create_dirs_if_necessary(data, args.outfolder)
        create_cumulative_graph_from_plot_data(data, args.outfolder, args.attribute, args.log)
        if args.latex:
            print_plot_data(data, args.order)


if __name__ == '__main__':
    main()
