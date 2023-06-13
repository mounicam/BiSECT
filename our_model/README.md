# Introduction

This directory consists of the code for our hybrid sentence splitter. 


# Requirements and Installation

The code is based on [fairseq](https://github.com/pytorch/fairseq) toolkit. It requires PyTorch version >= 1.0.0 and 
Python version >= 3.5. 

If you do not have PyTorch, please follow the instructions here to install: https://github.com/pytorch/pytorch#installation.

And then install fairseq from the source code shared in the repository.
```
pip install --editable .
```

# Pre-trained models

You can perform generation with one of models using the following command.
 
```
sh generate.sh <input file> <output file> <checkpoint path>
```

Download the checkpoints from [here](https://drive.google.com/drive/u/0/folders/1cI7jK7sq3flLarcTe9PXVRXZqcwuDeSz).

# Training 

1. Follow the step 1 described in the above section for Transformer.


2. Download the BERT-base checkpoint from [here](https://storage.googleapis.com/bert_models/2018_10_18/cased_L-12_H-768_A-12.zip) 
and unzip the folder.  Then, train using the following command:

```
CUDA_VISIBLE_DEVICES=<GPU1,GPU2...> python3  train.py <binarized data path from previous step> --save-dir <checkpoint directory>  \
    --lr 0.0001 --optimizer adam  -a bert_rand --max-update 100000 --user-dir my_model --batch-size 32 --fp16 \
    --lr-scheduler inverse_sqrt --warmup-updates 40000 --max-source-positions 512 --max-target-positions 512 \
    --bert-path cased_L-12_H-768_A-12/bert_model.ckpt
```

All the model parameters are specified in ``my_model/__init__.py`` file.

3. Follow the step 2 described in the previous section.  You can generate using the best checkpoint according to the cross-entropy loss, i.e. ``checkpoint_best.pt`` in the specified checkpoint directory. Alternatively, you can also choose the best checkpoint according to the SARI score on the validation dataset.

# Citation

If you use any of these resources, please cite fairseq and our paper:

```bibtex
@inproceedings{bisect2021,
  title={BiSECT: Learning to Split and Rephrase Sentences with Bitexts},
  author={Kim, Joongwon and Maddela, Mounica and Kriz, Reno Kriz and Xu, Wei and Callison-Burch, Chris},
  booktitle={Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year={2021}
}
```


```bibtex
@inproceedings{ott2019fairseq,
  title = {fairseq: A Fast, Extensible Toolkit for Sequence Modeling},
  author = {Myle Ott and Sergey Edunov and Alexei Baevski and Angela Fan and Sam Gross and Nathan Ng and David Grangier and Michael Auli},
  booktitle = {Proceedings of NAACL-HLT 2019: Demonstrations},
  year = {2019},
}
```
