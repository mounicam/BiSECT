# BiSECT

This repository contains the code and resources from [our paper](https://arxiv.org/abs/2109.05006).

## Repo Structure: 
1. ```bisect```: BiSECT dataset of complex-simple pairs.

2. ```metrics```: Automatic evaluation metrics for the task that we used in our work.

3. ```our_model```: Code for our hybrid splitter model. Further details to train or generate output from the pretrained models are available in a README file in the folder.

4. ```outputs```: System outputs.

5. ```experiments```: code for running human evaluation as well as MTurk output files

Each folder contains a README with further details.

For the BERT-intialized Transformer baseline, you can refer to [this repo](https://github.com/mounicam/neural_splitter). All the pretrained models are available [here](https://drive.google.com/drive/u/0/folders/104EG4oy5BTe_ddioOKnilaZOyguQ_xvt).


## Citation
Please cite if you use the above resources for your research
```
@inproceedings{bisect2021,
  title={BiSECT: Learning to Split and Rephrase Sentences with Bitexts},
  author={Kim, Joongwon and Maddela, Mounica and Kriz, Reno and Xu, Wei and Callison-Burch, Chris},
  booktitle={Proceedings of the Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year={2021}
}
```
