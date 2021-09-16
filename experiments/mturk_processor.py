import csv
import nltk
import numpy as np
import random
import scipy.stats as st
from matplotlib import pyplot as plt
from sacremoses import MosesDetokenizer

class MTurkProcessor:

    def __init__(self, lang='en'):
        """Constructor for Mechanical Turk processor

        Args:
            lang (str, optional): the language of the dataset. Defaults to 'en' (English).
        """
        self.detokenizer = MosesDetokenizer(lang=lang)
        self.lang = lang

    @staticmethod
    def build_score_by_worker(output_csv, topic="fluency", overlap=2, window=4):
        """Builds a data structure of ratings given by each worker

        Args:
            output_csv (str): path to output CSV
            topic (str, optional): indicator for response category. Defaults to fluency.
            overlap (int, optional): number of workers for each HIT. Defaults to 2.
            window (int, optional): number of system outputs for each HIT. Defaults to 4.

        Returns:
            score_by_worker: described below, num_hits: total number of HITs
        """
        ### The format of score_by_worker is the following:
        # score_by_worker
        #   worker_id
        #       output_id(sid)
        #           list[(complex_id(cid), answer)]
        #       ...
        #   worker_id
        #       ...
        #   ...
        with open(output_csv, 'r', encoding="utf-8") as file:
            reader = csv.reader(file, delimiter=',')
            score_by_worker = dict()
            for i, row in enumerate(reader):
                if i == 0:
                    worker_col = row.index("WorkerId")
                    input_cid = row.index("Input.cid")
                    input_sids = [row.index("Input.sid-%d" % (j+1)) for j in range(window)]
                    answer_ids = [row.index("Answer.%s-%d" % (topic, j+1)) for j in range(window)]
                elif row[worker_col] not in score_by_worker:
                    score_by_worker[row[worker_col]] = dict()
                    sep = row[input_cid].index("-") + 1
                    for a, s in zip(answer_ids, input_sids):
                        score_by_worker[row[worker_col]][row[s]] = list()
                        score_by_worker[row[worker_col]][row[s]].append((int(row[input_cid][sep:]), float(row[a])))
                else:
                    sep = row[input_cid].index("-") + 1
                    for a, s in zip(answer_ids, input_sids):
                        score_by_worker[row[worker_col]][row[s]].append((int(row[input_cid][sep:]), float(row[a])))
            num_hits = i // overlap
        return score_by_worker, num_hits
    
    @staticmethod
    def obtain_stats(score_by_system, num_hits):
        """Computes statistics from worker responses

        Args:
            score_by_system (dict[int->dict[int->list[int]]]): a dictionary containing list of worker ratings for each system and HIT
            num_hits (int): total number of HITs

        Returns:
            dict[str->float]: dictionary containing average score for each system
        """
        score_by_system_avg_tot = dict.fromkeys(score_by_system.keys())
        for sid, system_scores in score_by_system.items():
            system_score_avg = [-1 for _ in range(num_hits)]
            for i, scores in enumerate(system_scores):
                system_score_avg[i] = np.median(scores, axis=0)
            system_score_avg_filter = [x for x in system_score_avg if x >= 0]
            score_by_system_avg_tot[sid] = np.mean(np.array(system_score_avg_filter), axis=0)
        return score_by_system_avg_tot
    
    def create_input(self, complex_list, output_list, index_list, test_labels, model_labels, input_path=None, control=True):
        """Creates input to the Mechanical Turk interface, with the same complex sentence in each HIT

        Args:
            complex_list (list[str]): a list of file directories for complex sentence inputs
            output_list (list[list[str]]): a list of list of file directories for sentence outputs to be tested
            index_list (list[str]): a list of file directories for sentence indices to be used for testing
            test_labels (list[str]): a list of labels that describe different types of test sets
            model_labels (list[str]): a list of labels that describe different types of models used to generate outputs
            input_path (str, optional): the path for the CSV file to be used as input for MTurk. Defaults to None.
        """
        assert(len(complex_list) == len(output_list) == len(index_list) == len(test_labels))
        # Initialize input CSV path if not provided
        if not input_path:
            input_path = "experiments/mturk_input.csv"
        # Load all files from the specified directories
        complex_file_list = [open(c, "r", encoding="utf-8") for c in complex_list]
        output_file_list = [[open(o, "r", encoding="utf-8") for o in output] for output in output_list]
        idx_file_list = [open(i, "r") for i in index_list]
        label_list = [[t + '-' + m for m in model_labels] for t in test_labels]
        input_file = open(input_path, "w", encoding="utf-8")
        writer = csv.writer(input_file, delimiter=",")
        # Write headers for the CSV
        header = ["cid", "complex"]
        header.extend(["sid-%d" % (x + 1) for x in range(len(output_list[0]) + 1)])
        header.extend(["simple-%d" % (x + 1) for x in range(len(output_list[0]) + 1)])
        writer.writerow(header)
        # Prepare imputed files
        vocab_set = [set() for _ in range(len(complex_list))]
        vocab_list = [list() for _ in range(len(complex_list))]
        impute_list = [list() for _ in range(len(complex_list))]
        sample_list = []
        for i, outputs in enumerate(output_file_list):
            sample_lines = outputs[0].readlines()
            sample_list.append(sample_lines)
            counter, index = 0, 0
            # Build the vocabulary dictionary
            while counter < 1e3 and index < len(sample_lines):
                line = sample_lines[index]
                tokens = line.split(' ')
                for tok in tokens:
                    if tok.isalpha() and tok not in vocab_set[i]:
                        vocab_set[i].add(tok)
                        vocab_list[i].append(tok)
                        counter += 1
                index += 1
            for line in sample_lines:
                impute_list[i].append(self.impute_sent(line, vocab_list[i]))
        # Iterate over outputs from different test sets
        for complex_f, idx_f, output_f, test, labels, impute_lines, read_lines in \
                zip(complex_file_list, idx_file_list, output_file_list, test_labels,
                    label_list, impute_list, sample_list):
            idx_lines = idx_f.readlines()
            complex_lines = complex_f.readlines()
            output_lines = [read_lines]
            output_lines.extend([out.readlines() for out in output_f[1:]])
            if control:
                output_lines.append(impute_lines)
                labels.append(test + '-control')
            for i, idx in enumerate(idx_lines):
                pattern = np.arange(len(output_lines))
                random.shuffle(pattern)
                idx = int(idx) - 1
                new_lines = ['' for _ in range(len(output_lines) + 1)]
                new_lines[0] = self.process_sent(complex_lines[idx].strip())
                for j in range(len(output_lines)):
                    new_lines[j + 1] = self.process_sent(output_lines[pattern[j]][idx].strip())
                output_row = ['%s-%d' % (test, i), new_lines[0]]
                output_row.extend([labels[pattern[x]] for x in range(len(output_lines))])
                output_row.extend([new_lines[x + 1] for x in range(len(output_lines))])
                writer.writerow(output_row)
        input_file.close()

    def generate_diff(self, input_csv, output_path, window=4):
        """Generates an output CSV with differences highlighted based on the original CSV

        Args:
            input_csv (str): path to original CSV
            output_path (str): path to the output CSV
            window (int, optional): number of system outputs per HIT. Defaults to 4.
        """
        out_file = open(output_path, "w", encoding="utf-8")
        with open(input_csv, "r", encoding="utf-8") as in_file:
            reader = csv.reader(in_file, delimiter=',')
            writer = csv.writer(out_file, delimiter=',')
            for i, row in enumerate(reader):
                if i == 0:
                    input_cid = row.index("cid")
                    input_sid = [row.index("sid-%d" % (j+1)) for j in range(window)]
                    input_complex = row.index("complex")
                    input_simple = [row.index("simple-%d" % (j+1)) for j in range(window)]
                    writer.writerow(row)
                else:
                    complex_sent = row[input_complex]
                    row_out = [row[input_cid], complex_sent]
                    row_out += [row[idx] for idx in input_sid]
                    for idx in input_simple:
                        simple_sent = row[idx]
                        html_output = self.sent_diff(complex_sent, simple_sent)
                        html_output = html_output.replace("ins>", "mark>")
                        html_output = html_output.replace("<del>", "<span class='tooltip' style='color:red'>^<span class='tooltiptext'>")
                        html_output = html_output.replace("</del>", "</span></span>")
                        row_out.append(html_output)
                    writer.writerow(row_out)
        out_file.close()

    def quality_control_complex(self, score_by_worker, num_hits, ratio=0.2):
        """Applies quality control on each complex sentence

        Args:
            score_by_worker (dict[str->dict[int->list[(int, int)]]]): data structure containing  worker ratings
            num_hits (int): total number of HITs
            ratio (float, optional): max threshold for ratio of bad quality responses. Defaults to 0.2.

        Returns:
            dict[str->bool]: dictionary mapping worker IDs to booleans indicating whether to use each worker
        """
        workers_to_use = dict.fromkeys(score_by_worker.keys(), False)
        score_by_complex = [dict() for _ in range(num_hits)]
        # Populate the score by complex
        for wid, outputs in score_by_worker.items():
            for sid, response in outputs.items():
                for c, score in response:
                    if sid in score_by_complex[c]:
                        score_by_complex[c][sid].append(score)
                    else:
                        score_by_complex[c][sid] = [score]
        score_by_complex_min = [0 for _ in range(num_hits)]
        # Pre-compute average score per complex-system output
        for c in range(num_hits):
            avg_score = dict()
            for sid in outputs:
                if sid in score_by_complex[c] and "control" not in sid:
                    avg_score[sid] = np.mean(np.array(score_by_complex[c][sid]), axis=0)
            score_by_complex_min[c] = min(avg_score.values())
        # Count number of bad responses per worker
        worker_bad_count = dict.fromkeys(score_by_worker.keys(), 0)
        worker_count = dict.fromkeys(score_by_worker.keys(), 0)
        for wid, outputs in score_by_worker.items():
            for sid, response in outputs.items():
                if "control" in sid:
                    for c, score in response:
                        if score > 50:
                            worker_bad_count[wid] += 1
                        worker_count[wid] += 1
        # Filter workers based on pre-defined threshold
        count_good = 0
        for wid in worker_bad_count:
            if float(worker_bad_count[wid] / worker_count[wid]) < ratio:
                workers_to_use[wid] = True
                count_good += 1
        return workers_to_use

    def process_output(self, output_csv, topic="fluency", window=5, control=True):
        """processes MTurk output CSV

        Args:
            output_csv (str): path to the output CSV from MTurk
            topic (str): indicator for response category. Defaults to fluency.
            window (int, optional): number of system outputs per HIT. Defaults to 5.
            control (bool, optional): whether to apply quality control to results (unnecessary if checked beforehands). Defaults to True.

        Returns:
            dict[str->float]: dictionary containing average score for each system
        """
        ### Populate the score_by_worker dictionary from the MTurk output csv file
        score_by_worker, num_hits = self.build_score_by_worker(output_csv, topic, window=window)
        ### Now perform quality control
        if control:
            workers_to_use = self.quality_control_complex(score_by_worker, num_hits)
        else:
            workers_to_use = dict.fromkeys(score_by_worker.keys(), True)
        # workers_to_use = self.quality_control_naive(score_by_worker)
        ### Initialize score by system outputs
        score_by_system = dict()
        system_ids = list(score_by_worker.values())[0]
        for sid in system_ids:
            score_by_system[sid] = [[] for _ in range(num_hits)]
        ### Initialize score by system outputs for each worker
        score_by_system_worker = dict()
        for wid, use in workers_to_use.items():
            if use:
                score_by_system_worker[wid] = {sid: [-1 for _ in range(num_hits)] for sid in system_ids}
        ### Obtain scores from "good" workers
        for wid, use in workers_to_use.items():
            # print(wid, use)
            if use:
                outputs = score_by_worker[wid]
                # Loop over system outputs
                for sid, response in outputs.items():
                    # Loop over individual scores
                    for cid, score in response:
                        # print(cid)
                        score_by_system[sid][cid].append(score)
                        score_by_system_worker[wid][sid][cid] = score
        ### Compute overall statistics by averaging for each question and excluding min/max
        score_by_system_avg_tot = self.obtain_stats(score_by_system, num_hits)
        ### Compute overall statistics for every worker
        score_by_system_avg_tot_by_worker = dict()
        count_ratings_by_worker = dict()
        for wid in score_by_system_worker:
            worker_system_ratings = dict()
            for sid in score_by_system_worker[wid]:
                worker_ratings = [x for x in score_by_system_worker[wid][sid] if x >= 0]
                worker_system_ratings[sid] = np.mean(np.array(worker_ratings), axis=0)
            score_by_system_avg_tot_by_worker[wid] = worker_system_ratings
            count_ratings_by_worker[wid] = len(worker_ratings)
        return score_by_system_avg_tot


if __name__ == "__main__":

    ########### ALWAYS INSTANTIATE PROCESSOR ###########
    mturk = MTurkProcessor()

    ########### USE FOR GENERATING INPUTS ###########

    # Define input file paths
    complex_files = ["COMPLEX.txt"]
    output_files = [["SYSTEM1.txt", "SYSTEM2.txt", "SYSTEM3.txt"]]
    index_files = ["INDEX.txt"]
    test_labels_main = ["bisect"]
    model_labels_main = ["SYSTEM1", "SYSTEM2", "SYSTEM3"]
    csv_path = "PATH_TO_INPUT_CSV"

    # Create input CSV to Mechanical Turk
    mturk.create_input(complex_files, output_files, index_files, test_labels_main, model_labels_main, csv_path)
    
    # Generate modified input CSV with add/delete operations
    mturk.generate_diff("PATH_TO_INPUT_CSV", "PATH_TO_FINAL_INPUT_CSV")

    ########### USE FOR ANALYZING OUTPUTS ###########

    # Obtain ratings from non-anonymous workers
    output = mturk.process_output("PATH_TO_OUTPUT_CSV", topic="fluency", window=6, control=True)
    print(output)
