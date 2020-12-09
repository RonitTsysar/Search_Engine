import utils
from collections import defaultdict

class local_method:

    def __init__(self, config, inverted_docs, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.config = config
        self.inverted_docs = inverted_docs
        self.inverted_index = inverted_index
        self.tf_vector_per_doc = {}

        self.loaded_doc = None
        self.loaded_doc_num = None
        self.loaded_posting_name = None

        self.correlation_matrix = []
        # {wi : {doc1:tf1, doc3:tf3},  wj: {doc2:tf2, doc3:tf3}}
        self.relevant_docs_per_term = {}

    def expand_query(self, query, round_1):

        query_set = set()
        query_set.update(query.split(' '))

        all_unique_terms = set()
        relevent_tweets_id = {}
        for tup in round_1:
            relevent_tweets_id[tup[0]] = self.inverted_docs[tup[0]]
        # sort by value
        relevent_tweets_id = {k: v for k, v in sorted(relevent_tweets_id.items(), key=lambda item: item[1])}

        # create unique_terms set
        for tweet in relevent_tweets_id.items():
            tweet_posting = tweet[1]
            tweet_id = tweet[0]
            # load suitable posting
            if self.loaded_doc_num is None or self.loaded_doc_num != tweet_posting:
                self.loaded_doc = utils.load_obj(self.config.get_savedFileMainFolder() + '\\doc' + str(tweet_posting))
                self.loaded_doc_num = tweet_posting

            unique_terms = self.loaded_doc[tweet_id][0]
            all_unique_terms.update(unique_terms)

        # n = len(all_unique_terms)

       ################################################################################################################

        for i, term in enumerate(all_unique_terms):
            try:
                posting_name = self.inverted_index[term][1]
            except:
                try:
                    posting_name = self.inverted_index[term.lower()][1]
                except:
                    continue

            if self.loaded_posting_name is None or self.loaded_posting_name != posting_name:
                posting_dict = utils.load_obj(self.config.get_savedFileMainFolder() + "\\" + str(posting_name))
                self.loaded_posting_name = posting_name

            tweets_contain_term = posting_dict[term]

            # from list to dict, convert list of tuple to dict
            # {tweet_id1: [normalized_tf, tf], tweet_id2: [normalized_tf, tf]}
            # TODO - normalized_tf or tf ?!
            tweets_contain_term_dict = defaultdict(list)
            for id, normalized_tf, tf in tweets_contain_term:
                tweets_contain_term_dict[id].append(tf)

            # create term in self.relevant_docs_per_term - {wi : {doc1:tf1, doc3:tf3},  wj: {doc2:tf2, doc3:tf3}}
            self.relevant_docs_per_term[term] = {}
            for tweet_tuple in round_1:
                tweet_id = tweet_tuple[0]
                if tweet_id in tweets_contain_term_dict:
                    self.relevant_docs_per_term[term][tweet_id] = tweets_contain_term_dict[tweet_id][0]

        all_terms = list(self.relevant_docs_per_term.keys())
        query_indexes = []
        query = query
        for i in range(len(all_terms)):
            self.correlation_matrix.append([])
            if all_terms[i] in query:
                query_indexes.append(i)
            for j in range(len(all_terms)):
                wi = all_terms[i]
                wi_tf_dict = self.relevant_docs_per_term[wi]
                wj = all_terms[j]
                wj_tf_dict = self.relevant_docs_per_term[wj]
                self.correlation_matrix[i].append(self.calculate_Cij(wi_tf_dict, wj_tf_dict))

        # normalization
        for i in range(len(all_terms)):
            for j in range(len(all_terms)):
                devide_val = float(self.correlation_matrix[i][i]) + float(self.correlation_matrix[j][j]) - float(
                    self.correlation_matrix[i][j])
                if devide_val == 0:
                    self.correlation_matrix[i][j] = 0
                else:
                    self.correlation_matrix[i][j] = float(self.correlation_matrix[i][j]) / float(
                        (self.correlation_matrix[i][i]) + float(self.correlation_matrix[j][j]) - float(
                            self.correlation_matrix[i][j]))

        for index in query_indexes:
            term_list = self.correlation_matrix[index]
            del term_list[index]
            max_value = max(term_list)
            max_index = self.correlation_matrix[index].index(max_value)
            query_set.add(all_terms[max_index])

        query = ' '.join(str(e) for e in query_set)
        return query

    def calculate_Cij(self, wi_tf_dict, wj_tf_dict):
        cij = 0
        for doc_id in wi_tf_dict:
            if doc_id in wj_tf_dict:
                cij += wi_tf_dict[doc_id] * wj_tf_dict[doc_id]
        return cij
