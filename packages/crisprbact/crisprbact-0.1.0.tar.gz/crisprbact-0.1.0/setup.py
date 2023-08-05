# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['crisprbact']

package_data = \
{'': ['*']}

install_requires = \
['biopython>=1.75,<2.0', 'click>=7.0,<8.0', 'numpy>=1.17,<2.0']

entry_points = \
{'console_scripts': ['crisprbact = crisprbact.cli:main']}

setup_kwargs = {
    'name': 'crisprbact',
    'version': '0.1.0',
    'description': 'Tools to design and analyse CRISPRi experiments',
    'long_description': '# CRISPRbact\n\n**Tools to design and analyse CRISPRi experiments in bacteria.**\n\nCRISPRbact currently contains an on-target activity prediction tool for the Streptococcus pyogenes dCas9 protein.\nThis tool takes as an input the sequence of a gene of interest and returns a list of possible target sequences with the predicted on-target activity. Predictions are made using a linear model fitted on data from a genome-wide CRISPRi screen performed in E. coli (Cui et al. Nature Communications, 2018). The model predicts the ability of dCas9 to block the RNA polymerase when targeting the non-template strand (i.e. the coding strand) of a target gene.\n\n## Getting Started\n\n### Installation\n\nFor the moment, you can install this package only via PyPI\n\n#### PyPI\n\n```console\n$ pip install crisprbact\n$ crisprbact --help\n```\n\n```\nUsage: crisprbact [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  -v, --verbose\n  --help         Show this message and exit.\n\nCommands:\n  predict\n```\n\n### API\n\nUsing this library in your python code.\n\n```python\nfrom crisprbact import on_target_predict\n\nguide_rnas = on_target_predict("ACCACTGGCGTGCGCGTTACTCATCAGATGCTGTTCAATACCGATCAGGTTATCGAAGTGTTTGTGATTGTTTGCCGCGCGCGTGGCGAAGGCCCGTGATGAAGGAAAAGTTTTGCGCTATGTTGGCAATATTGATGAAG")\n\nfor guide_rna in guide_rnas:\n    print(guide_rna)\n\n```\n\n_output :_\n\n```\n{\'target\': \'TCATCACGGGCCTTCGCCACGCGCG\', \'guide\': \'TCATCACGGGCCTTCGCCAC\', \'start\': 82, \'stop\': 102, \'pam\': 80, \'ori\': \'-\', \'pred\': -0.4719254873780802}\n{\'target\': \'CATCACGGGCCTTCGCCACGCGCGC\', \'guide\': \'CATCACGGGCCTTCGCCACG\', \'start\': 81, \'stop\': 101, \'pam\': 79, \'ori\': \'-\', \'pred\': 1.0491308060379676}\n{\'target\': \'CGCGCGCGGCAAACAATCACAAACA\', \'guide\': \'CGCGCGCGGCAAACAATCAC\', \'start\': 63, \'stop\': 83, \'pam\': 61, \'ori\': \'-\', \'pred\': -0.9021152826078697}\n{\'target\': \'CCTGATCGGTATTGAACAGCATCTG\', \'guide\': \'CCTGATCGGTATTGAACAGC\', \'start\': 29, \'stop\': 49, \'pam\': 27, \'ori\': \'-\', \'pred\': 0.23853258873311955}\n```\n\n### Command line interface\n\n#### Predict guide RNAs activity\n\nInput the sequence of a target gene and this script will output candidate guide RNAs for the S. pyogenes dCas9 with predicted on-target activity.\n\n```console\n$ crisprbact predict --help\n```\n\n```\nUsage: crisprbact predict [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  from-seq  Outputs candidate guide RNAs for the S.\n  from-str  Outputs candidate guide RNAs for the S.\n```\n\n##### From a string sequence:\n\nThe target input sequence can be a simple string.\n\n```console\n$ crisprbact predict from-str --help\n```\n\n```\nUsage: crisprbact predict from-str [OPTIONS] [OUTPUT_FILE]\n\n  Outputs candidate guide RNAs for the S. pyogenes dCas9 with predicted on-\n  target activity from a target gene.\n\n  [OUTPUT_FILE] file where the candidate guide RNAs are saved. Default =\n  "stdout"\n\nOptions:\n  -t, --target TEXT  [required]\n  --help             Show this message and exit.\n```\n\n```console\n$ crisprbact predict from-str -t ACCACTGGCGTGCGCGTTACTCATCAGATGCTGTTCAATACCGATCAGGTTATCGAAGTGTTTGTGATTGTTTGCCGCGCGCGTGGCGAAGGCCCGTGATGAAGGAAAAGTTTTGCGCTATGTTGGCAATATTGATGAAG guide-rnas.tsv\n```\n\noutput file `guide-rnas.tsv` :\n\nNo `seq_id` is defined since it is from a simple string.\n\n```\ntarget\tPAM position\tprediction\tseq_id\nTCATCACGGGCCTTCGCCACGCGCG\t80\t-0.4719254873780802\tN/A\nCATCACGGGCCTTCGCCACGCGCGC\t79\t1.0491308060379676\tN/A\nCGCGCGCGGCAAACAATCACAAACA\t61\t-0.9021152826078697\tN/A\nCCTGATCGGTATTGAACAGCATCTG\t27\t0.23853258873311955\tN/A\n```\n\nYou can also pipe the results :\n\n```console\n$ crisprbact predict from-str -t ACCACTGGCGTGCGCGTTACTCATCAGATGCTGTTCAATACCGATCAGGTTATCGAAGTGTTTGTGATTGTTTGCCGCGCGCGTGGCGAAGGCCCGTGATGAAGGAAAAGTTTTGCGCTATGTTGGCAATATTGATGAAG | tail -n +2 | wc -l\n```\n\n##### From a sequence file\n\n```console\n$ crisprbact predict from-seq --help\n```\n\n```\nUsage: crisprbact predict from-seq [OPTIONS] [OUTPUT_FILE]\n\n  Outputs candidate guide RNAs for the S. pyogenes dCas9 with predicted on-\n  target activity from a target gene.\n\n  [OUTPUT_FILE] file where the candidate guide RNAs are saved. Default =\n  "stdout"\n\nOptions:\n  -t, --target FILENAME           Sequence file  [required]\n  -f, --seq-format [fasta|fa|gb|genbank]\n                                  Sequence file format  [default: fasta]\n  --help                          Show this message and exit.\n```\n\n- Fasta file (could be a multifasta file)\n\n```console\n$ crisprbact predict from-seq -t /tmp/seq.fasta guide-rnas.tsv\n```\n\n- GenBank file\n\n```console\n$ crisprbact predict from-seq -t /tmp/seq.gb -f gb guide-rnas.tsv\n```\n\n##### Output file\n\n```\ntarget\tPAM position\tprediction\tinput_id\nATTTGTTGGCAACCCAGCCAGCCTT\t855\t-0.7310112260341689\tCP027060.1\nCACGTCCGGCAATATTTCCGCGAAC\t830\t0.14773859036983505\tCP027060.1\nTCCGAGCGGCAACGTCTCTGATAAC\t799\t-0.4922487382950619\tCP027060.1\nGCTTAAAGGGCAAAATGTCACGCCT\t769\t-1.814666749464254\tCP027060.1\nCTTAAAGGGCAAAATGTCACGCCTT\t768\t-0.4285147731290152\tCP027060.1\nCGTTTGAGGAGATCCACAAAATTAT\t732\t-1.2437430146548256\tCP027060.1\nCATGAATGGTATAAACCGGCGTGCC\t680\t-0.8043242669169294\tCP027060.1\n\n```\n\n## Contributing\n\n### Clone repo\n\n```console\n$ git clone https://gitlab.pasteur.fr/dbikard/crisprbact.git\n```\n\n### Create a virtualenv\n\n```console\n$ virtualenv -p python3.7 .venv\n$ . .venv/bin/activate\n$ pip install poetry\n```\n\n### Install crisprbact dependencies\n\n```console\n$ poetry install\n```\n\n### Install hooks\n\nIn order to run flake8 and black for each commit.\n\n```console\n$ pre-commit install\n```\n',
    'author': 'David Bikard',
    'author_email': 'david.bikard@pasteur.fr',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://gitlab.pasteur.fr/dbikard/crisprbact',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
