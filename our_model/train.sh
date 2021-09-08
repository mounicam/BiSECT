#!/usr/bin/env bash


DATA_BIN=$1
CP=$2
BERT_PATH=$3

/usr/bin/python3  train.py $DATA_BIN -a bert_rand --max-update 150000   \
    --fp16 --lr 0.0001 --optimizer adam --save-dir $CP --user-dir my_model --batch-size 16 --update-freq 6 \
    --lr-scheduler inverse_sqrt --warmup-updates 40000 --max-source-positions 512 --max-target-positions 512 \
    --bert-path $BERT_PATH
