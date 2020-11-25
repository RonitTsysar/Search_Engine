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
                    # self.inverted_idx[term] = 1
                    self.inverted_idx[term] = [1, self.posting_files_counter]

                else:
                    # self.inverted_idx[term] += 1
                    self.inverted_idx[term][0] += 1

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
        utils.save_obj(self.posting_dict, str(self.posting_files_counter))
        # clean up
        self.num_of_terms_in_posting = 0
        self.posting_dict = {}
        self.all_posting.append([self.posting_files_counter])
        self.posting_files_counter += 1


    def save_in_merge(self, merged_posting, merged_list):
        utils.save_obj(merged_posting, str(self.posting_files_counter))
        merged_list.append(self.posting_files_counter)
        self.posting_files_counter += 1
        return {}


    # not parallel
    # def merge_all_postings(self):
    #
    #     while len(self.all_posting) > 1:
    #         updated_posting_list = [] #new merged
    #         i = 0
    #
    #         while i < len(self.all_posting): # choose 2 batches and send to merge
    #
    #             merged_posting = OrderedDict() #new dict
    #             batch_merged_list = [] # added dicts
    #             # lists of postings names (counter)
    #             batch_1, batch_2 = self.all_posting[i], self.all_posting[i+1]
    #             len_b1, len_b2 = len(batch_1), len(batch_2)
    #             # idx_b1, idx_b2, pointer_pd1, pointer_pd2, batch_pointer = 0, 0, 0, 0, 0
    #             idx_b1, idx_b2, pointer_pd1, pointer_pd2 = 0, 0, 0, 0
    #
    #             posting_dict_1 = utils.load_obj(self.all_posting[idx_b1])
    #             posting_dict_2 = utils.load_obj(self.all_posting[idx_b2])
    #             # batch_pointer = min(pointer_pd1, pointer_pd2)
    #
    #             # iterate through 2 lists of posting dicts
    #             while idx_b1 < len_b1 and idx_b2 < len_b2:
    #             # while batch_pointer < min(len_b1,len_b2):
    #                 if idx_b1 >= len_b1:
    #                     posting_dict_1 = utils.load_obj(self.all_posting[idx_b1])
    #                     pointer_pd1 = 0
    #                 elif idx_b2 >= len_b2:
    #                     posting_dict_2 = utils.load_obj(self.all_posting[idx_b2])
    #                     pointer_pd2 = 0
    #
    #                 keys_1 = list(posting_dict_1.keys())
    #                 keys_2 = list(posting_dict_2.keys())
    #
    #                 # iterate through 2 posting dicts
    #                 for comp_idx in enumerate(keys_1 if len(keys_1) < len(keys_2) else keys_2):
    #                     # term in posting 1 < term in posting 2
    #                     term_1, term_2 = keys_1[comp_idx], keys_2[comp_idx]
    #                     if term_1 < term_2:
    #                         merged_posting[term_1] = posting_dict_1[term_1]
    #                         pointer_pd1 += 1
    #                         # self.inverted_idx[term_1][1?] = self.posting_files_counter
    #                     elif term_1 > term_2:
    #                         merged_posting[term_2] = posting_dict_1[term_2]
    #                         pointer_pd2 += 1
    #                         # self.inverted_idx[term_2][1?] = self.posting_files_counter
    #                     # else: # term1 == term2
    #
    #                     if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
    #                         merged_posting = self.helper_save_posting(merged_posting, batch_merged_list)
    #
    #                 # check which posting dict is finished
    #                 if comp_idx  >= len(keys_1):
    #                     idx_b1 += 1
    #                 elif comp_idx >= len(keys_2):
    #                     idx_b2 += 1
    #
    #         i += 2
    #
    #     self.all_posting = updated_posting_list

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
        # for the first iteration
        posting_dict_1 = utils.load_obj(str(left[idx_left]))
        posting_dict_2 = utils.load_obj(str(right[idx_right]))
        keys_1 = list(posting_dict_1.keys())
        keys_2 = list(posting_dict_2.keys())
        pointer_pd1 = pointer_pd2 = 0
        merged_posting = OrderedDict()

        # iterate through 2 lists of posting dicts
        while idx_left < len(left) and idx_right < len(right):

            # iterate through 2 posting dictionaries
            while pointer_pd1 < len(keys_1) and pointer_pd2 < len(keys_2):
                term_1, term_2 = keys_1[pointer_pd1], keys_2[pointer_pd2]
                if term_1 < term_2:
                    merged_posting[term_1] = posting_dict_1[term_1]
                    pointer_pd1 += 1
                    self.inverted_idx[term_1][1] = self.posting_files_counter

                elif term_1 > term_2:
                    merged_posting[term_2] = posting_dict_2[term_2]
                    pointer_pd2 += 1
                    self.inverted_idx[term_2][1] = self.posting_files_counter

                else: # term1 == term2
                    tweets_1, tweets_2 = posting_dict_1[term_1], posting_dict_2[term_2]
                    merged_tweets = []
                    tweets_1_i = tweets_2_i = 0
                    while tweets_1_i < len(tweets_1) and tweets_2_i < len(tweets_2):
                        if tweets_1[tweets_1_i] <= tweets_2[tweets_2_i]:
                            merged_tweets.append(tweets_1[tweets_1_i])
                            tweets_1_i += 1
                        else:
                            merged_tweets.append(tweets_2[tweets_2_i])
                            tweets_2_i += 1
                    if tweets_1_i == len(tweets_1):
                        merged_tweets.extend(tweets_2[tweets_2_i:])
                    else:
                        merged_tweets.extend(tweets_1[tweets_1_i:])

                    merged_posting[term_1] = merged_tweets

                    pointer_pd1 += 1
                    pointer_pd2 += 1
                    self.inverted_idx[term_1][1] = self.posting_files_counter

                if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                    merged_posting = self.save_in_merge(merged_posting, merged_list)

            # if posting from left list is finished
            if pointer_pd1 == len(keys_1):
                # there are more posting dicts in left
                if idx_left < len(left)-1:
                    idx_left += 1
                    pointer_pd1 = 0
                    posting_dict_1 = utils.load_obj(str(left[idx_left]))
                    keys_1 = list(posting_dict_1.keys())
                # else:
                #     if idx_right < len(right):
                #         # copying all leftovers from unfinished posting dict
                #         while pointer_pd2 < len(keys_2):
                #             if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                #                 merged_posting = self.save_in_merge(merged_posting, merged_list)
                #             merged_posting[keys_2[pointer_pd2]] = posting_dict_2[keys_2[pointer_pd2]]
                #             pointer_pd2 += 1

            if pointer_pd2 == len(keys_2):
                if idx_right < len((right))-1:
                    idx_right += 1
                    pointer_pd2 = 0
                    posting_dict_2 = utils.load_obj(str(right[idx_right]))
                    keys_2 = list(posting_dict_2.keys())
                # else:
                #     if idx_left < len(left):
                #         # copying all leftovers from unfinished posting dict
                #         while pointer_pd1 < len(keys_1):
                #             if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                #                 merged_posting = self.save_in_merge(merged_posting, merged_list)
                #             merged_posting[keys_1[pointer_pd1]] = posting_dict_1[keys_1[pointer_pd1]]
                #             pointer_pd1 += 1

        # need to check if finish last dict in left instead of copying it again

        posting_dict_2 = utils.load_obj(str(right[idx_right]))
        keys_1 = list(posting_dict_1.keys())
        keys_2 = list(posting_dict_2.keys())
        pointer_pd1 = pointer_pd2 = 0
        merged_posting = OrderedDict()

        # left list is not finished
        while idx_left < len(left)-1:
            # copying all leftovers from unfinished posting dict
            while pointer_pd1 < len(keys_1)-1:
                if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                    merged_posting = self.save_in_merge(merged_posting, merged_list)
                merged_posting[keys_1[pointer_pd1]] = posting_dict_1[keys_1[pointer_pd1]]
                pointer_pd1 += 1
            idx_left += 1
            if idx_left < len(left)-1:
                posting_dict_1 = utils.load_obj(str(left[idx_left]))
                pointer_pd1 = 0

        # right list is not finished
        while idx_right < len(right)-1:
            # copying all leftovers from unfinished posting dict
            while pointer_pd2 < len(keys_2)-1:
                if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                    merged_posting = self.save_in_merge(merged_posting, merged_list)
                merged_posting[keys_2[pointer_pd2]] = posting_dict_2[keys_2[pointer_pd2]]
                pointer_pd2 += 1
            idx_right += 1
            if idx_right < len(right)-1:
                posting_dict_2 = utils.load_obj(str(right[idx_right]))
                pointer_pd2 = 0

        # if idx_left == len(left):
        #     merged_list.extend(right[idx_right:])
        # if idx_right == len(right):
        #     merged_list.extend(left[idx_left:])

        return merged_list


    # def merge_leftovers(self, longer_list, idx_list, idx_dict, merged_dict):



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
        # num_of_threads = 2 ** n
        # instantiate a Pool of workers
        # pool = Pool(processes = num_of_threads)
        # Now we have a bunch of sorted sublists.  while there is more than
        # one, combine them with merge.
        while len(self.all_posting) > 1:
            # get sorted sublist pairs to send to merge
            list_of_pairs = [(self.all_posting[i], self.all_posting[i + 1]) \
                    for i in range(0, len(self.all_posting), 2)]
            # self.all_posting = pool.map(self.merge_wrap, list_of_pairs)
            test = self.merge_wrap(list_of_pairs[0])
        # Since we start with numproc a power of two, there will always be an
        # even number of sorted sublists to pair up, until there is only one.
        self.all_posting = self.all_posting[0]


    # Calculate idf for each term in inverted index after finish indexing
    def calculate_idf(self, N):
        for term, df in self.inverted_idx.items():
            idf = math.log2(N/df)
            self.inverted_idx[term] = idf

