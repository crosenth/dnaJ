#!/usr/bin/env python3
"""
"""
import argparse
import pandas

from Bio import SeqIO

ascending = {
    'is_type': False,
    'is_refseq': False,
    'length': False,
    'ambig_count': True,
    'modified_date': False}

DTYPES = {
    'accession': str,
    'ambig_count': int,
    'description': str,
    'download_date': str,
    'is_type': bool,
    'isolate': str,
    'isolation_source': str,
    'length': int,
    'modified_date': str,
    'mol_type': str,
    'name': str,
    'organism': str,
    'original': str,
    'seq_start': int,
    'seq_stop': int,
    'seqname': str,
    'source': str,
    'species': str,
    'strain': str,
    'tax_id': str,
    'version': str,
    'version_num': int,
    }


def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('seqs')
    p.add_argument('info')
    p.add_argument('seqs_out')
    p.add_argument('info_out')
    p.add_argument('--sort-by')
    args = p.parse_args()
    seq_info = pandas.read_csv(
        args.info,
        dtype=DTYPES,
        parse_dates=['download_date', 'modified_date'],
        date_parser=lambda x: pandas.datetime.strptime(x, '%d-%b-%Y'))
    columns = seq_info.columns
    seq_info['is_refseq'] = ~seq_info['original'].isnull()
    if args.sort_by:
        sort_by = args.sort_by.split(',')
        seq_info = seq_info.sort_values(
            by=sort_by, ascending=[ascending[i] for i in sort_by])
    # select top item
    seq_info = seq_info.groupby(
        by='species', as_index=False, sort=False, group_keys=False).first()
    seqnames = set(seq_info['seqname'].tolist())
    with open(args.seqs_out, 'w') as seqs_out:
        for s in SeqIO.parse(args.seqs, 'fasta'):
            if s.id in seqnames:
                seqs_out.write('>{}\n{}\n'.format(s.description, s.seq))
    seq_info.to_csv(args.info_out, index=False, columns=columns)


if __name__ == '__main__':
    main()
