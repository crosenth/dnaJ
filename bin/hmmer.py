#!/usr/bin/env python3
"""
Add is_type column based on presence in type strain file
"""
import argparse
import csv
import sys


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('info')
    p.add_argument('hmmer')
    p.add_argument('--max-evalue', type=float)
    p.add_argument(
        '--out',
        type=argparse.FileType('w'),
        default=sys.stdout)
    args = p.parse_args()
    hmmer = (l.split()[:8] for l in open(args.hmmer) if not l.startswith('#'))
    fieldnames = ['target name', 'accession', 'query name',
                  'accession', 'evalue', 'score', 'bias']
    hmmer = (dict(zip(fieldnames, h)) for h in hmmer)
    if args.max_evalue:
        hmmer = (h for h in hmmer if float(h['evalue']) <= args.max_evalue)
    seqnames = set(h['target name'] for h in hmmer)
    info_csv = csv.DictReader(open(args.info))
    info = (i for i in info_csv if i['seqname'] in seqnames)
    writer = csv.DictWriter(args.out, fieldnames=info_csv.fieldnames)
    writer.writeheader()
    writer.writerows(info)


if __name__ == '__main__':
    main()
