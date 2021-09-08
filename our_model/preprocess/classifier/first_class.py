import re
import string


class FirstClass:
	def __init__(self):

		self.SEPS = {"CC", ";", ":", "RB", "IN"}
		self.pattern = re.compile("^((?:ADVP|PP) (, )*)*S (, )*(CC )*(IN )*S \.$")

	def from_first_level(self, parse_str):
		parse_str = parse_str.replace("SQ", "S")
		nodes = parse_str.split()[:-1]
		return re.search(self.pattern, parse_str) or parse_str == "S , RB S ." or \
			(len(set(nodes).difference({"S", "CC", ","})) == 0 and "CC" in nodes) or \
			parse_str == "SBARQ , CC SBARQ ." or parse_str == "SBARQ CC SBARQ ."

	def from_sep(self, src):
		return ";" in src and all([len(tok.strip()) > 0 for tok in src.split(";")])

	def is_class(self, tree, first_level):
		src = " ".join(tree.leaves())
		return self.from_first_level(first_level) or self.from_sep(src)

	def _get_splits(self, tree, tgt):
		chunks = []
		chunk_splits = []
		for child in tree[0]:
			if child.label() in self.SEPS and len(chunks) > 0 and chunks[-1][-1] in self.SEPS:
				chunks[-1].append(child.label())
				chunk_splits[-1].append(" ".join(child.leaves()))
			else:
				chunks.append([child.label()])
				chunk_splits.append([" ".join(child.leaves())])

		ref_left, ref_right = [sent.strip() for sent in tgt.split("<SEP>")]
		final_splits = []
		for i, tokens in enumerate(chunks):
			if all([t in self.SEPS for t in tokens]):
				src_left = []
				for sent in chunk_splits[:i]:
					src_left.extend(sent)

				if len(src_left) > 0:
					if src_left[-1] in string.punctuation:
						src_left = src_left[:-1]

					if "? <SEP>" in tgt:
						src_left.append("?")
					else:
						src_left.append(".")

				src_right = []
				for sent in chunk_splits[i:]:
					src_right.extend(sent)

				left = len(src_left) * 1.0 / len(ref_left)
				right = len(src_right) * 1.0 / len(ref_right)
				final_splits.append((" ".join(src_left), " ".join(src_right), abs(left - 1.0) + abs(right - 1.0)))

		final_splits.sort(key=lambda x: x[2])
		return final_splits

	def _capitalize(self, final_splits):
		final_splits = [split for split in final_splits if len(split[0]) > 0 and len(split[1]) > 0]
		if len(final_splits) > 0:
			splits = final_splits[0]
			right = splits[1].split()
			right[0] = right[0].capitalize()
			return splits[0] + " <SEP> " + " ".join(right)
		return None

	def get_train_data(self, tgt, first_level, tree):

		src = " ".join(tree.leaves())

		if self.from_first_level(first_level):
			final_splits = self._get_splits(tree, tgt)
			return self._capitalize(final_splits)

		elif self.from_sep(src):
			ref_left, ref_right = [sent.strip() for sent in tgt.split("<SEP>")]
			chunk_splits = [sent.strip() for sent in src.split(";")]

			final_splits = []
			for i in range(len(chunk_splits)):
				src_left = chunk_splits[:i]
				src_right = chunk_splits[i:]
				if len(src_left) > 0:
					src_left.append(".")

				if len(src_left) > 0 and len(src_right) > 0:
					left = len(src_left) * 1.0 / len(ref_left)
					right = len(src_right) * 1.0 / len(ref_right)
					final_splits.append((" ".join(src_left), " ".join(src_right), abs(left - 1.0) + abs(right - 1.0)))

			final_splits.sort(key=lambda x: x[2])
			return self._capitalize(final_splits)

		return None
