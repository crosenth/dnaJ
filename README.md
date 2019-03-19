# DnaJ pipeline

**By**: S Salipante, N Hoffman and C Rosenthal

Chaperone DnaJ, also known as Hsp40 (heat shock protein 40 kD), 
is a molecular chaperone protein. It is expressed in a wide 
variety of organisms from bacteria to humans.

**Question** - Can we use the DnaJ dna region to help speciate organisms in the Enterobacteriaceae family
and Escherichia and Shigella genera?

## Description of pipeline steps and decision process

Here is an example of the kinds of Genbank records and 
annotations we are looking for in our pipeline

![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/73dc7e818d3cb6822916966dc8553af4/Screenshot_from_2019-03-01_09-46-16.png)
![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/e096c7eb7dff6c6d417d9fd5a05a9fe7/Screenshot_from_2019-03-05_10-48-39.png)

The first step is to construct an NCBI Esearch query for a
list of accession numbers that may contain DnaJ features:

``esearch -db nucleotide -query "Enterobacteriaceae[Organism] AND dnaj[All Fields]"``

Which gives us 136,547 potential dnaJ records.  The next step is to download 
the feature tables for all 136,547 records:

``mefetch -db nucleotide -format ft -out feature_tables.txt``

Besides the first example we looked at there may be many different ways dnaJ is annotated.
To get an idea of what other kinds of annotations may correspond 
to the dnaJ region we can do something like this on the feature_tables.txt file:

``grep -i 'dnaj' feature_table.txt | sort | uniq -c | sort -nr``

![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/c11f9c0ea3f9788b7039d0852d454644/Screen_Shot_2019-03-07_at_11.12.36_AM.png)

Based on those counts we can parse coordinates from the following string patterns:

1. product molecular chaperone DnaJ
1. gene dnaJ
1. product chaperone protein DnaJ
1. product DnaJ protein
1. product DnaJ domain-containing protein
1. product dnaJ domain protein
1. product chaperone dnaJ
1. product DnaJ
1. product dnaJ central domain protein

To parse the coordinates we can use ftract:

``ftract --full-format 
-feature gene:gene:"dnaj" 
-feature CDS:product:"molecular chaperone DnaJ"  
-feature CDS:product:"chaperone protein DnaJ" 
-feature CDS:product:"DnaJ protein" 
-feature CDS:product:"DnaJ domain-containing protein" 
-feature CDS:product:"dnaJ domain protein" 
-feature CDS:product:"chaperone dnaJ" 
-feature CDS:product:"DnaJ" 
-feature CDS:product:"dnaJ central domain protein" 
feature_table.txt``

Once we have each of these coordinates parsed let's do a quick record count:

![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/3f86406ef68d2b49f571ba4b25d69eea/Screenshot_from_2019-03-20_10-09-57.png)

Now we can download each dnaJ sequence by accession and coordinates:

``mefetch -csv -id coordinates.csv -db nucleotide -format gbwithparts -out records.gb``

This is a big file.  The next steps involve converting the genbank records into a fasta 
file (seqs.fasta) and an annotations file (seq_info.csv).

After a deduplication step and selecting for named taxonomic records we end 
up with a total of 40,169 potential dnaJ records.

The next step is build an alignment profile to test sequence quality.
For this process the first step is to select downloaded records that 
are designated type strain material.

"Type strain material is the taxonomic device that ties formal names to the 
physical specimens that serve as exemplars for the species. For the prokaryotes 
these are strains submitted to the culture collections; for the eukaryotes they 
are specimens submitted to museums or herbaria." - https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4383940/

And build a multiple alignment using muscle.

``muscle -in seqs.fasta -out muscle.fasta``

![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/f9b9bf84b5c107ff5768cd3d5cef13de/Screenshot_from_2019-03-19_16-44-16.png)

After creating the multiple alignment we can create a rough alignment profile using hmmer.

``hmmbuild --dna rough.hmm muscle.fasta``

Next we can search those same type strain sequences against the rough/type strain alignment profile:

``hmmsearch -tblout hmmer.tsv rough.hmm seqs.fasta``

It seems a little circular but what that does is allow me to side by side look 
at the muscle alignment and some alignment metrics and choose sequences
that I like and sequences that I do not like. 

![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/79ab340e073127d3da107b5847391d16/Screenshot_from_2019-03-19_16-24-17.png)
![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/44aac6868e5e56709d7e140c85f15932/Screenshot_from_2019-03-19_16-24-48.png)
![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/308790119bf160872e5d11f5c13cf289/Screenshot_from_2019-03-19_16-25-20.png)
![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/070fe031725e92df656313055eb3530d/Screenshot_from_2019-03-19_16-25-56.png)
![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/eb5722f892ad44965fa65b76eabc7b85/Screenshot_from_2019-03-19_16-26-36.png)

And from there I can choose record ``LR134137_3722540_3722971`` as my last accepted dnaJ sequence.
With that knowledge I can filter the type strains against the ordered hmmsearch results:

``hmmer.py --last-in LR134137_3722540_3722971 seq_info.csv hmm_rough.tsv``

And build another, higher confidence hmmer profile to filter the rest of the sequences:

``hmmbuild --dna dnaj.hmm filtered.fasta``

From there I can go thru the same hmmsearch and filter steps and go from 
40,169 sequences to 25,450 high confidence sequences.  From there a dnaJ alignment
looks something like this:

![](https://gitlab.labmed.uw.edu/molmicro/dnaj/uploads/f41b15eee180d126b19663fc4ee7ec19/Screenshot_from_2019-03-19_16-42-01.png)

**TODO**: Figure out what is going on with the 14,719 dropped seqs. Any suggestions?

**TODO**: Turn this into our own NCBI dnaJ in-house reference database.
