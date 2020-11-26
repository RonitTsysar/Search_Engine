from parser_module import Parse
from ranker import Ranker
import utils
import numpy as np

class Searcher:

    def __init__(self, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse()
        self.ranker = Ranker()
        self.inverted_index = inverted_index

    def relevant_docs_from_posting(self, query):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query: query
        :return: dictionary of relevant documents.
        """
        posting = utils.load_obj("posting")
        relevant_docs = {}
        for idx, term in enumerate(query):
            try: # an example of checks that you have to do
                tweets_contain_term = posting[term]  #[(document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount)]
                for tweet_tuple in tweets_contain_term:
                    tweet_id = tweet_tuple[0]
                    if tweet_id not in relevant_docs.keys():
                        relevant_docs[tweet_id] = np.zeros(len(query), dtype = float)
                    tf = tweet_tuple[1]
                    idf = self.inverted_index[term]
                    relevant_docs[tweet_id][idx] = tf * idf

            except:
                print('term {} not found in posting'.format(term))
        return relevant_docs


