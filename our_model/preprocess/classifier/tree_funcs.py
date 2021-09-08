from nltk.tree import *
from stanfordcorenlp import StanfordCoreNLP


class TreeFunctions:
	def __init__(self):
		self.nlp = StanfordCoreNLP(r'stanford-corenlp-4.2.0')

	def get_tree(self, src_to_parse):
		try:
			parse = self.nlp.parse(src_to_parse)
			tree = Tree.fromstring(parse)

			first_level = []
			for first in tree:
				for child in first:
					first_level.append(child.label())
			first_level = " ".join(first_level)
			return tree, first_level
		except:
			print("Cannot parse :", src_to_parse)
			return None, None

	def close(self):
		self.nlp.close()
