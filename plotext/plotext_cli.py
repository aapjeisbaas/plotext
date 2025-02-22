#!/usr/bin/env python

import plotext as plt

import sys
import argparse
from collections import defaultdict


def _column(x):
    """Helper function to parse indexes of columns when doing and histogram plot

    This function is called after ArgumentParser has parsed the args
    """
    # we return a tuple of int, instead of an int for consistency on how we access columns
    # with other type of plots.
    return (int(x) - 1,)


def _split_columns(x):
    """Helper function to parse pair of indexes
    """
    try:
        a, b = map(int, x.split(","))
        # columns from command line are numbered starting from 1
        # but internally we start counting from 0
        return a - 1, b - 1
    except ValueError as ex:
        message = """ 
        Cannot understand the pair of columns you want to print.
        Columns are identified by numbers starting from 1. Each pair
        of columns is identified by two numbers separated by a comma
        without a space 1,2 1,5 6,4\n\n\n"""
        print(message, ex)
        raise ex


def _plot_size(x):
    try:
        a, b = map(int, x.split(","))
        return a, b
    except ValueError as ex:
        message = """ 
        Cannot understand the size of the plot. Please pass a pair of integers separated by a comma
        without a space: 100,30\n\n\n"""
        print(message, ex)
        raise ex


def _build_parser():
    """Define command line args
    """
    examples = """
    examples:


    # plot data from stdin
    $ cat data.txt | plotext scatter

    # plot data from a file
    $ plotext scatter -f data.txt

    # bar plot of second-first column
    $ cat data.txt | plotext bar --columns 2,1

    # linespoints of first-second and first-third column
    $ plotext linespoints -f data.txt --columns 1,2 1,3

    # histogram plot. columns are separated by ,
    $ plotext hist -f data.csv -d , -c 1 2

    """
    parser = argparse.ArgumentParser(
        prog="plotext",
        description="plots directly on the terminal",
        epilog=examples,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "plot", choices=["scatter", "bar", "line", "linespoints", "hist"]
    )

    parser.add_argument(
        "-f",
        "--file",
        help="Read data from FILE. If this flag is not used, plotext reads from stdin",
    )

    parser.add_argument(
        "-d",
        "--delimiter",
        help="Use DELIMITER instead of spaces for column separator",
        default=None,
    )

    parser.add_argument(
        "-c",
        "--columns",
        help="""Columns to plot. 
        For scatter, line, linespoints, and bar, they must be pairs separated by ',' without spaces 
        
        1,2 1,3 4,2.

        For histogram plots, list of columns 1 2 3. By default, the first two columns are used""",
        nargs="*",
        type=str,
        default=["1,2"],
    )

    parser.add_argument(
        "--bins", help="Number of bins for histogram plot", type=int, default=10
    )

    parser.add_argument("-s", "--size", help="Size of the plot", type=_plot_size)

    parser.add_argument("-xl", "--xlabel", help="Set x label", nargs="?")

    parser.add_argument("-yl", "--ylabel", help="Set y label", nargs="?")

    parser.add_argument("-t", "--title", help="Set plot title", nargs="?")

    parser.add_argument("-g", "--grid", help="Enable grid", action="store_true")

    return parser


def _parser_call_back(args):
    if args.plot == "hist":
        # histogram plots expect just a list of columns, not pairs
        args.columns = list(map(_column, args.columns))
    else:
        args.columns = list(map(_split_columns, args.columns))
    return args


def parse_args(argv):
    """Returns the namespace with all the command line args"""
    parser = _build_parser()
    args = parser.parse_args(argv)
    # post-process several args
    return _parser_call_back(args)


def _post_process_all_floats(columns, plot_type):
    """Convert all data read from file or stdin to float. 
    This function is invoked by get_data()"""
    for k, v in columns.items():
        try:
            columns[k] = list(map(float, v))
        except ValueError:
            print("All elements of a", plot_type, "plot must numbers.")
            print("Cannot convert elements of column", k + 1, "to float.\n\n")
            raise
    return columns


def _post_process_bar(columns, pairs):
    """Convert y-axis values into float. x-axis values are left str"""
    # in a bar plot, x-axis elements are left string
    # y elements, must be conveterd to float

    # get all y indexs
    idx = {i for _, i in pairs}

    for i in idx:
        try:
            columns[i] = list(map(float, columns[i]))
        except ValueError:
            print("In a bar plot, elements on the y-axis must be numbers.")
            print("Cannot convert elements of column", i + 1, "to float.\n\n")
            raise
    return columns


def _get_data_from(file_descriptor, args):
    """Read line from file_descriptor, which is a file or stdin. 

    Each line is plit according to the delimiter passed from command line. 

    Returns a dictionary with column-id:['list', 'of', 'values']"""

    # the user can pass several pairs of columns where one column is repeated
    # e.g., 1,2 1,3 1,4
    # therefore, we remove duplicates using a set
    idx = {i for t in args.columns for i in t}

    d = defaultdict(list)
    for line in file_descriptor:
        line = line.split(sep=args.delimiter)
        for i in idx:
            d[i].append(line[i])
    return d


def get_data(args):
    """returns dict{idx:[values]}. 

    Depending on the plot type selected, [values] may contain floats or strings
    """

    if args.file:
        with open(args.file) as f:
            columns = _get_data_from(f, args)
    else:
        columns = _get_data_from(sys.stdin, args)

    # here we basically convert x and/or y elements to float
    if args.plot == "bar":
        columns = _post_process_bar(columns, args.columns)
    else:
        columns = _post_process_all_floats(columns, args.plot)

    return columns


def _plot_properties(args):
    """Apply optional configurations to the plot"""
    if args.xlabel:
        plt.xlabel(args.xlabel)

    if args.ylabel:
        plt.ylabel(args.ylabel)

    if args.title:
        plt.title(args.title)

    if args.grid:
        plt.grid(True)

    if args.size:
        plt.plotsize(*args.size)


def plot(data, args):
    """Draw the plot."""

    for x in args.columns:
        if args.plot == "scatter":
            i, j = x
            plt.scatter(data[i], data[j])
        elif args.plot == "bar":
            i, j = x
            plt.bar(data[i], data[j])
        elif args.plot == "line":
            i, j = x
            plt.plot(data[i], data[j])
        elif args.plot == "linespoints":
            i, j = x
            plt.plot(data[i], data[j], marker=".")
            plt.scatter(data[i], data[j], marker="small")
        elif args.plot == "hist":
            i = x[0]
            plt.hist(data[i], bins=args.bins)

    _plot_properties(args)
    plt.show()


def main(argv=None):
    # parse command line args
    args = parse_args(argv)

    # get relevant data from stdin or file
    data = get_data(args)

    plot(data, args)


if __name__ == "__main__":
    sys.exit(main())
