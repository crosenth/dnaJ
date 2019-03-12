"""
Download and curate the NCBI 16S rRNA sequences

TODO: download records updated before last download
"""
import configparser
import errno
import os
import sys
import time

# requirements installed in the virtualenv
from SCons.Script import ARGUMENTS, Depends, Environment, Help, Variables

venv = os.environ.get('VIRTUAL_ENV')
if not venv:
    sys.exit('--> an active virtualenv is required'.format(venv))
if not os.path.exists('settings.conf'):
    sys.exit("Can't find settings.conf")
conf = configparser.SafeConfigParser()
conf.read('settings.conf')
settings = conf['settings']


def blast_db(env, sequence_file, output_base):
    '''
    Create a blast database and file md5sum
    '''
    extensions = ['.nhr', '.nin', '.nsq']
    blast_out = env.Command(
        target=[output_base + ext for ext in extensions],
        source=sequence_file,
        action='makeblastdb -dbtype nucl -in $SOURCE -out ' + output_base)
    env.Command(
        target=output_base,
        source=blast_out,
        action='md5sum $SOURCES > $TARGET')
    return blast_out


vrs = Variables(None, ARGUMENTS)
vrs.Add('api_key', 'ncbi api_key for downloading data', settings['api_key'])
vrs.Add('email', 'email address for ncbi', settings['email'])
vrs.Add('nreq', ('Number of concurrent http requests to ncbi'), 8)
vrs.Add('out', default=os.path.join('$base', time.strftime('%Y%m%d')))
vrs.Add('retry', 'ncbi retry milliseconds', '60000')
vrs.Add('sort_by', 'sequence sorting', settings['sort_by'])
vrs.Add('tax_url', default=settings['taxonomy'], help='database url')
# cache vars

environment_variables = dict(
    os.environ,
    PATH=':'.join([
        'bin',
        os.path.join(venv, 'bin'),
        '/usr/local/bin',
        '/usr/bin',
        '/bin']),
)

env = Environment(
    ENV=environment_variables,
    variables=vrs,
    shell='bash',
    taxit=(
        '{singularity} exec '
        '--bind {taxonomy} '
        '--bind {trusted_taxids} '
        '--bind $$(readlink -f $$(pwd)) '
        '--pwd $$(readlink -f $$(pwd)) '
        '{taxtastic} taxit'.format(**settings)),
    deenurp=(
        '{singularity} exec '
        '--bind $$(readlink -f $$(pwd)) '
        '--pwd $$(readlink -f $$(pwd)) '
        '{deenurp} deenurp'.format(**settings)),
    eutils=(
        '{singularity} exec '
        '--bind $$(readlink -f $$(pwd)) '
        '--pwd $$(readlink -f $$(pwd)) '
        '{eutils}'.format(**settings))
)

env.Decider('MD5-timestamp')

Help(vrs.GenerateHelpText(env))

esearch = env.Command(
    target='output/raw/records.txt',
    source=None,
    action=['$eutils esearch '
            '-db nucleotide '
            '-query "Enterobacteriaceae[Organism] AND dnaj[All Fields]" '
            '| mefetch -vv -api-key $api_key '
            '-email $email '
            '-format acc '
            '-log output/ncbi.log '
            '-max-retry -1 '
            '-proc $nproc'])

feature_table = env.Command(
    target='$out/raw/feature_table.txt',
    source=esearch,
    action=['mefetch -vv '
            '-api-key $api_key '
            '-db nucleotide '
            '-email $email '
            '-format ft '
            '-id $SOURCE '
            '-log $out/ncbi.log '
            '-max-retry -1 '
            '-mode text '
            '-out $TARGET '
            '-proc $nproc '
            '-retmax 1 '
            '-retry $retry'])

coordinates = env.Command(
    target='$out/raw/coordinates.csv',
    source=feature_table,
    action=('ftract '
            '-feature gene:gene:"dnaj" '
            '-feature CDS:product:"molecular chaperone DnaJ" '
            '-feature CDS:product:"chaperone protein DnaJ" '
            '-feature CDS:product:"DnaJ protein" '
            '-feature CDS:product:"DnaJ domain-containing protein" '
            '-feature CDS:product:"dnaJ domain protein" '
            '-feature CDS:product:"chaperone dnaJ" '
            '-feature CDS:product:"DnaJ" '
            '-feature CDS:product:"dnaJ central domain protein" '
            '--full-format '
            '--out $TARGET '
            '$SOURCE'))

genbank = env.Command(
    target='$out/raw/records.gb',
    source=coordinates,
    action=('mefetch -vv '
            '-id $SOURCE '
            '-api-key $api_key '
            '-csv '
            '-db nucleotide '
            '-email $email '
            '-format gbwithparts '
            '-log $out/ncbi.log '
            '-max-retry -1 '
            '-mode text '
            '-out $TARGET'
            '-proc $nproc '
            '-retmax 1 '
            '-retry $retry'))

raw_fa, raw_info, _, _, _ = env.Command(
    target=[
        '$out/raw/seqs.fasta',
        '$out/raw/info.csv',
        '$out/raw/pubmed_info.csv',
        '$out/raw/references.csv',
        '$out/raw/refseq_info.fasta'],
    source=genbank,
    action='extract_genbank.py $SOURCE 07-Mar-2019 $TARGETS')

types = env.Command(
    target='$out/raw/types.txt',
    source=None,
    action=['$eutils esearch '
            '-db nucleotide '
            '-query "Enterobacteriaceae[Organism] AND '
            'dnaj[All Fields] AND sequence_from_type[Filter]" '
            '| mefetch -vv -api-key $api_key '
            '-email $email '
            '-format acc '
            '-log $out/ncbi.log '
            '-max-retry -1 '
            '-proc $nproc'])

ncbi = env.Command(
    target='$out/taxonomy/ncbi_taxonomy.db',
    source=None,
    action='taxit new_database sqlite:///$out')

taxtable = env.Command(
    target='$out/taxonomy/taxtable.csv',
    source=ncbi,
    action=('$taxit get_descendants $SOURCE 543 '  # Enterobacteriaceae
            '| named.py --taxids /dev/stdin sqlite:///$SOURCE '
            '| $taxit taxtable --out $TARGET --tax-id-file /dev/stdin $SOURCE'
            ))

annotated = env.Command(
    target='$out/raw/annotated/seq_info.csv',
    source=[raw_info, types, taxtable],
    action=['is_type.py ${SOURCES[:2]} | '
            'merge.py /dev/stdin ${SOURCE[2]} '
            '--right-columns tax_id,species '
            '--out $TARGET'])

'''
deduplicates seq_info and extracts cooresponding sequences
'''
fa, info = env.Command(
    target=['$out/seqs.fasta', '$out/seq_info.csv'],
    source=[raw_fa, annotated],
    action='partition_refs.py $SOURCES $TARGETS')
