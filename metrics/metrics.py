import argparse
import simplediff
from collections import Counter
from nltk import word_tokenize
from fkgl import compute_fkgl
from sari import compute_sari
from gleu import sentence_gleu, corpus_gleu


def clean(sentence):
	sent_tokens = []
	for sent in sentence.split("<SEP>"):
		sent_tokens.extend(word_tokenize(sent.strip()))
	return " ".join(sent_tokens)


def read_file(filename, ref=False):
	i = 0
	new_lines = []
	for line in open(filename, 'r'):
		line = line.strip().split("\t")
		if ref:
			new_sents = [clean(reference) for reference in line]
			new_lines.append(new_sents)
		else:
			new_sent = clean(line[0])
			new_lines.append(new_sent)
		i += 1

	return new_lines


def edit_ref(sent, dst):
	difftokens = simplediff.diff(dst.split(), sent.split())
	added_phrases = [" ".join(tokens) for s, tokens in difftokens if s == "+"]

	new_ref = []
	for s, tokens in difftokens:
		if s == "=":
			new_ref.extend(tokens)
		elif s == "-":
			phrase = " ".join(tokens)
			id = 0
			flag = False
			for paraphrase in added_phrases:
				if (paraphrase in ppdb and phrase in ppdb[paraphrase]) \
					or (phrase in ppdb and paraphrase in ppdb[phrase]):
					new_ref.append(paraphrase)
					added_phrases.pop(id)
					flag = True
					break
				id += 1
			if not flag:
				new_ref.append(phrase)

	difftokens = simplediff.diff(new_ref, sent.split())
	added_phrases = []
	for s, tokens in difftokens:
		if s == "+":
			added_phrases.extend(tokens)

	new_ref = []
	for s, tokens in difftokens:
		if s == "=":
			new_ref.extend(tokens)
		elif s == "-":
			for phrase in tokens:
				id = 0
				flag = False
				for paraphrase in added_phrases:
					if (paraphrase in ppdb and phrase in ppdb[paraphrase]) or (
							phrase in ppdb and paraphrase in ppdb[phrase]):
						new_ref.append(paraphrase)
						added_phrases.pop(id)
						flag = True
						break
					id += 1
				if not flag:
					new_ref.append(phrase)

	new_ref = " ".join(new_ref)
	return new_ref


def compression_ratio(comp, simp):
	return len(simp.split()) * 1.0 / len(comp.split())


def print_metrics(complex_sentences, simplified_sentences, reference_sentences):
	assert len(complex_sentences) == len(simplified_sentences) == len(reference_sentences)

	simplified_sentences = [s.replace("` `", '``').replace("' '", "''") for s in
							simplified_sentences]

	reference_sentences = [[edit_ref(simp, ref) for ref in ref_sents] for ref_sents, simp in
						   zip(reference_sentences, simplified_sentences)]

	slen, wlen, fkgl = compute_fkgl(simplified_sentences)

	sari_score, _, add, keep, deletep, _, _ = compute_sari(complex_sentences, reference_sentences,
																		   simplified_sentences)

	rbleu = corpus_gleu([[ref.split() for ref in refs] for refs in reference_sentences],
						[sent.split() for sent in simplified_sentences])

	cr = [compression_ratio(comp, simp) for comp, simp in zip(complex_sentences, simplified_sentences)]
	cr = sum(cr) * 1.0 / len(cr)

	bleu = []
	overlap_all = []
	for comp, simp in zip(complex_sentences, simplified_sentences):
		ref = [comp.lower().split()]
		hyp = simp.lower().split()
		hyp_counter = Counter(hyp)
		ref_counter = Counter(ref[0])
		overlap = sum((hyp_counter - ref_counter).values()) * 1.0 / len(hyp)
		bleu.append(sentence_gleu(ref, hyp))
		overlap_all.append(overlap)

	bleu = sum(bleu) * 100.0 / len(bleu)
	overlap = sum(overlap_all) * 100.0 / len(overlap_all)

	avg_len = [len(sent.split()) for sent in simplified_sentences]
	avg_len = sum(avg_len) * 1.0 / len(avg_len)

	print("SARI add/keep/delete scores: ", round(sari_score * 100.0, 1), round(add * 100.0, 1),
		  round(keep * 100.0, 1), round(deletep * 100.0, 1))
	print("FKGL: ", round(fkgl, 1))
	print("BLEU: ", round(rbleu * 100.0, 1))
	print("Avg sentence length / Avg. output length: ", round(slen, 1), round(avg_len, 1))
	print("Compression Ratio: ", round(cr, 2))
	print("Self-BLEU: ", round(bleu, 1))
	print("% new words: ", round(overlap, 1))


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument("-r", dest="reference", help="Reference file where references are seperated with a tab.")
	parser.add_argument("-c", dest="complex", help="File with complex sentences.")
	parser.add_argument("-ppdb", dest="ppdb", help="PPDB phrase file")
	parser.add_argument("-s", dest="simplified", help="File with simplified sentences.")
	args = parser.parse_args()

	ppdb = {}
	for line in open(args.ppdb):
		line = line.strip().split("\t")
		if len(line[0]) > 0 and len(line[1]) > 0:
			if line[0] not in ppdb:
				ppdb[line[0]] = set()
			ppdb[line[0]].add(line[1])

	complex_sentences = read_file(args.complex)
	reference_sentences = read_file(args.reference, ref=True)
	simplified_sentences = read_file(args.simplified)
	print_metrics(complex_sentences, simplified_sentences, reference_sentences)
