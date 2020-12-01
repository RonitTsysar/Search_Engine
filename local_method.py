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

        self.correlation_matrix = []
       # {wi : {doc1:tf1, doc3:tf3},  wj: {doc2:tf2, doc3:tf3}}
        self.relevant_docs_per_term = {}

    def expand_query(self, query, round_1):

        all_unique_terms = set()
        relevent_tweets_id = [i[0] for i in round_1]

        for doc_name in self.inverted_docs.keys():
            inersection_temp = []
            if len(relevent_tweets_id) == 0:
                break
            self.loaded_doc = utils.load_obj(self.config.get_savedFileMainFolder() + '\\doc' + str(doc_name))
            doc_ids_in_loaded_file = self.loaded_doc.keys()
            # all tweets in loadded doc
            inersection_temp = list(set(list(doc_ids_in_loaded_file)) & set(relevent_tweets_id))

            # remove inersection tweets from tweets_contain_term
            temp = [doc for doc in relevent_tweets_id if doc not in inersection_temp]
            relevent_tweets_id = temp

            for tweet_id in inersection_temp:
                unique_terms = self.loaded_doc[tweet_id][0]
                all_unique_terms.update(unique_terms)

        n = len(all_unique_terms)

        for i, term in enumerate(all_unique_terms):
            try:
                posting_name = self.inverted_index[term][1]
            except:
                try:
                    posting_name = self.inverted_index[term.lower()][1]
                except:
                    continue
            posting_dict = utils.load_obj(self.config.get_savedFileMainFolder() + "\\" + str(posting_name))
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
                devide_val = float(self.correlation_matrix[i][i]) + float(self.correlation_matrix[j][j]) - float(self.correlation_matrix[i][j])
                if devide_val == 0:
                    self.correlation_matrix[i][j] = 0
                else:
                    self.correlation_matrix[i][j] = float(self.correlation_matrix[i][j]) / float((self.correlation_matrix[i][i]) + float(self.correlation_matrix[j][j]) - float(self.correlation_matrix[i][j]))


        for index in query_indexes:
            term_list = self.correlation_matrix[index]
            del term_list[index]
            max_value = max(term_list)
            max_index = self.correlation_matrix[index].index(max_value)
            query += ' ' + all_terms[max_index]

        return query

    def calculate_Cij(self, wi_tf_dict, wj_tf_dict):
        cij = 0
        for doc_id in wi_tf_dict:
            if doc_id in wj_tf_dict:
                cij += wi_tf_dict[doc_id] * wj_tf_dict[doc_id]
        return cij
