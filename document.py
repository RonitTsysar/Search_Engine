class Document:

    def __init__(self, tweet_id, max_tf, entities_set, small_big_letters_dict, unique_terms_amount, tweet_date=None, term_doc_dictionary=None, doc_length=0):
        """
        :param tweet_id: tweet id
        :param tweet_date: tweet date
        :param full_text: full text as string from tweet
        :param url: url
        :param retweet_text: retweet text
        :param retweet_url: retweet url
        :param quote_text: quote text
        :param quote_url: quote url
        :param term_doc_dictionary: dictionary of term and documents.
        :param doc_length: doc length
        """
        self.tweet_id = tweet_id
        self.tweet_date = tweet_date
        self.term_doc_dictionary = term_doc_dictionary
        self.doc_length = doc_length

        self.max_tf = max_tf
        self.entities_set = entities_set
        self.small_big_letters_dict = small_big_letters_dict
        self.unique_terms_amount = unique_terms_amount
