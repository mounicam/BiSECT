# Automatic evaluation

We looked at the following evaluation metrics for the task:
- SARI along with add, keep, and delete scores.
- FKGL
- BLEU score with the reference.
- BLEU score with the source (to capture system conservatism).
- Average % of new words (to capture system conservatism).
- Average sentence length.
- Average output length.
- Average BERTScore.


## Modified SARI:
We implemented an extended version of SARI that considers lexical paraphrases of the reference. 
An n-gram from the output is considered correct if the given n-gram or its paraphrase from PPDB occurs in the reference, 
using the PPDB-XL version. Without this change, the original SARI tends to underestimate rephrasing.

The PPDB file can be downloaded [here](https://drive.google.com/drive/folders/104EG4oy5BTe_ddioOKnilaZOyguQ_xvt). Please make sure you have the file in the metrics folder before running the metrics code.


## Instructions: 
You can calculate the metrics using the command below:

```python3 metrics/metrics.py -r <reference file> -c <complex sentence file> -s <system output> -ppdb metrics/ppdb_xl.tsv```
    
Here, ``<reference file>`` assumes that the references are seperated by a tab. 

Note that we do not include BERTScore as it is available [here](https://github.com/Tiiiger/bert_score). 
We used bert-base-uncased model to calculate the semantic similarity between the output and the reference.

