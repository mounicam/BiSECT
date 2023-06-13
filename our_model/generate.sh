#!/usr/bin/env bash


INPUT_FILE=$1
OUTPUT_FILE=$2
CP=$3

rm -rf /tmp/bisect/
mkdir -p /tmp/bisect/

python3 preprocess/anonymize_wordpiece.py --input $INPUT_FILE --vocab preprocess/vocab.txt \
 --output  /tmp/bisect/test.aner.src
cp /tmp/bisect/test.aner.src /tmp/bisect/test.aner.dst
cp /tmp/bisect/test.aner.src /tmp/bisect/train.aner.src
cp /tmp/bisect/test.aner.src /tmp/bisect/train.aner.dst

python3 preprocess.py --workers 5 --source-lang src --target-lang dst \
 --testpref /tmp/bisect/test.aner  --trainpref /tmp/bisect/train.aner \
  --destdir  /tmp/bisect/data-bin --padding-factor 1 --joined-dictionary --srcdict preprocess/vocab_count.txt

python3 generate.py /tmp/bisect/data-bin --path $CP --min-len-a 0.0 --min-len-b 0 \
  --max-len-a 5.0 --no-repeat-ngram-size 3 --max-len-b 0 --batch-size 32 --beam 10 --nbest 1 \
  --user-dir my_model --print-alignment --gen-subset test > $OUTPUT_FILE.aner

python3 postprocess/postprocess.py  --input $OUTPUT_FILE.aner --output $OUTPUT_FILE --src $INPUT_FILE

rm $OUTPUT_FILE.aner


