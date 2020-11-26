from parser_module import Parse
from ranker import Ranker
import utils
import numpy as np

class Searcher:

    def __init__(self, inverted_index, with_stem):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.parser = Parse(with_stem)
        self.ranker = Ranker()
        self.inverted_index = inverted_index

    def get_query_dict(self, tokenized_query):
        # create {term : tf} for query
        max_tf = 1
        query_dict = {}
        for index, term in enumerate(tokenized_query):
            if term not in query_dict.keys():
                query_dict[term] = 1

            else:
                query_dict[term] += 1
                if query_dict[term] > max_tf:
                    max_tf = query_dict[term]

        for term in query_dict:
            query_dict[term] /= max_tf

        return query_dict

    def relevant_docs_from_posting(self, query_dict):
        """
        This function loads the posting list and count the amount of relevant documents per term.
        :param query_dict: query
        :return: dictionary of relevant documents.
        """

        relevant_docs = {}
        query_vector = np.zeros(len(query_dict), dtype=float)

        for idx, term in enumerate(query_dict):
            try: # an example of checks that you have to do

                # TODO - need to load the right posting for each term
                posting_name = self.inverted_index[term][1]
                posting_dict = utils.load_obj(str(posting_name))
                tweets_contain_term = posting_dict[term]

                # tweets_contain_term = posting_dict[term]  #[(document.tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount)]
                for tweet_tuple in tweets_contain_term:
                    tweet_id = tweet_tuple[0]
                    if tweet_id not in relevant_docs.keys():
                        relevant_docs[tweet_id] = np.zeros(len(query_dict), dtype = float)
                    tf_tweet = tweet_tuple[1]
                    idf = self.inverted_index[term][0]
                    relevant_docs[tweet_id][idx] = tf_tweet * idf

                    tf_query = query_dict[term]
                    query_vector[idx] = tf_query * idf

            except:
                print('term {} not found in posting'.format(term))

        return relevant_docs, query_vector


