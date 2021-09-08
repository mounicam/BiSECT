import re
import simplediff
from nltk import word_tokenize


class SecondClass:
	def _capitalize(self, final_split):
		splits = [sp.strip() for sp in final_split.split("SEPAX")]

		if len(splits[0]) > 0 and len(splits[1]) > 0:
			right = splits[1].strip().split()
			right[0] = right[0].capitalize()
			return splits[0] + " <SEP> " + " ".join(right)
		return None

	def get_train_data(self, src, dst):

		src = word_tokenize(src)
		dst = dst.replace("<SEP>", "SEPAX").split()
		diff_tokens = simplediff.diff(src, dst)

		sep_index = [i for i, tokens in enumerate(diff_tokens) if tokens[0] == "+" and "SEPAX" in tokens[1]][0]

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
			return self._capitalize(" ".join(new_tokens).strip())
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
			return self._capitalize(" ".join(new_tokens).strip())
