import math
import pickle
import bisect
from concurrent.futures.thread import ThreadPoolExecutor
from collections import Counter
import utils
from multiprocessing import Pool
from collections import OrderedDict


class Indexer:

    TERM_NUM_IN_POSTING = 500000
    DOC_NUM_IN_POSTING = 100000

    def __init__(self, config):
        # STRUCTURE OF INDEX

        # inverted_idx - {term : [df, posting_files_counter]} ----------> # inverted_idx - {term : [idf, posting_files_counter]}
        # posting_dict - {term: [(document.tweet_id, normalized_tf, tf)]}
        # tweets_inverted - {tweet_id : tweets_posting_counter}
        # tweets_posting - {tweet_id : [document.unique_terms, document.unique_terms_amount, document.max_tf, document.doc_length]}

        self.inverted_idx = {}
        self.posting_dict = {}
        self.all_posting = []
        self.posting_files_counter = 1
        self.num_of_terms_in_posting = 0

        self.entities = Counter()
        self.small_big = {}
        self.config = config

        # for Local Method
        self.docs_inverted = {}
        self.docs_posting = {}
        self.docs_counter = 1
        self.num_of_docs_in_posting = 0


    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """
        document_dictionary = document.term_doc_dictionary
        # entities as is ->  token
        self.entities.update(document.entities_set)

        # preprocessing for Local Method

        self.docs_posting[document.tweet_id] = [document.unique_terms, document.unique_terms_amount, document.max_tf, document.doc_length]
        self.docs_inverted[document.tweet_id] = self.docs_counter
        self.num_of_docs_in_posting += 1
        if self.num_of_docs_in_posting == Indexer.DOC_NUM_IN_POSTING:
            self.save_doc()

        # Go over each term in the doc
        for term in document_dictionary.keys():
            try:
                # small_big
                # term = lower case
                if term in document.small_big_letters_dict:
                    if term not in self.small_big.keys():
                        self.small_big[term] = document.small_big_letters_dict[term]
                    else:
                        self.small_big[term] = self.small_big[term] and document.small_big_letters_dict[term]

                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    self.inverted_idx[term] = [1, self.posting_files_counter]
                else:
                    self.inverted_idx[term][0] += 1

                tf = document_dictionary[term]
                normalized_tf = tf/document.max_tf

                if term not in self.posting_dict.keys():
                    self.posting_dict[term] = [(document.tweet_id, normalized_tf, tf)]
                else:
                    bisect.insort(self.posting_dict[term], (document.tweet_id, normalized_tf, tf))
                self.num_of_terms_in_posting += 1
            except:
                print('problem with the following key {}'.format(term))

            # saving files with pickle - TODO - give path to save this files
            if self.num_of_terms_in_posting == Indexer.TERM_NUM_IN_POSTING:
                self.save_posting()
        # if is_last:
        #     self.save_posting()
        #     self.save_doc()

    def check_last(self):
        self.save_posting()
        self.save_doc()

    def test_before_merge(self):
        l = []
        for i, name in enumerate(self.all_posting):
            name = name[0]
            print(name)
            dict = utils.load_obj(str(name))
            keys = list(dict.keys())
            l += keys
        set_keys = set(l)
        print()

    def save_posting(self):
        if len(self.posting_dict) > 0:
            # sort keys(terms)
            self.posting_dict = {key: self.posting_dict[key] for key in sorted(self.posting_dict)}
            utils.save_obj(self.posting_dict, str(self.posting_files_counter))
            # clean up
            self.num_of_terms_in_posting = 0
            self.posting_dict = {}
            self.all_posting.append([self.posting_files_counter])
            self.posting_files_counter += 1

    def save_doc(self):
        if len(self.docs_posting) > 0:
            utils.save_obj(self.docs_posting, 'doc' + str(self.docs_counter))
            self.docs_counter += 1
            self.docs_posting = {}


    def save_in_merge(self, merged_posting, merged_list):
        utils.save_obj(merged_posting, str(self.posting_files_counter))
        merged_list.append(self.posting_files_counter)
        self.posting_files_counter += 1
        return {}

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

                # bad entity
                if term_1 in self.entities and self.entities[term_1] < 2:
                    # if self.entities[term_1] < 2:
                    pointer_pd1 += 1
                    # DELETE FROM ALL PLACES
                    if term_1 in self.inverted_idx.keys():
                        del self.inverted_idx[term_1]
                        # del posting_dict_1[term_1]
                    continue

                if term_2 in self.entities and self.entities[term_2] < 2:
                    # if self.entities[term_2] < 2:
                    pointer_pd2 += 1
                    # DELETE FROM ALL PLACES
                    if term_2 in self.inverted_idx.keys():
                        del self.inverted_idx[term_2]
                        # del posting_dict_2[term_2]
                    continue

                # only big letters
                if term_1 in self.small_big and not self.small_big[term_1] and term_1 in self.inverted_idx.keys():
                    old_1 = term_1
                    term_1 = term_1.upper()

                    self.inverted_idx[term_1] = self.inverted_idx[old_1]
                    del self.inverted_idx[old_1]

                    posting_dict_1[term_1] = posting_dict_1[old_1]
                    del self.posting_dict_1[old_1]

                if term_2 in self.small_big and not self.small_big[term_2] and term_2 in self.inverted_idx.keys():
                    old_2 = term_2
                    term_2 = term_2.upper()

                    self.inverted_idx[term_2] = self.inverted_idx[old_2]
                    del self.inverted_idx[term_2]

                    posting_dict_2[term_2] = posting_dict_1[old_2]
                    del self.posting_dict_2[old_2]

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
                idx_left += 1
                # there are more posting dicts in left
                if idx_left < len(left)-1:
                    # idx_left += 1
                    posting_dict_1 = utils.load_obj(str(left[idx_left]))
                    pointer_pd1 = 0
                    keys_1 = list(posting_dict_1.keys())


            if pointer_pd2 == len(keys_2):
                idx_right += 1
                # pointer_pd2 = 0
                if idx_right < len((right)):
                    posting_dict_2 = utils.load_obj(str(right[idx_right]))
                    pointer_pd2 = 0
                    keys_2 = list(posting_dict_2.keys())


        # left list is not finished
        while idx_left < len(left):
            # copying all terms from posting dict
            while pointer_pd1 < len(keys_1):
                if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                    merged_posting = self.save_in_merge(merged_posting, merged_list)
                merged_posting[keys_1[pointer_pd1]] = posting_dict_1[keys_1[pointer_pd1]]
                pointer_pd1 += 1
            idx_left += 1
            if idx_left < len(left):
                posting_dict_1 = utils.load_obj(str(left[idx_left]))
                pointer_pd1 = 0

        # right list is not finished
        while idx_right < len(right):
            # copying all leftovers from unfinished posting dict
            while pointer_pd2 < len(keys_2):
                if len(merged_posting) == Indexer.TERM_NUM_IN_POSTING:
                    merged_posting = self.save_in_merge(merged_posting, merged_list)
                merged_posting[keys_2[pointer_pd2]] = posting_dict_2[keys_2[pointer_pd2]]
                pointer_pd2 += 1
            idx_right += 1
            if idx_right < len(right):
                posting_dict_2 = utils.load_obj(str(right[idx_right]))
                pointer_pd2 = 0

        merged_posting = self.save_in_merge(merged_posting, merged_list)

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
        # num_of_threads = 2 ** n
        # instantiate a Pool of workers
        # pool = ThreadPoolExecutor(num_of_threads)
        # Now we have a bunch of sorted sublists.  while there is more than
        # one, combine them with merge.
        last_odd = None
        while len(self.all_posting) > 1:
            # get sorted sublist pairs to send to merge
            if len(self.all_posting) % 2 != 0:
                last_odd = self.all_posting.pop()
            list_of_pairs = [(self.all_posting[i], self.all_posting[i + 1]) \
                    for i in range(0, len(self.all_posting), 2)]
            # self.all_posting = list(pool.map(self.merge_wrap, list_of_pairs))
            self.all_posting = list(map(self.merge_wrap, list_of_pairs))

            if last_odd:
                self.all_posting.append(last_odd)
                last_odd = None
            # test = self.merge_wrap(list_of_pairs)
        # Since we start with numproc a power of two, there will always be an
        # even number of sorted sublists to pair up, until there is only one.
        self.all_posting = self.all_posting[0]

        #########################################################################
        # # test merge!
        # l = []
        # for i, name in enumerate(self.all_posting):
        #     print(name)
        #     dict = utils.load_obj(str(name))
        #     keys = list(dict.keys())
        #     l += keys
        #
        # for key in l:
        #     if l.count(key) > 1:
        #         print('KAKI')
        #     else:
        #         print(".")
        #########################################################################

    # Calculate idf for each term in inverted index after finish indexing
    def calculate_idf(self, N):
        for val in self.inverted_idx.values():
            val[0] = math.log2(N/val[0])



