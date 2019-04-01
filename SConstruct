"""
Download and curate the NCBI 16S rRNA sequences

TODO: download records updated before last download
"""
import configparser
import os
import sys

# requirements installed in the virtualenv
from SCons.Script import ARGUMENTS, Environment, Help, Variables

venv = os.environ.get('VIRTUAL_ENV')
if not venv:
    sys.exit('--> an active virtualenv is required'.format(venv))
if not os.path.exists('settings.conf'):
    sys.exit("Can't find settings.conf")
conf = configparser.SafeConfigParser()
conf.read('settings.conf')
settings = conf['settings']
vrs = Variables(None, ARGUMENTS)
vrs.Add('api_key', 'ncbi api_key for downloading data', settings['api_key'])
vrs.Add('email', 'email address for ncbi', settings['email'])
vrs.Add('nreq', ('Number of concurrent http requests to ncbi'), 8)
vrs.Add('out', default='output')
vrs.Add('retry', 'ncbi retry milliseconds', '60000')
vrs.Add('sort_by', 'sequence sorting', settings['sort_by'])

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
        '--bind $$(readlink -f $$(pwd)) '
        '--pwd $$(readlink -f $$(pwd)) '
        '{taxtastic} taxit'.format(**settings)),
    eutils=(
        '{singularity} exec '
        '--bind $$(readlink -f $$(pwd)) '
        '--pwd $$(readlink -f $$(pwd)) '
        '{eutils}'.format(**settings))
)

env.Decider('MD5-timestamp')

Help(vrs.GenerateHelpText(env))

