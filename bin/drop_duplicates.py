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
    p.add_argument(
        'fasta_out', default=sys.stdout, type=argparse.FileType('w'))
    p.add_argument(
        'info_out', default=sys.stdout, type=argparse.FileType('w'))
    args = p.parse_args()
    info_csv = csv.DictReader(open(args.info))
    info = {r['seqname']: r for r in info_csv}
    originals = set(r['original'] for r in info.values())
    info = {k: v for k, v in info.items() if v['accession'] not in originals}
    info_out = csv.DictWriter(args.info_out, fieldnames=info_csv.fieldnames)
    info_out.writeheader()
    for s in SeqIO.parse(args.fasta, 'fasta'):
        if s.id in info:
            args.fasta_out.write('>{}\n{}\n'.format(s.description, s.seq))
            info_out.writerow(info[s.id])
            del info[s.id]  # drop any duplicate


if __name__ == '__main__':
    main()
