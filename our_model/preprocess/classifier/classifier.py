import sys
import argparse
from collections import Counter
from nltk import word_tokenize
from collections import Counter

from first_class import FirstClass
from third_class import ThirdClass
from second_class import SecondClass
from tree_funcs import TreeFunctions


def main(complex_file, simple_file, output_file):

	tree_fns = TreeFunctions()
	first_class = FirstClass()
	second_class = SecondClass()
	third_class = ThirdClass()

	fps = open(output_file, "w")

	total = 0
	for src, dst_org in zip(open(complex_file), open(simple_file)):
		src = src.strip()
		dst_org = dst_org.strip()

		src_tokens = word_tokenize(src.lower())
		dst_tokens = dst_org.lower().replace("<sep>", "SEPAX").split()

		tree, first_level = tree_fns.get_tree(src)
		if tree is not None:
			if first_class.is_class(tree, first_level):
				dst = first_class.get_train_data(dst_org, first_level, tree)
				label = 3 if dst is None else 1
			elif third_class.is_class(first_level, tree, src_tokens, dst_tokens):
				dst = dst_org
				label = 3
			else:
				dst = second_class.get_train_data(src, dst_org)
				label = 2 if dst is not None else -1

			if dst is not None and label > 0:
				fps.write(src + "\t" + dst + "\t" + dst_org + "\t" + str(label) + "\n")

		total += 1
		if total % 10 == 0:
			print(total , "processed")

	tree_fns.close()
	fps.close()


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", dest="simple", help="Reference file.")
	parser.add_argument("-c", dest="complex", help="Complex sentence file.")
	parser.add_argument("-o", dest="output", help="Output file with class labels.")
	args = parser.parse_args()

	main(args.complex, args.simple, args.output)
