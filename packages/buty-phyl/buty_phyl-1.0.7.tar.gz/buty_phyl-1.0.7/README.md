# buty_phyl
## Introduction
* buty_phyl infers traits by 16S
* input: otu table (-t) and otu sequences (-s)
* requirement: mafft
* Optional: fasttree
![alt text](https://raw.githubusercontent.com/caozhichongchong/buty_phyl/master/Methodology.png)

## Install
`pip install buty_phyl`\
in preparation: `anaconda download caozhichongchong/buty_phyl`

## Availability
in preparation: https://anaconda.org/caozhichongchong/buty_phyl

https://pypi.org/project/buty_phyl

## How to use it
1. test the buty_phyl\
`buty_phyl --test`

2. try your data\
`buty_phyl -t your.otu.table -s your.otu.seqs`\
`buty_phyl -t your.otu.table -s your.otu.seqs -top 2000`

3. try different traits (default is butyrate production)\
predicting butyrate production\
`buty_phyl -t your.otu.table -s your.otu.seqs`\
or\
`buty_phyl -t your.otu.table -s your.otu.seqs --rt b`\
predicting sulfate reduction\
`buty_phyl -t your.otu.table -s your.otu.seqs --rt s`\
predicting nitrate reduction\
`buty_phyl -t your.otu.table -s your.otu.seqs --rt n`

4. use your own traits\
`buty_phyl -t your.otu.table -s your.otu.seqs --rs your.own.reference.16s --rt your.own.reference.traits`

* your.own.reference.16s is a fasta file containing the 16S sequences of your genomes\
\>Genome_ID1\
ATGC...\
\>Genome_ID2\
ATGC...

* your.own.reference.traits is a metadata of whether there's trait in your genomes (0 for no and 1 for yes)\
Genome_ID1   0\
Genome_ID1   1

## Results
The result dir of "Bayers_model":
* `filename.infertraits.txt`: the OTUs inferring as butyrate-producing bacteria (1.0), unknown bacteria (0.5), 
and non-butyrate-producing bacteria (0.0).
* `filename.infertraits.abu`: the total abundance of butyrate-producing bacteria.
* `filename.infertraits.commensal.abu`: the total abundance of commensal butyrate-producing bacteria.
* `filename.infertraits.pathogen.abu`: the total abundance of pathogenic butyrate-producing bacteria.
* `filename.infertraits.otu_table`: the otu_table of butyrate-producing bacteria.
* `filename.infertraits.commensal.otu_table`: the otu_table of commensal butyrate-producing bacteria.
* `filename.infertraits.pathogen.otu_table`: the otu_table of pathogenic butyrate-producing bacteria.
* `filename.bpbspecies.commensal.abu`: the abundance of commensal butyrate-producing species.
* `filename.bpbspecies.pathogen.abu`: the abundance of pathogenic butyrate-producing species.

The result dir of "Filtered_OTU":
* Some temp files of filtered OTUs, alignment, and tree.

## Copyright
Copyright: An Ni Zhang, Prof. Eric Alm, Alm Lab in MIT\
Citation: Not yet, coming soon!\
Contact: anniz44@mit.edu
