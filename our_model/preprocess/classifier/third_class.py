import re

CONJS = {"since", "when", "after", "as", "although", "though", "because", "whenever", "while", "if", "even", "not",
		 "instead", "before", "in", "due", "besides"}

pat1 = re.compile("^.* S , NP VP .$")
pat2 = re.compile("^.* SBAR , NP VP .$")


class ThirdClass:
	def is_class(self, first_level, tree, src_tokens, dst_tokens):
		return first_level.split()[0] == "SBAR" or first_level.split()[0] == "SBAR" \
			or self.is_rule_1(first_level) or \
			self.is_rule_2(first_level, tree) or \
			self.is_rule_3(first_level, tree) or \
			(src_tokens[0] in CONJS and src_tokens[0] != dst_tokens[0])

	def is_rule_1(self, parse_str):
		return parse_str == "S , NP VP ." or parse_str == "CC SBAR , NP VP ." \
			or parse_str == "S NP VP ." \
			or parse_str == "`` S , '' NP VP ." or re.search(pat1, parse_str) \
			or re.search(pat2, parse_str)

	def is_rule_2(self, parse_str, tree):
		return (parse_str == "PP , NP VP ." or parse_str == "PP , CC NP VP ." or parse_str == "PP NP VP") and any(
			[len(child.leaves()) > 10 and child.label() == "PP" for child in tree[0]])

	def is_rule_3(self, parse_str, tree):
		if "NP VP ." in parse_str:
			second_level = [child for child in tree[0][-2]]
			return len(second_level) > 3 and second_level[-1].label() == "S" and second_level[-2].label() == ","
		return False
