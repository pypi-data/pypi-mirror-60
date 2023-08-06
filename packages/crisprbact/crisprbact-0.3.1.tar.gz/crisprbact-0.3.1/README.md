# CRISPRbact

**Tools to design and analyse CRISPRi experiments in bacteria.**

CRISPRbact currently contains an on-target activity prediction tool for the Streptococcus pyogenes dCas9 protein.
This tool takes as an input the sequence of a gene of interest and returns a list of possible target sequences with the predicted on-target activity. Predictions are made using a linear model fitted on data from a genome-wide CRISPRi screen performed in E. coli (Cui et al. Nature Communications, 2018). The model predicts the ability of dCas9 to block the RNA polymerase when targeting the non-template strand (i.e. the coding strand) of a target gene.

## Getting Started

### Installation

For the moment, you can install this package only via PyPI

#### PyPI

```console
$ pip install crisprbact
$ crisprbact --help
```

```
Usage: crisprbact [OPTIONS] COMMAND [ARGS]...

Options:
  -v, --verbose
  --help         Show this message and exit.

Commands:
  predict
```

### API

Using this library in your python code.

```python
from crisprbact import on_target_predict

guide_rnas = on_target_predict("ACCACTGGCGTGCGCGTTACTCATCAGATGCTGTTCAATACCGATCAGGTTATCGAAGTGTTTGTGATTGTTTGCCGCGCGCGTGGCGAAGGCCCGTGATGAAGGAAAAGTTTTGCGCTATGTTGGCAATATTGATGAAG")

for guide_rna in guide_rnas:
    print(guide_rna)

```

_output :_

```
{'target': 'TCATCACGGGCCTTCGCCACGCGCG', 'guide': 'TCATCACGGGCCTTCGCCAC', 'start': 82, 'stop': 102, 'pam': 80, 'ori': '-', 'pred': -0.4719254873780802}
{'target': 'CATCACGGGCCTTCGCCACGCGCGC', 'guide': 'CATCACGGGCCTTCGCCACG', 'start': 81, 'stop': 101, 'pam': 79, 'ori': '-', 'pred': 1.0491308060379676}
{'target': 'CGCGCGCGGCAAACAATCACAAACA', 'guide': 'CGCGCGCGGCAAACAATCAC', 'start': 63, 'stop': 83, 'pam': 61, 'ori': '-', 'pred': -0.9021152826078697}
{'target': 'CCTGATCGGTATTGAACAGCATCTG', 'guide': 'CCTGATCGGTATTGAACAGC', 'start': 29, 'stop': 49, 'pam': 27, 'ori': '-', 'pred': 0.23853258873311955}
```

### Command line interface

#### Predict guide RNAs activity

Input the sequence of a target gene and this script will output candidate guide RNAs for the S. pyogenes dCas9 with predicted on-target activity.

```console
$ crisprbact predict --help
```

```
Usage: crisprbact predict [OPTIONS] COMMAND [ARGS]...

Options:
  --help  Show this message and exit.

Commands:
  from-seq  Outputs candidate guide RNAs for the S.
  from-str  Outputs candidate guide RNAs for the S.
```

##### From a string sequence:

The target input sequence can be a simple string.

```console
$ crisprbact predict from-str --help
```

```
Usage: crisprbact predict from-str [OPTIONS] [OUTPUT_FILE]

  Outputs candidate guide RNAs for the S. pyogenes dCas9 with predicted on-
  target activity from a target gene.

  [OUTPUT_FILE] file where the candidate guide RNAs are saved. Default =
  "stdout"

Options:
  -t, --target TEXT  [required]
  --help             Show this message and exit.
```

```console
$ crisprbact predict from-str -t ACCACTGGCGTGCGCGTTACTCATCAGATGCTGTTCAATACCGATCAGGTTATCGAAGTGTTTGTGATTGTTTGCCGCGCGCGTGGCGAAGGCCCGTGATGAAGGAAAAGTTTTGCGCTATGTTGGCAATATTGATGAAG guide-rnas.tsv
```

output file `guide-rnas.tsv` :

No `seq_id` is defined since it is from a simple string.

```
target	PAM position	prediction	seq_id
TCATCACGGGCCTTCGCCACGCGCG	80	-0.4719254873780802	N/A
CATCACGGGCCTTCGCCACGCGCGC	79	1.0491308060379676	N/A
CGCGCGCGGCAAACAATCACAAACA	61	-0.9021152826078697	N/A
CCTGATCGGTATTGAACAGCATCTG	27	0.23853258873311955	N/A
```

You can also pipe the results :

```console
$ crisprbact predict from-str -t ACCACTGGCGTGCGCGTTACTCATCAGATGCTGTTCAATACCGATCAGGTTATCGAAGTGTTTGTGATTGTTTGCCGCGCGCGTGGCGAAGGCCCGTGATGAAGGAAAAGTTTTGCGCTATGTTGGCAATATTGATGAAG | tail -n +2 | wc -l
```

##### From a sequence file

```console
$ crisprbact predict from-seq --help
```

```
Usage: crisprbact predict from-seq [OPTIONS] [OUTPUT_FILE]

  Outputs candidate guide RNAs for the S. pyogenes dCas9 with predicted on-
  target activity from a target gene.

  [OUTPUT_FILE] file where the candidate guide RNAs are saved. Default =
  "stdout"

Options:
  -t, --target FILENAME           Sequence file  [required]
  -f, --seq-format [fasta|fa|gb|genbank]
                                  Sequence file format  [default: fasta]
  --help                          Show this message and exit.
```

- Fasta file (could be a multifasta file)

```console
$ crisprbact predict from-seq -t /tmp/seq.fasta guide-rnas.tsv
```

- GenBank file

```console
$ crisprbact predict from-seq -t /tmp/seq.gb -f gb guide-rnas.tsv
```

##### Output file

```
target	PAM position	prediction	input_id
ATTTGTTGGCAACCCAGCCAGCCTT	855	-0.7310112260341689	CP027060.1
CACGTCCGGCAATATTTCCGCGAAC	830	0.14773859036983505	CP027060.1
TCCGAGCGGCAACGTCTCTGATAAC	799	-0.4922487382950619	CP027060.1
GCTTAAAGGGCAAAATGTCACGCCT	769	-1.814666749464254	CP027060.1
CTTAAAGGGCAAAATGTCACGCCTT	768	-0.4285147731290152	CP027060.1
CGTTTGAGGAGATCCACAAAATTAT	732	-1.2437430146548256	CP027060.1
CATGAATGGTATAAACCGGCGTGCC	680	-0.8043242669169294	CP027060.1

```

## Contributing

### Clone repo

```console
$ git clone https://gitlab.pasteur.fr/dbikard/crisprbact.git
```

### Create a virtualenv

```console
$ virtualenv -p python3.7 .venv
$ . .venv/bin/activate
$ pip install poetry
```

### Install crisprbact dependencies

```console
$ poetry install
```

### Install hooks

In order to run flake8 and black for each commit.

```console
$ pre-commit install
```
