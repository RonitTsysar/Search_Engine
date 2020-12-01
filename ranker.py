from numpy import dot
from numpy.linalg import norm

class Ranker:

    def __init__(self):
        pass

    @staticmethod
    def rank_relevant_docs(relevant_docs, query_vector, avg_doc_len):
        """
        This function provides rank for each relevant document and sorts them by their scores.
        The current score considers solely the number of terms shared by the tweet (full_text) and query.
        :param relevant_doc: dictionary of documents that contains at least one term from the query.
        :return: sorted list of documents by score
        """
        # relevant_docs = {tweet_id : [vec tf-idf for cosine, [vec tf,len_doc for BM25]]}
        # tweet_tuple = (tweet_id, normalized_tf, tf, document.max_tf, document.unique_terms_amount, len_doc)

        k, b = 1.5, 0.75
        for tweet, tweet_data in relevant_docs.items():
            cosine_tweet_vector = tweet_data[0]
            cosine_sim = dot(cosine_tweet_vector, query_vector) / (norm(cosine_tweet_vector) * norm(query_vector))

            BM25_tweet_vector = tweet_data[1][0]
            total_BM25 = 0
            for idx, tf in enumerate(BM25_tweet_vector):
                tf_idf = cosine_tweet_vector[idx]
                doc_len = tweet_data[1][1]

                upper = tf_idf * (k + 1)
                below = tf + k*(1 - b + b * (doc_len/avg_doc_len))
                total_BM25 += upper/ below

            relevant_docs[tweet] = cosine_sim
            # relevant_docs[tweet] = 0.8*cosine_sim + 0.2*total_BM25
        return sorted(relevant_docs.items(), key=lambda item: item[1], reverse=True)

    @staticmethod
    def retrieve_top_k(sorted_relevant_doc, k=1):
        """
        return a list of top K tweets based on their ranking from highest to lowest
        :param sorted_relevant_doc: list of all candidates docs.
        :param k: Number of top document to return
        :return: list of relevant document
        """
        return sorted_relevant_doc[:k]
