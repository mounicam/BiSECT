#!/usr/bin/env bash


RAW_DATA_PATH=$1 # Raw data path.
DATA_BIN=$2 # Binarized data path

# We take bert-base-cased checkpoint here. Vocab file belongs to the same checkpoint with [FILL] as one of the unused tokens

for split in train test valid
do
    echo $split

    echo "Extracting rules."
    mkdir -p $RAW_DATA_PATH/rules
    python3 preprocess/classifier/classifier.py -r $RAW_DATA_PATH/${split}.dst -c $RAW_DATA_PATH/${split}.src \
    -o $RAW_DATA_PATH/rules/${split}.tsv

    echo "Tokenizing data with padding."
    mkdir -p $RAW_DATA_PATH/wp
    python3 preprocess/tokenize/get_padded_data.py -i $RAW_DATA_PATH/rules/${split}.tsv -o $RAW_DATA_PATH/wp/${split}.aner -v preprocess/tokenize/vocab.txt

done

echo "Binarizing data."
ANON_DATA_PATH=$RAW_DATA_PATH/wp
/usr/bin/python3 preprocess.py --workers 5 --source-lang src --target-lang dst \
      --trainpref $ANON_DATA_PATH/train.aner --validpref $ANON_DATA_PATH/valid.aner --testpref $ANON_DATA_PATH/test.aner \
      --destdir  $DATA_BIN --padding-factor 1 --joined-dictionary --srcdict preprocess/tokenize/vocab_count.txt
cp $ANON_DATA_PATH/*.labels $DATA_BIN/.