if False:  # run_full_pipeline=True|False
    taxdb = env.Command(
        target='$out/taxonomy/ncbi_taxonomy.db',
        source=None,
        action='$taxit new_database sqlite:///$out')

    taxtable = env.Command(
        target='$out/taxonomy/taxtable.csv',
        source=taxdb,
        action=['$taxit get_descendants $SOURCE 543 '  # Enterobacteriaceae
                '| named.py --taxids /dev/stdin sqlite:///$SOURCE '
                '| $taxit taxtable '
                '--out $TARGET '
                '--tax-id-file '
                '/dev/stdin $SOURCE'])

    esearch = env.Command(
        target='$out/ncbi/accessions.txt',
        source=None,
        action=['$eutils esearch '
                '-db nucleotide '
                '-query "Enterobacteriaceae[Organism] AND dnaj[All Fields]" '
                '| mefetch -vv -api-key $api_key '
                '-email $email '
                '-format acc '
                '-log $out/ncbi.log '
                '-max-retry -1 '
                '-proc $nproc'])

    # TODO: incorporate ignore.txt

    feature_table = env.Command(
        target='$out/ncbi/feature_table.txt',
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
        target='$out/ncbi/coordinates.csv',
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
        target='$out/ncbi/records.gb',
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
    '''
    TODO: use time.date here
    '''
    ncbi_fa, ncbi_info, _, _, _ = env.Command(
        target=[
            '$out/ncbi/seqs.fasta',
            '$out/ncbi/info.csv',
            '$out/ncbi/pubmed_info.csv',
            '$out/ncbi/references.csv',
            '$out/ncbi/refseq_info.fasta'],
        source=genbank,
        action='extract_genbank.py $SOURCE 07-Mar-2019 $TARGETS')

    types = env.Command(
        target='$out/ncbi/types.txt',
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
else:
    ncbi_fa = '$out/ncbi/seqs.fasta'
    ncbi_info = '$out/ncbi/seq_info.csv'
    taxtable = '$out/taxtable.csv'
    types = '$out/ncbi/types.txt'

'''
drop duplicate records and refseq originals
'''
dedup_fa, dedup_info = env.Command(
    target=['$out/ncbi/dedup/seqs.fasta',
            '$out/ncbi/dedup/dedup.csv'],
    source=[ncbi_fa, ncbi_info],
    action='drop_duplicates.py $SOURCES $TARGETS')

'''
add is_type column
'''
is_type = env.Command(
    target='$out/ncbi/dedup/seq_info.csv',
    source=[dedup_info, types],
    action='is_type.py --out $TARGET $SOURCES')

'''
Select just species named rows.  Genus column is added
for selecting Escherichia and Shigella species later
'''
named_info = env.Command(
    target='$out/ncbi/dedup/named/seq_info.csv',
    source=[is_type, taxtable],
    action=['merge.py $SOURCES '
            '--how inner '  # only species named rows
            '--right-columns tax_id,species,genus '
            '--out $TARGET'])

named_fa = env.Command(
    target='$out/ncbi/dedup/named/seqs.fasta',
    source=[dedup_fa, named_info],
    action='partition_seqs.py --out $TARGET $SOURCES')

'''
get seqs for muscle alignment
'''
type_fa = env.Command(
    target='$out/profile/seqs.fasta',
    source=[named_info, dedup_fa],
    action=['csvgrep.py --columns is_type True ${SOURCES[0]} | '
            'partition_seqs.py --out $TARGET ${SOURCES[1]} /dev/stdin'])

'''
create muscle alignment
'''
muscle = env.Command(
    target='$out/profile/muscle.fasta',
    source=type_fa,
    action='muscle -in $SOURCE -out $TARGET')

'''
initial hmmer profile
'''
rough_profile = env.Command(
    target='$out/profile/rough.hmm',
    source=muscle,
    action='hmmbuild --dna --cpu 14 $TARGET $SOURCE')

'''
get type hits to first profile
'''
type_hits = env.Command(
    target='$out/profile/hmm_rough.tsv',
    source=[rough_profile, type_fa],
    action='hmmsearch --cpu 14 --tblout $TARGET $SOURCES > /dev/null')

'''
LR134137_3722540_3722971 is last seqname per muscle and type_hits
'''
hmmer_info = env.Command(
    target='$out/profile/filtered/seq_info.csv',
    source=[named_info, type_hits],
    action=['hmmer.py '
            '--last-in LR134137_3722540_3722971 '
            '--out $TARGET $SOURCES'])

'''
get seqs for new dnaj profile
'''
hmmer_seqs = env.Command(
    target='$out/profile/filtered/seqs.fasta',
    source=[type_fa, hmmer_info],
    action='partition_seqs.py --out $TARGET $SOURCES')

'''
make another msa file this time using hmmer
'''
hmmer_msa = env.Command(
    target='$out/profile/filtered/msa.fasta',
    source=[rough_profile, hmmer_seqs],
    action='hmmalign --outformat afa --dna -o $TARGET $SOURCES')

'''
dnaj hmmer final profile
'''
profile = env.Command(
    target='$out/profile/filtered/dnaj.hmm',
    source=hmmer_msa,
    action='hmmbuild --dna --cpu 14 $TARGET $SOURCE')

'''
make another msa file for --max-evalue decision
'''
env.Command(
    target='$out/types_msa.fasta',
    source=[profile, type_fa],
    action='hmmalign --outformat afa --dna -o $TARGET $SOURCES')

'''
hits against dnaj profile
'''
hits = env.Command(
    target='$out/hmmer.tsv',
    source=[profile, named_fa],
    action='hmmsearch --cpu 14 --tblout $TARGET $SOURCES > /dev/null')

'''
LR134137_3722540_3722971 is last type strain in profile model
'''
info = env.Command(
    target='$out/seq_info.csv',
    source=[named_info, hits],
    action=['hmmer.py '
            '--last-in LR134137_3722540_3722971 '
            '--out $TARGET $SOURCES'])

fa = env.Command(
    target='$out/seqs.fasta',
    source=[named_fa, info],
    action='partition_seqs.py --out $TARGET $SOURCES')

one_fa, species_info = env.Command(
    target=['$out/one/seqs.fasta', '$out/one/seq_info.csv'],
    source=[fa, info],
    action='extract_one.py --sort-by $sort_by $SOURCES $TARGETS')

'''
alignment
'''
one_msa = env.Command(
    target='$out/one/msa.fasta',
    source=[profile, one_fa],
    action='hmmalign --dna --outformat afa -o $TARGET $SOURCES')

'''
candidatus info
'''
candidatus_info = env.Command(
    target='$out/one/candidatus/seq_info.csv',
    source=species_info,
    action=['csvgrep.py '
            '--columns organism '
            '--ignore-case '
            '--out $TARGET '
            '"candidatus" $SOURCE'])

'''
candidatus info
'''
candidatus_fa = env.Command(
    target='$out/one/candidatus/seqs.fasta',
    source=[one_fa, candidatus_info],
    action='partition_seqs.py --out $TARGET $SOURCES')

'''
no candidatus info
'''
no_candidatus_info = env.Command(
    target='$out/one/no_candidatus/seq_info.csv',
    source=species_info,
    action=['csvgrep.py '
            '--columns organism '
            '--ignore-case '
            '--invert-match '
            '--out $TARGET '
            '"candidatus" $SOURCE'])

'''
no candidatus fa
'''
no_candidatus_fa = env.Command(
    target='$out/one/no_candidatus/seqs.fasta',
    source=[one_fa, no_candidatus_info],
    action='partition_seqs.py --out $TARGET $SOURCES')

'''
output all Escherichia (561) and Shigella (620) seqs into own dir
'''
genus_info = env.Command(
    target='$out/genus/seq_info.csv',
    source=info,
    action='csvgrep.py --out $TARGET --columns genus "561|620" $SOURCE')

genus_fa = env.Command(
    target='$out/genus/seqs.fasta',
    source=[fa, genus_info],
    action='partition_seqs.py --out $TARGET $SOURCES')
