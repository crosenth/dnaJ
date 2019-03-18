#!/usr/bin/env python

import pandas
import re
import sys
import argparse


def get_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pattern', help="The name of the run")
    parser.add_argument('file', help="The dir corresponding to the run")
    parser.add_argument(
        '--columns',
        metavar='COLS',
        help='Comma delimited list of column names or indices if --no-header')
    parser.add_argument(
        '-v', '--invert-match',
        action='store_true',
        help='Invert the sense of matching, to select non-matching lines.')
    parser.add_argument(
        '-i', '--ignore-case',
        action='store_true',
        help=('Ignore case distinctions in both '
              'the PATTERN and the input files.'))
    parser.add_argument(
        '--out', type=argparse.FileType('w'), default=sys.stdout)
    return parser.parse_args()


def main():
    args = get_args()
    if args.columns:
        columns = args.columns.split(',')
    else:
        columns = args.csv.columns.tolist()
    df = pandas.read_csv(args.file, dtype=str, na_filter=False)
    if args.ignore_case:
        pattern = re.compile(args.pattern, re.IGNORECASE)
    else:
        pattern = re.compile(args.pattern)

    def search(string):
        return bool(re.search(pattern, string))

    if args.invert_match:
        df = df[~df[columns].apply(lambda x: x.map(search).any(), axis=1)]
    else:
        df = df[df[columns].apply(lambda x: x.map(search).any(), axis=1)]
    df.to_csv(args.out, index=False)


if __name__ == '__main__':
    sys.exit(main())
