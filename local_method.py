import utils
import numpy as np

class local_method:

    def __init__(self, inverted_docs, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.inverted_docs = inverted_docs
        self.inverted_index = inverted_index
        self.tf_vector_per_doc = {}

    def expand_query(self, query, round_1):
        all_unique_terms = set()
        for doc_tuple in round_1:
            tweet_id = doc_tuple[0]
            doc_posting_name = self.inverted_docs[tweet_id]
            docs_posting = utils.load_obj('doc' + str(doc_posting_name))
            unique_terms = docs_posting[tweet_id][0]
            all_unique_terms.add(unique_terms)

        n = len(all_unique_terms)
        # correlation_matrix =
        for idx, term in enumerate(all_unique_terms):
            posting_name = self.inverted_index[term][1]
            posting_dict = utils.load_obj(str(posting_name))
            tweets_contain_term = posting_dict[term]

            for tweet_tuple in tweets_contain_term:
                tweet_id = tweet_tuple[0]
                tf = tweet_tuple[2]
                if self.tf_vector_per_doc[tweet_id] is None:
                    self.tf_vector_per_doc[tweet_id] = np.zeros(n, dtype = float)
                self.tf_vector_per_doc[tweet_id][idx] = tf

        print()



            # doc_matrix = np.fromfunction(lambda i, j: i * j, (5, 5))