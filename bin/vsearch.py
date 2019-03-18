#!/usr/bin/env python3
"""
"""
import argparse
import csv


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('aligns')
    p.add_argument('info')
    p.add_argument('info_out')
    args = p.parse_args()
    aligns = csv.DictReader(
        open(args.aligns),
        delimiter='\t',
        fieldnames=['query', 'target', 'qstrand', 'id', 'tilo', 'tihi'])
    keep = set(a['query'] for a in aligns)
    info = csv.DictReader(open(args.info))
    with open(args.info_out, 'w') as out:
        info_out = csv.DictWriter(out, fieldnames=info.fieldnames)
        info_out.writeheader()
        for i in info:
            if i['seqname'] in keep:
                info_out.writerow(i)


if __name__ == '__main__':
    main()
