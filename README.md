## Basic description of pipeline

1. Esearch query for list of accession numbers that may contain DnaJ features.  An example query could be ``esearch -db nucleotide -query "Enterobacteriaceae[Organism] AND dnaj[All Fields]"``
1. Download the feature table for each accession.  A feature table contains *just* the feature annotations for each sequence.  The sequence itself is *not* included in a feature table. https://www.ncbi.nlm.nih.gov/WebSub/html/help/feature-table.html
1. Pattern match the feature tables for DnaJ annotations and parse out the sequence coordinates. An example of the pattern matching utility looks like ``ftract -feature "gene:gene:dnaj" -log ncbi.log -out dnaj.csv`` or ``ftract -feature "cds:product:dnaj" -log ncbi.log -out dnaj.csv``
1. Download Genbank records using DnaJ feature coordinates.  An example ``mefetch -mode text -strand 1 -db nucleotide -id CP015085.1 -format gbwithparts -seq_stop 3777659-seq_start 3778819``
1. Parse genbank record into sequences.fasta and seq_info.csv files.
1. Perform any sequence filtering.
1. Build search/blast database.
