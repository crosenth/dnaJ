#!/usr/bin/env python3
"""
"""
import argparse
import csv
import sys

from Bio import SeqIO


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('fasta')
    p.add_argument('info')
    p.add_argument('--out', default=sys.stdout, type=argparse.FileType('w'))
    args = p.parse_args()
    seqnames = set(i['seqname'] for i in csv.DictReader(open(args.info)))
    for s in SeqIO.parse(args.fasta, 'fasta'):
        if s.id in seqnames:
            args.out.write('>{}\n{}\n'.format(s.description, s.seq))


if __name__ == '__main__':
    main()
