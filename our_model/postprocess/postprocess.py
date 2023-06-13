import glob, re
import argparse
from string import punctuation


def get_output_sentences(file_name, interactive=5, lines_to_ignore=5):
    if interactive == 4:
        lines = open(file_name).readlines()[lines_to_ignore:]
    else:
        lines = open(file_name).readlines()[lines_to_ignore:-2]

    i = 0
    preds = {}
    while i < len(lines):

        token = lines[i].split()[0]
        number = int(token.split("-")[1])

        hyp = lines[i + (interactive - 3)].split("\t")[2].strip()
        alignments = lines[i + (interactive - 1)].split("\t")[1].strip()
        alignments = [int(a.split("-")[0]) for a in alignments.split()]

        preds[number] = (hyp, alignments)
        i = i + interactive

    return preds


def transform(s, src):
    stokens = s.split()
    snew = s
    for i, token in enumerate(stokens):
        if i > 0 and i < len(stokens) - 1 and token in punctuation:
            substrboth =  stokens[i - 1] + token + stokens[i + 1]
            substrleft = stokens[i - 1] + token
            substright = token + stokens[i + 1]
            if substrboth in src:
                snew = snew.replace(stokens[i - 1] + " " + token + " " + stokens[i + 1], substrboth)
            elif substrleft in src:
                snew = snew.replace(stokens[i - 1] + " " + token, substrleft)
            elif substright in src:
                snew = snew.replace(token + " " + stokens[i + 1], substright)

    snew = snew.replace("'''", "''")
    snew = snew.replace('"', "''")
    snew = snew.replace('- LRB -', " ( ")
    snew = snew.replace('- RRB -', " ) ")
    return snew


def main(args):

    out_anon_sents = get_output_sentences(args.input, int(args.interactive), int(args.ignore_lines))
    src_sents = [line.strip() for line in open(args.src)]

    fp = open(args.output, "w")
    for i in range(0, len(out_anon_sents)):
        hyp, _ = out_anon_sents[i]
        denon_sent = hyp.replace("[SEP]", "<SEP>").strip()

        if denon_sent.endswith("<SEP>"):
            denon_sent = " ".join(denon_sent.split()[1:-1])
        else:
            denon_sent = " ".join(denon_sent.split()[1:])

        denon_sent = denon_sent.replace(" ##", "").strip()
        denon_sent = " ".join([tok for tok in denon_sent.split() if "[unused12]" not in tok])

        fp.write(transform(denon_sent, src_sents[i]) + "\n")

    fp.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--src')
    parser.add_argument('--input')
    parser.add_argument('--output')
    parser.add_argument('--ignore_lines', default=5)
    parser.add_argument('--interactive', default=5)
    args = parser.parse_args()
    main(args)
