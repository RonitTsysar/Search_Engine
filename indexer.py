import math
import pickle
import bisect
import utils
from multiprocessing import Pool
from collections import OrderedDict


class Indexer:

    TERM_NUM_IN_POSTING = 30000

    def __init__(self, config):
        # STRUCTURE OF INDEX
        # inverted_idx - {term : [df, posting_files_counter]} ----------> # inverted_idx - {term : [idf, posting_files_counter]}
        # inverted_idx - {term : [df, idf, total_tf]} ???
        # postingDict - {term: [(document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount)]}

        # self.inverted_idx = OrderedDict()
        # self.posting_dict = OrderedDict()
        self.inverted_idx = {}
        self.posting_dict = {}
        self.config = config

        self.all_posting = []
        self.posting_files_counter = 1
        self.num_of_terms_in_posting = 0


    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    # only df, without total_tf
                    self.inverted_idx[term] = 1
                    # self.inverted_idx[term] = [1, self.posting_files_counter]

                else:
                    self.inverted_idx[term] += 1
                    # self.inverted_idx[term][0] += 1

                tf = document_dictionary[term]
                normalized_tf = tf/document.max_tf  # or float(tf/document.max_tf)
                # print(self.posting_dict[term].keys())

                # bisect.insort - keep the list sorted
                if term not in self.posting_dict.keys():
                    self.posting_dict[term] = [(document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount)]
                else:
                    bisect.insort(self.posting_dict[term], (document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount))
                self.num_of_terms_in_posting += 1
            except:
                print('problem with the following key {}'.format(term[0]))


            ################################################################
            #                    save to files - Ronit
            ################################################################
            # saving files with pickle - TODO - give path to save this files
            if self.num_of_terms_in_posting == Indexer.TERM_NUM_IN_POSTING:
                self.save_posting()
               #  # TODO - RONIT - bisect - check how to keep list sorted by doc_id
               #  # sort keys(terms)
               #  self.posting_dict = {key: self.posting_dict[key] for key in sorted(self.posting_dict)}
               # # TODO - change to utils.save
               #  with open(f'posting{self.posting_files_counter}.pickle', 'wb') as file:
               #      # self.posting_files_counter += 1
               #      pickle.dump(self.posting_dict, file)
               #  # clean up
               #  self.num_of_terms_in_posting = 0
               #  self.posting_dict = {}
               #  self.all_posting_dicts.append([self.posting_files_counter])
               #  self.posting_files_counter += 1

            # TODO - decide or save df and total tf or only df
            # try:
            #     # Update inverted index and posting
            #     if term not in self.inverted_idx.keys():
            #         # with total_tf
            #         self.inverted_idx[term] = [1, 0]
            #         self.postingDict[term] = {}
            #
            #     # updates df
            #     else:
            #         self.inverted_idx[term][0] += 1  # with total_tf
            #
            #     tf = len(document_dictionary[term])
            #     self.inverted_idx[term][1] += tf
            #
            #     self.postingDict[term][document.tweet_id] = [normalized_tf, tf, document.max_tf, document.unique_terms_amount]
            #
            # except:
            #     print('problem with the following key {}'.format(term[0]))


    def save_posting(self):
        # sort keys(terms)
        self.posting_dict = {key: self.posting_dict[key] for key in sorted(self.posting_dict)}
        # TODO - change to utils.save
        with open(f'posting{self.posting_files_counter}.pickle', 'wb') as file:
            pickle.dump(self.posting_dict, file)
        # clean up
        self.num_of_terms_in_posting = 0
        self.posting_dict = {}
        self.all_posting.append([self.posting_files_counter])
        self.posting_files_counter += 1


    def helper_save_posting(self, posting_dict, postings_list):
        postings_list.append(self.posting_files_counter)
        utils.save_obj(posting_dict, self.posting_files_counter)
        posting_dict = OrderedDict()
        self.posting_files_counter += 1
        return posting_dict

        # clean up
        self.num_of_terms_in_posting = 0
        self.posting_dict = {}
        self.all_posting.append([self.posting_files_counter])
        self.posting_files_counter += 1

    # not parallel
    def merge_all_postings(self):

        while len(self.all_posting) > 1:
            updated_posting_list = [] #new merged
            i = 0

            while i < len(self.all_posting): # choose 2 batches and send to merge

                merged_posting = OrderedDict() #new dict
                batch_merged_list = [] # added dicts
                # lists of postings names (counter)
                batch_1, batch_2 = self.all_posting[i], self.all_posting[i+1]
                len_b1, len_b2 = len(batch_1), len(batch_2)
                # idx_b1, idx_b2, pointer_pd1, pointer_pd2, batch_pointer = 0, 0, 0, 0, 0
                idx_b1, idx_b2, pointer_pd1, pointer_pd2 = 0, 0, 0, 0

                posting_dict_1 = utils.load_obj(self.all_posting[idx_b1])
                posting_dict_2 = utils.load_obj(self.all_posting[idx_b2])
                # batch_pointer = min(pointer_pd1, pointer_pd2)

                # iterate through 2 lists of posting dicts
                while idx_b1 < len_b1 and idx_b2 < len_b2:
                # while batch_pointer < min(len_b1,len_b2):
                    if idx_b1 >= len_b1:
                        posting_dict_1 = utils.load_obj(self.all_posting[idx_b1])
                        pointer_pd1 = 0
                    elif idx_b2 >= len_b2:
                        posting_dict_2 = utils.load_obj(self.all_posting[idx_b2])
                        pointer_pd2 = 0

                    keys_1 = list(posting_dict_1.keys())
                    keys_2 = list(posting_dict_2.keys())

                    # iterate through 2 posting dicts
                    for comp_idx in enumerate(keys_1 if len(keys_1) < len(keys_2) else keys_2):
                        # term in posting 1 < term in posting 2
                        term_1, term_2 = keys_1[comp_idx], keys_2[comp_idx]
                        if term_1 < term_2:
                            merged_posting[term_1] = posting_dict_1[term_1]
                            pointer_pd1 += 1
                            # self.inverted_idx[term_1][1?] = self.posting_files_counter
                        elif term_1 > term_2:
                            merged_posting[term_2] = posting_dict_1[term_2]
                            pointer_pd2 += 1
                            # self.inverted_idx[term_2][1?] = self.posting_files_counter
                        # else: # term1 == term2

                        if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                            merged_posting = self.helper_save_posting(merged_posting, batch_merged_list)

                    # check which posting dict is finished
                    if comp_idx  >= len(keys_1):
                        idx_b1 += 1
                    elif comp_idx >= len(keys_2):
                        idx_b2 += 1

            i += 2

        self.all_posting = updated_posting_list

    def linspace(self, a, b, nsteps):
        """
        returns list of simple linear steps from a to b in nsteps.
        """
        ssize = float(b - a) / (nsteps - 1)
        return [a + i * ssize for i in range(nsteps)]

    def merge(self, left, right):
        """returns a merged and sorted version of the two already-sorted lists."""
        merged_list = []
        idx_left = idx_right = 0
        posting_dict_1 = utils.load_obj(self.all_posting[idx_left])
        posting_dict_2 = utils.load_obj(self.all_posting[idx_right])
        # iterate through 2 lists of posting dicts
        while idx_left < len(left) and idx_right < len(right):

            keys_1 = list(posting_dict_1.keys())
            keys_2 = list(posting_dict_2.keys())

            pointer_pd1 = pointer_pd2 = 0
            merged_posting = OrderedDict()

            # iterate through 2 posting dictionaries
            while pointer_pd1 < len(keys_1) and pointer_pd2 < len(keys_2):
                term_1, term_2 = keys_1[pointer_pd1], keys_2[pointer_pd2]
                if term_1 < term_2:
                    merged_posting[term_1] = posting_dict_1[term_1]
                    pointer_pd1 += 1
                    # self.inverted_idx[term_1][1?] = self.posting_files_counter
                elif term_1 > term_2:
                    merged_posting[term_2] = posting_dict_1[term_2]
                    pointer_pd2 += 1
                    # self.inverted_idx[term_2][1?] = self.posting_files_counter
                else: # term1 == term2
                    merged_posting[term_1] = posting_dict_1[term_1]
                    # TODO - save the merged list sorted by tweet_id
                    # merged_posting[term_1] = merge 2 sorted lists of tweets sorted by id
                    pointer_pd1 += 1
                    pointer_pd2 += 1
                    # self.inverted_idx[term_1][1?] = self.posting_files_counter

                # TODO - FIX helper_save_posting
                if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                    merged_posting = self.helper_save_posting(merged_posting, merged_list)

            if pointer_pd1 == len(keys_1):
                idx_left += 1
                pointer_pd1 = 0
                # need to load next dict from left
            if pointer_pd2 == len(keys_2):
                idx_right += 1
                pointer_pd2 = 0

        # need to check if finish last dict in left instead of copying it again




        if idx_left == len(left):
            merged_list.extend(right[idx_right:])
        if idx_right == len(right):
            merged_list.extend(left[idx_left:])

        return merged_list


    def merge_wrap(self, pair):
        l, r = pair
        return self.merge(l, r)

    def merge_sort_parallel(self, n):
        """
        Attempt to get parallel mergesort faster in Windows.  There is
        something wrong with having one Process instantiate another.
        Looking at speedup.py, we get speedup by instantiating all the
        processes at the same level.
        """
        num_of_threads = 2 ** n
        # instantiate a Pool of workers
        pool = Pool(processes = num_of_threads)
        # Now we have a bunch of sorted sublists.  while there is more than
        # one, combine them with merge.
        while len(self.all_posting_list) > 1:
            # get sorted sublist pairs to send to merge
            list_of_pairs = [(self.all_posting[i], self.all_posting[i + 1]) \
                    for i in range(0, len(self.all_posting), 2)]
            self.all_posting = pool.map(self.merge_wrap, list_of_pairs)
        # Since we start with numproc a power of two, there will always be an
        # even number of sorted sublists to pair up, until there is only one.
        self.all_posting = self.all_posting[0]


    # Calculate idf for each term in inverted index after finish indexing
    def calculate_idf(self, N):
        for term, df in self.inverted_idx.items():
            idf = math.log2(N/df)
            self.inverted_idx[term] = idf

