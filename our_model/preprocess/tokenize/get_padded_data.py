import sys, glob
import argparse
import simplediff
from nltk import word_tokenize
from wordpiece import FullTokenizer
from second_rule import SecondClass


def pad_sequences(tokenizer, seq1, seq2):
	seq1 = tokenizer.tokenize(seq1)
	seq2 = " [SEP] ".join([" ".join(tokenizer.tokenize(dst_line.strip())) for dst_line in seq2.split("<SEP>")]).split()
	if len(seq1) < len(seq2):
		return seq1 + ["[FILL]"] * (len(seq2) - len(seq1)), seq2
	if len(seq2) < len(seq1):
		return seq1, seq2 + ["[FILL]"] * (len(seq1) - len(seq2))
	assert len(seq2) == len(seq1)
	return seq1, seq2


def main(input_file, output_prefix, vocab_file):
	fps = open(output_prefix + ".src", "w")
	fpd = open(output_prefix + ".dst", "w")
	fpl = open(output_prefix + ".labels", "w")

	sc = SecondClass()
	tokenizer = FullTokenizer(vocab_file, do_lower_case=False)

	for line in open(input_file):
		tokens = line.strip().split("\t")
		src, dst, dst_org, label = tokens
		dst_org = " <SEP> ".join([s.strip() for s in dst_org.split("<SEP>")])

		src_tokens = word_tokenize(src)
		diff_tokens = simplediff.diff(src_tokens, dst_org.replace("<SEP>", "SEPAX").split())

		if "SEPAX" in diff_tokens[0][1] or "SEPAX" in diff_tokens[-1][1]:
			label = "3"

		if label == "2":
			assert dst is not None

			dst = sc.get_train_data(diff_tokens, src_tokens, dst_org.replace("<SEP>", "SEPAX").split())
			dst_tokens = dst.split()

			left = 0
			while left < len(dst_tokens) and left < len(src_tokens) and src_tokens[left] == dst_tokens[left]:
				left += 1

			right_dst = len(dst_tokens) - 1
			right_src = len(src_tokens) - 1
			while right_src >= 0 and right_dst >= 0 and src_tokens[right_src] == dst_tokens[right_dst]:
				right_src -= 1
				right_dst -= 1

			dst_middle = " ".join(dst_tokens[left:right_dst + 1])

			dst_left, dst_right = [s.strip() for s in dst_org.split(dst_middle)]
			src_left, src_middle, src_right = " ".join(src_tokens[:left]), \
											  " ".join(src_tokens[left:right_src + 1]), " ".join(
				src_tokens[right_src + 1:])
			src_left, dst_left = pad_sequences(tokenizer, src_left, dst_left)
			src_right, dst_right = pad_sequences(tokenizer, src_right, dst_right)
			src_middle, dst_middle = pad_sequences(tokenizer, src_middle, dst_middle)

			src = "[CLS] " + " ".join(src_left + src_middle + src_right).strip() + " [SEP]"
			dst = "[CLS] " + " ".join(dst_left + dst_middle + dst_right).strip() + " [SEP]"
			labels = ["1"] + ["1"] * len(src_left) + ["0"] * len(src_middle) + ["1"] * len(src_right) + ["1"]

		else:
			src, dst = pad_sequences(tokenizer, src, dst)
			src = "[CLS] " + " ".join(src).strip() + " [SEP]"
			dst = "[CLS] " + " ".join(dst).strip() + " [SEP]"
			labels = ["0"] * len(src.split())

		label = str(int(label) - 1)
		assert len(labels) == len(src.split()) == len(dst.split())
		fps.write(src + "\n")
		fpd.write(dst + "\n")
		fpl.write(str(label) + " " + " ".join(labels) + "\n")

	fps.close()
	fpd.close()
	fpl.close()

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-v", dest="vocab", default="preprocess/tokenize/vocab.txt")
	parser.add_argument("-i", dest="input", help="Complex-Split sentence tsv file with rule labels.")
	parser.add_argument("-o", dest="output", help="Output prefix. .src, .dst and, .label files are created.")
	args = parser.parse_args()

	main(args.input, args.output, args.vocab)