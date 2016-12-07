import os
import matplotlib.pyplot as plt
import argparse

from matplotlib.legend_handler import HandlerLine2D
from matplotlib.font_manager import FontProperties
from common import read_json_file


def get_graph_data_per_problem(grouped_data, attr_x, attr_y):
    print('Getting cumulative data per problem ...')

    # processing data
    graph_data = {}
    for domain, problems in grouped_data.items():
        graph_data[domain] = {}
        for problem, algos in problems.items():
            graph_data[domain][problem] = {}
            for algo, val_list in algos.items():
                graph_data[domain][problem][algo] = {'x': [], 'y': []}
                for val in val_list:
                    if attr_x in val and attr_y in val and val[attr_x] is not None and val[attr_y] is not None:
                        graph_data[domain][problem][algo]['x'].append(val[attr_x])
                        graph_data[domain][problem][algo]['y'].append(val[attr_y])
    return graph_data


def create_dirs_if_necessary(graph_data, OUTDIR):
    for domain, problems in graph_data.items():
        if not os.path.exists(OUTDIR + '/' + domain):
            os.makedirs(OUTDIR + '/' + domain)


def create_graph_from_plot_data(graph_data, OUTDIR, attr_x, attr_y, xlog, ylog):
    print('Creating graphs ...')

    # plotting
    fontP = FontProperties()
    fontP.set_size('small')

    colors = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
    color_idx = 0

    for domain, problems in graph_data.items():
        for problem, algos in problems.items():
            print('Creating graph for ' + domain + ' ' + problem)
            fig = plt.figure()
            subplt = fig.add_subplot(111)
            subplt.set_xlabel(attr_x)
            subplt.set_ylabel(attr_y)
            for algo, xy_data in algos.items():
                if len(xy_data['x']) > 0:
                    if algo == 'base_unsat':
                        subplt.scatter(xy_data['x'], xy_data['y'], label=algo, linewidth=2, c=colors[color_idx])
                    else:
                        subplt.scatter(xy_data['x'], xy_data['y'], label=algo, c=colors[color_idx])
                    color_idx = (color_idx + 1) % len(colors)
                    subplt.grid(b=True, which='major', color='gray', linestyle='-')
                    subplt.minorticks_on()
                    subplt.grid(b=True, which='minor', color='gray')
                    subplt.margins(0.05)
                    if xlog:
                        subplt.set_xscale('log')
                    else:
                        subplt.set_xscale('linear')
                        subplt.get_xaxis().get_major_formatter().set_useOffset(False)
                        subplt.get_xaxis().get_major_formatter().set_scientific(False)
                        if len(str(xy_data['x'][0])) > 5:
                            plt.setp(subplt.get_xticklabels(), rotation=30, horizontalalignment='right')
                    if ylog:
                        subplt.set_yscale('log')
                    else:
                        subplt.set_yscale('linear')
                        subplt.get_yaxis().get_major_formatter().set_useOffset(False)
                        subplt.get_yaxis().get_major_formatter().set_scientific(False)
                    subplt.margins(0.05)
            plt.legend(handler_map={subplt: HandlerLine2D(numpoints=1)}, prop=fontP, loc='upper left')
            plt.savefig(OUTDIR + '/' + domain + '/' + problem + '.png')
            plt.close()
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
    parser.add_argument("--attribute-x", "-ax", help="attribute to use in x axis", default="max_abstraction_states")
    parser.add_argument("--attribute-y", "-ay", help="attribute to use in y axis", default="computation_time")
    parser.add_argument("--unsolvable-only", "-u", help="only count the unsolvable instances", dest='unsolvable_only',
                        action='store_true')
    parser.add_argument("--log-x", "-lx", help='use log scaling on x axis', dest='log_x', action='store_true')
    parser.add_argument("--log-y", "-ly", help='use log scaling on y axis', dest='log_y', action='store_true')
    parser.add_argument("--filter", "-f", help="filter the intersection domains and problems only", dest='filter',
                        action='store_true')
    # parser.add_argument("--latex", "-ltx", help="print the data in latex", dest='latex',
    # action='store_true')
    # parser.add_argument('--order', '-ord',
    # help='space separated string, the order of the algorithm column shown in the table',
    # type=str)
    # parser.set_defaults(log=False, unsolvable_only=False, latex=False)
    parser.set_defaults(log_x=False, log_y=False, unsolvable_only=False)
    args = parser.parse_args()
    # if args.order is not None:
    #   args.order = args.order.split(' ')

    data, problems = read_json_file(args.json_file, args.filter, args.unsolvable_only)
    if not check_attribute_exists(data, args.attribute_x):
        print('Attribute', args.attribute_x, 'does not exist')
        return
    if not check_attribute_exists(data, args.attribute_y):
        print('Attribute', args.attribute_y, 'does not exist')
        return
    create_dirs_if_necessary(data, args.outfolder)
    data = get_graph_data_per_problem(data, args.attribute_x, args.attribute_y)
    create_graph_from_plot_data(data, args.outfolder, args.attribute_x, args.attribute_y, args.log_x, args.log_y)


if __name__ == '__main__':
    main()
