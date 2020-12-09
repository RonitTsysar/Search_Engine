from parser_module import Parse
from ranker import Ranker
import utils
import numpy as np

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

        self.loaded_posting = None
        self.loaded_posting_name = None
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

        posting_query_dict = {}
        for term in query_dict:
            # we have that try because of the entities problem
            try:
                posting_query_dict[term] = self.inverted_index[term][1]
            except:
                pass
        # sort by value
        posting_query_dict = {k: v for k, v in sorted(posting_query_dict.items(), key=lambda item: item[1])}

        relevant_docs = {}
        query_vector = np.zeros(len(query_dict), dtype=float)

        for indx, item in enumerate(posting_query_dict.items()):
            try:
                term = item[0]
                posting_name = item[1]

                # load suitable posting
                if self.loaded_posting_name is None or self.loaded_posting_name != posting_name:
                    self.loaded_posting = utils.load_obj(self.config.get_savedFileMainFolder() + "\\" + str(posting_name))
                    self.loaded_posting_name = posting_name

                for tup in self.loaded_posting[term]:
                    tweet_id = tup[0]

                    if tweet_id not in relevant_docs.keys():
                        relevant_docs[tweet_id] = np.zeros(len(query_dict), dtype=float)

                    tf_tweet = tup[1]
                    idf = self.inverted_index[term][-1]
                    relevant_docs[tweet_id][indx] = tf_tweet * idf

                    tf_query = query_dict[term]
                    query_vector[indx] = tf_query * idf
            except:
                pass
        return relevant_docs, query_vector


