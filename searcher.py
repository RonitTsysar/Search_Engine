from parser_module import Parse
from ranker import Ranker
import utils
import numpy as np
from tqdm import tqdm
from collections import defaultdict

class Searcher:

    def __init__(self, config, inverted_index, inverted_docs):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.config = config
        self.parser = Parse(config)
        self.ranker = Ranker()
        self.inverted_index = inverted_index
        self.inverted_docs = inverted_docs

        self.loaded_doc_name = None
        self.loaded_doc = None

    def get_query_dict(self, tokenized_query):
        # create {term : tf} for query
        max_tf = 1
        query_dict = {}
        for index, term in enumerate(tokenized_query):
            if term not in query_dict:
                query_dict[term] = 1

            else:
                query_dict[term] += 1
                if query_dict[term] > max_tf:
                    max_tf = query_dict[term]

        for term in query_dict:
            query_dict[term] /= max_tf

        return query_dict

    def relevant_docs_from_posting(self, query_dict):

        relevant_docs = {}
        query_vector = np.zeros(len(query_dict), dtype=float)

        for idx, term in tqdm(enumerate(query_dict)):
            try:
                posting_name = self.inverted_index[term][1]

                posting_dict = utils.load_obj(self.config.get_savedFileMainFolder() + "\\" + str(posting_name))
                tweets_contain_term_dict = defaultdict(list)
                for i, j, k in posting_dict[term]:
                    tweets_contain_term_dict[i] = j

                tweets_contain_term__ids = [i[0] for i in posting_dict[term]]

                for doc_name in self.inverted_docs.keys():
                    if len(tweets_contain_term__ids) == 0:
                        break
                    doc_loaded = utils.load_obj(self.config.get_savedFileMainFolder() + '\\doc' + str(doc_name))
                    doc_ids_in_loaded_file = doc_loaded.keys()
                    # all tweets in loadded doc
                    inersection_temp = list(set(list(doc_ids_in_loaded_file)) & set(tweets_contain_term__ids))
                    # remove inersection tweets from tweets_contain_term
                    temp = [doc for doc in tweets_contain_term__ids if doc not in inersection_temp]
                    tweets_contain_term__ids = temp

                    for tweet_id in inersection_temp:
                        if tweet_id not in relevant_docs:
                            doc_len = doc_loaded[tweet_id][-1]
                            relevant_docs[tweet_id] = [np.zeros(len(query_dict), dtype=float),
                                                       [np.zeros(len(query_dict), dtype=float), doc_len]]

                        # TODO - decide if normalized tf or tf
                        tf_tweet = tweets_contain_term_dict[tweet_id]
                        idf = self.inverted_index[term][0]
                        relevant_docs[tweet_id][0][idx] = tf_tweet * idf
                        relevant_docs[tweet_id][1][0][idx] = tf_tweet

                        tf_query = query_dict[term]
                        query_vector[idx] = tf_query * idf
            except:
                print('term {} not found in posting'.format(term))

        return relevant_docs, query_vector



