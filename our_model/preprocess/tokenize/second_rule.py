import re
import simplediff
from nltk import word_tokenize


class SecondClass:
	def get_train_data(self, diff_tokens, src, dst):

		sep_index = [i for i, tokens in enumerate(diff_tokens) if tokens[0] == "+" and "SEPAX" in tokens[1]][0]
		assert 1 <= sep_index < len(diff_tokens) - 1

		if diff_tokens[sep_index][1][1] == "SEPAX":
			sindex = 0
			dindex = 0
			new_tokens = []
			for tokens in diff_tokens[:sep_index - 1]:
				if tokens[0] == "=" or tokens[0] == "-":
					for _ in tokens[1]:
						new_tokens.append(src[sindex])
						sindex += 1

				if tokens[0] == "=" or tokens[0] == "+":
					for _ in tokens[1]:
						dindex += 1

			for _ in diff_tokens[sep_index - 1][1]:
				if diff_tokens[sep_index - 1][0] == "=":
					new_tokens.append(src[sindex])
					dindex += 1
				sindex += 1

			while sep_index < len(diff_tokens) and not (
						diff_tokens[sep_index][0] == "=" and len(diff_tokens[sep_index][1]) >= 4):
				tokens = diff_tokens[sep_index]
				if tokens[0] == "=":
					for _ in tokens[1]:
						new_tokens.append(dst[dindex])
						sindex += 1
						dindex += 1
				elif tokens[0] == "+":
					for _ in tokens[1]:
						new_tokens.append(dst[dindex])
						dindex += 1
				else:
					for _ in tokens[1]:
						sindex += 1
				sep_index += 1

			if sep_index < len(diff_tokens):
				for tokens in diff_tokens[sep_index:]:
					if tokens[0] == "=" or tokens[0] == "-":
						for _ in tokens[1]:
							new_tokens.append(src[sindex])
							sindex += 1
			return " ".join(new_tokens).strip().replace("SEPAX", "<SEP>")
		else:
			left = sep_index - 1
			while left >= 0 and (diff_tokens[left][0] == "-" or diff_tokens[left][0] == "+" or (
						diff_tokens[left][0] == "=" and len(diff_tokens[left][1]) < 2)):
				left -= 1

			right = sep_index + 1
			while right < len(diff_tokens) and (diff_tokens[right][0] == "-" or diff_tokens[right][0] == "+" or (
						diff_tokens[right][0] == "=" and len(diff_tokens[right][1]) < 2)):
				right += 1

			sindex = 0
			dindex = 0
			new_tokens = []

			if left > -1:
				for tokens in diff_tokens[:left + 1]:
					if tokens[0] == "=":
						for _ in tokens[1]:
							new_tokens.append(src[sindex])
							sindex += 1
							dindex += 1
					elif tokens[0] == "-":
						for _ in tokens[1]:
							new_tokens.append(src[sindex])
							sindex += 1
					else:
						for _ in tokens[1]:
							dindex += 1

			for tokens in diff_tokens[left + 1:right]:
				if tokens[0] == "=":
					for _ in tokens[1]:
						new_tokens.append(src[sindex])
						sindex += 1
						dindex += 1
				elif tokens[0] == "-":
					for _ in tokens[1]:
						sindex += 1
				else:
					for _ in tokens[1]:
						new_tokens.append(dst[dindex])
						dindex += 1

			if right < len(diff_tokens):
				for tokens in diff_tokens[right:]:
					if tokens[0] == "=":
						for _ in tokens[1]:
							new_tokens.append(src[sindex])
							sindex += 1
							dindex += 1
					elif tokens[0] == "-":
						for _ in tokens[1]:
							new_tokens.append(src[sindex])
							sindex += 1
					else:
						for _ in tokens[1]:
							dindex += 1
			return " ".join(new_tokens).strip().replace("SEPAX", "<SEP>")
