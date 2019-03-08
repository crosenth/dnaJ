#!/usr/bin/env python3
"""
output all valid tax_ids in database
"""

import argparse
import configparser
import sqlalchemy
import sys


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument(
        'url',
        help='Database string URI or filename.')
    p.add_argument(
        '--taxids',
        default=sys.stdin,
        type=argparse.FileType('r'),
        help='file of taxids')
    p.add_argument(
        '--out',
        default=sys.stdout,
        type=argparse.FileType('w'),
        help='list of all version downloaded')
    args = p.parse_args()
    conf = configparser.SafeConfigParser(allow_no_value=True)
    conf.optionxform = str  # options are case-sensitive
    engine = sqlalchemy.create_engine(args.url)
    conn = engine.connect()
    meta = sqlalchemy.MetaData(engine, reflect=True)
    nodes = meta.tables['nodes']
    s = sqlalchemy.select([nodes.c.tax_id]).where(sqlalchemy.and_(
        nodes.c.is_valid, nodes.c.rank != 'no_rank'))
    result = conn.execute(s)
    if args.taxids:
        taxids = [i.strip() for i in args.taxids]
        taxids = set(i for i in taxids if i)
        result = (r for r in result if r[0] in taxids)
    for i in result:
        args.out.write(i[0] + '\n')


if __name__ == '__main__':
    main()
