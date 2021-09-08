#!/usr/bin/env bash

DATA_BIN=$1 # Binarized data directory
CP=$2 # Checkpoint path
OUTPUT=$3 # Output file path
RAW_SRC=$4 # Source file path


python3 generate.py $DATA_BIN --path $CP --min-len-a 0.0 --min-len-b 0 --max-len-a 5.0 --no-repeat-ngram-size 3 --max-len-b 0 --batch-size 32 --beam 10 --nbest 1 --user-dir my_model --print-alignment --gen-subset test > $OUTPUT.aner

python3 postprocess/postprocess.py  --input $OUTPUT.aner --output $OUTPUT --src $RAW_SRC

rm $OUTPUT.aner

