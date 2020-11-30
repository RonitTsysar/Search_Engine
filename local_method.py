import utils
from collections import defaultdict

class local_method:

    def __init__(self, inverted_docs, inverted_index):
        """
        :param inverted_index: dictionary of inverted index
        """
        self.inverted_docs = inverted_docs
        self.inverted_index = inverted_index
        self.tf_vector_per_doc = {}

        self.loaded_doc = None
        self.loaded_doc_num = None

    def expand_query(self, query, round_1):
        all_unique_terms = set()
        for doc_tuple in round_1:
            tweet_id = doc_tuple[0]
            doc_posting_name = self.inverted_docs[tweet_id]
            if doc_posting_name != self.loaded_doc_num:
                self.loaded_doc = utils.load_obj('doc' + str(doc_posting_name))
                self.loaded_doc_num = doc_posting_name

            unique_terms = self.loaded_doc[tweet_id][0]
            all_unique_terms.update(unique_terms)

        n = len(all_unique_terms)

        data = {}
        for i, term in enumerate(all_unique_terms):
            try:
                posting_name = self.inverted_index[term][1]
            except:
                try:
                    posting_name = self.inverted_index[term.lower()][1]
                except:
                    continue
            posting_dict = utils.load_obj(str(posting_name))
            tweets_contain_term = posting_dict[term]

            # from list to dict
            tweets_contain_term_dict = defaultdict(list)
            for i, j, k in tweets_contain_term:
                tweets_contain_term_dict[i].append(k)

            # create term in data - {wi : {doc1:tf1, doc3:tf3},  wj: {doc2:tf2, doc3:tf3}}
            data[term] = {}
            for tweet_tuple in round_1:
                tweet_id = tweet_tuple[0]
                if tweet_id in tweets_contain_term_dict:
                    data[term][tweet_id] = tweets_contain_term_dict[tweet_id][0]

        w = list(data.keys())
        l = len(w)
        fat_mat = []
        query_indexes = []
        query = query
        for i in range(l):
            fat_mat.append([])
            if w[i] in query:
                query_indexes.append(i)
            for j in range(l):
                li = data[w[i]]
                lj = data[w[j]]
                fat_mat[i].append(self.calculate_Cij(li, lj))

        # normalization
        for i in range(l):
            for j in range(l):
                v = float((fat_mat[i][i]) + float(fat_mat[j][j]) - float(fat_mat[i][j]))
                if v == 0:
                    fat_mat[i][j] = 0
                else:
                    fat_mat[i][j] = float(fat_mat[i][j]) / float((fat_mat[i][i]) + float(fat_mat[j][j]) - float(fat_mat[i][j]))


        for index in query_indexes:
            temp_list = fat_mat[index]
            del temp_list[index]
            max_value = max(temp_list)
            max_index = fat_mat[index].index(max_value)
            print(w[max_index])
            query += ' ' + w[max_index]

        return query

    def calculate_Cij(self, li, lj):
        value = 0
        for doc_id in li:
            if doc_id in lj:
                value += li[doc_id] * lj[doc_id]
        return value


    # doc_matrix = np.fromfunction(lambda i, j: i * j, (5, 5))