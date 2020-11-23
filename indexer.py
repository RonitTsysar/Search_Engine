import math
import pickle
import bisect
from collections import OrderedDict


class Indexer:

    TERM_NUM_IN_POSTING = 30000

    def __init__(self, config):
        # STRUCTURE OF INDEX
        # inverted_idx - {term : df} ----------> # inverted_idx - {term : idf}
        # inverted_idx - {term : [df, idf, total_tf]} ???
        # postingDict - {term : {tweet_id: [normalized_tf, tf, max_tf, unique_amount]}}

        # self.inverted_idx = OrderedDict()
        # self.posting_dict = OrderedDict()
        self.inverted_idx = {}
        self.posting_dict = {}
        self.config = config

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
                    # self.posting_dict[term] = {}
                    # self.posting_dict[term] = OrderedDict()
                else:
                    self.inverted_idx[term] += 1

                # if term not in self.posting_dict.keys():
                    # self.posting_dict[term] = {}

                tf = document_dictionary[term]
                normalized_tf = tf/document.max_tf  # or float(tf/document.max_tf)
                # print(self.posting_dict[term].keys())
                # self.posting_dict[term][document.tweet_id] = [normalized_tf, tf, document.max_tf, document.unique_terms_amount]

                # bisect.insort - keep the list sorted
                if term not in self.posting_dict.keys():
                    self.posting_dict[term] = [(document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount)]
                else:
                    bisect.insort(self.posting_dict[term], (document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount))
                self.num_of_terms_in_posting += 1
            except:
                # print(self.posting_dict[term][document.tweet_id])
                print('problem with the following key {}'.format(term[0]))


            ################################################################
            #                    save to files - Ronit
            ################################################################
            # saving files with pickle - TODO - give path to save this files
            if self.num_of_terms_in_posting == Indexer.TERM_NUM_IN_POSTING:
                # TODO - RONIT - bisect - check how to keep list sorted by doc_id
                # sort keys(terms)
                self.posting_dict = {key: self.posting_dict[key] for key in sorted(self.posting_dict)}
                with open(f'posting{self.posting_files_counter}.pickle', 'wb') as file:
                    self.posting_files_counter += 1
                    pickle.dump(self.posting_dict, file)
                # clean up
                self.num_of_terms_in_posting = 0
                self.posting_dict = {}


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



    # Calculate idf for each term in inverted index after finish indexing
    def calculate_idf(self, N):
        for term, df in self.inverted_idx.items():
            idf = math.log2(N/df)
            self.inverted_idx[term] = idf

        # map(lambda x,n: math.log2(n/x[0]), self.inverted_idx.iteritems())

    # def calculate_tf_idf(self):
    #     for term, value in self.postingDict.items():
    #         idf = self.inverted_idx[term]
    #         tf_idf = value[0] * idf
    #         self.postingDict[term][tweet_id]