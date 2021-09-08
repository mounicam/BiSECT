# System outputs

We provide the system outputs for our model and different baselines on the ``BiSECT`` and [``HSplit``](https://github.com/eliorsulem/HSplit-corpus) test sets. 

- ``copy512_bisect``: LSTM model trained on BiSECT dataset.
- ``copy512_wiki``: LSTM model trained on Wikisplit dataset.
- ``dissim``: [Rule based splitting](https://github.com/Lambda-3/DicourseSimplification)
- ``transformer_bisect``: [BERT-initialized transformer](https://github.com/mounicam/neural_splitter/) trained on BiSECT.
- ``transformer_wiki``: [BERT-initialized transformer](https://github.com/mounicam/neural_splitter/) trained on Wikisplit.
- ``ourmodel_bisect``: Our model trained on BiSECT.
- ``ourmodel_bisect_wikisplit``: Our model trained on BiSECT and Wikisplit.

For all the outputs, the split sentences are separated by a ``<SEP>`` token.
