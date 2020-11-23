import pickle

class Indexer:

    DOCS_NUM_IN_POSTING = 500

    def __init__(self, config):
        self.inverted_idx = {}
        self.postingDict = {}
        self.config = config

        self.posting_files_counter = 1
        self.num_of_files_in_posting = 0
        # STRUCTURE OF INDEX
        # inverted_idx - {term : [df, total_tf?]}
        # postingDict - {term : {tweet_id: [tf, max_tf, amount_unique]}}

    def add_new_doc(self, document):
        """
        This function perform indexing process for a document object.
        Saved information is captures via two dictionaries ('inverted index' and 'posting')
        :param document: a document need to be indexed.
        :return: -
        """

        document_dictionary = document.term_doc_dictionary
        # Go over each term in the doc
        self.num_of_files_in_posting += 1

        for term in document_dictionary.keys():
            try:
                # Update inverted index and posting
                if term not in self.inverted_idx.keys():
                    # without total_tf
                    # self.inverted_idx[term] = 1

                    # with total_tf
                    self.inverted_idx[term] = [1, 0]
                    self.postingDict[term] = {}

                # updates df
                else:
                    # self.inverted_idx[term] += 1  # without total_tf
                    self.inverted_idx[term][0] += 1  # with total_tf

                # TODO - do we need to save total tf (from practice) ??
                tf = len(document_dictionary[term])
                self.inverted_idx[term][1] += tf

                # self.postingDict[term].append((document.tweet_id, document_dictionary[term]))

                # TODO - decide if save in term dict parser only location/ tf+location
                # self.postingDict[term][document.tweet_id] = [[document_dictionary[term][0], document.max_tf, len(document.unique_terms)]]
                self.postingDict[term][document.tweet_id] = [tf, document.max_tf, len(document.unique_terms)]

            except:
                print('problem with the following key {}'.format(term[0]))

        ################################################################
        #                    save to files - Ronit
        ################################################################
        # saving files with pickle - TODO - give path to save this files
        if self.num_of_files_in_posting == Indexer.DOCS_NUM_IN_POSTING:
            # TODO - RONIT - bysect - check how to keep list sorted by doc_id
            # sort before save
            self.postingDict = {key: self.postingDict[key] for key in sorted(self.postingDict)}
            with open(f'posting{self.posting_files_counter}.pickle', 'wb') as file:
                self.posting_files_counter += 1
                pickle.dump(self.postingDict, file)
            # clean up
            self.num_of_files_in_posting = 0
            self.postingDict = {}

