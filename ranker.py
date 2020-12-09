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
        for tweet, tweet_vector in relevant_docs.items():
            cosine_sim = dot(tweet_vector, query_vector) / (norm(tweet_vector) * norm(query_vector))
            relevant_docs[tweet] = cosine_sim
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
