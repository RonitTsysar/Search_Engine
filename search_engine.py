from local_method import local_method
from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import time
from tqdm import tqdm

# TODO - check if it's ok to add it here!


def run_engine(with_stem):
    """
    :return:
    """
    config = ConfigClass()
    r = ReadFile(corpus_path=config.get__corpusPath())
    p = Parse(with_stem)
    indexer = Indexer(config)
    number_of_documents = 0
    number_of_files = 0
    total_len_docs = 0
    avg_doc_len = 0

    is_last = False
    for i, file in enumerate(r.read_corpus()):
        # Iterate over every document in the file
        number_of_files += 1
        # is_last = False
        for idx, document in tqdm(enumerate(file)):
            # parse the document
            parsed_document = p.parse_doc(document)
            number_of_documents += 1
            total_len_docs += parsed_document.doc_length
            indexer.add_new_doc(parsed_document)

    indexer.check_last()
    indexer.merge_sort_parallel(3)
    indexer.calculate_idf(number_of_documents)
    avg_doc_len = total_len_docs/number_of_documents
    print('Finished parsing and indexing. Starting to export files')

    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    # TODO - DELETE!
    # utils.save_obj(indexer.posting_dict, "posting")
    utils.save_obj(indexer.docs_inverted, "docs_inverted")
    return avg_doc_len

def load_index():
    inverted_index = utils.load_obj("inverted_idx")
    print('Load inverted index')
    return inverted_index

def load_docs_index():
    inverted_docs = utils.load_obj("docs_inverted")
    print('Load inverted docs index')
    return inverted_docs


def search_and_rank_query(query, inverted_index, inverted_docs, k, avg_doc_len, with_stem):
    p = Parse(with_stem)
    query_as_list = p.parse_sentence(query)[0]
    searcher = Searcher(inverted_index, inverted_docs, with_stem)
    query_dict = searcher.get_query_dict(query_as_list)
    relevant_docs, query_vector = searcher.relevant_docs_from_posting(query_dict)
    ranked_docs = searcher.ranker.rank_relevant_docs(relevant_docs, query_vector, avg_doc_len)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)

    # # TODO - DELETE!!!
    # ranked = searcher.ranker.retrieve_top_k(ranked_docs, k)
    # for doc_tuple in ranked:
    #     print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))


def main(with_stem):
    # run_engine(with_stem)
    # TODO - we need to create searcher&parser here instead of inside method search_and_rank_query
    # searcher = Searcher(inverted_index, with_stem)
    # p = Parse(with_stem)

    avg_doc_len = run_engine(with_stem)
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    inverted_docs = load_docs_index()

    # TODO - check if it's ok to change parameters and
    # TODO - Decide k=1000 round_1 we? need to match for the requested final k (instructions 2000 top)
    round_1 = search_and_rank_query(query, inverted_index, inverted_docs, 1000, avg_doc_len, with_stem)
    local_method_ranker = local_method(inverted_docs, inverted_index)
    expanded_query = local_method_ranker.expand_query(query, round_1)
    for doc_tuple in search_and_rank_query(expanded_query, inverted_index, inverted_docs, k, avg_doc_len, with_stem):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
