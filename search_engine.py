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


def run_engine(config):
    """
    :return:
    """
    parser = Parse(config)
    r = ReadFile(corpus_path=config.get__corpusPath())
    indexer = Indexer(config)
    number_of_files = 0

    for i, file in enumerate(r.read_corpus()):
        # Iterate over every document in the file
        number_of_files += 1
        for idx, document in tqdm(enumerate(file)):
            # parse the document
            parsed_document = parser.parse_doc(document)
            indexer.add_new_doc(parsed_document)
    start = time.time()
    indexer.check_last()
    indexer.merge_sort_parallel(3)
    print(f' time after merge sort : {time.time() - start}')
    # TODO - to think about it
    start = time.time()
    indexer.calculate_idf(parser.number_of_documents)
    print(f' time after calculate_idf : {time.time() - start}')
    print('Finished parsing and indexing. Starting to export files')
    # TODO - check how to save
    avg_doc_len = parser.total_len_docs / parser.number_of_documents
    utils.save_obj(avg_doc_len, config.get_savedFileMainFolder() + "\\data")

    utils.save_obj(indexer.inverted_idx, config.get_savedFileMainFolder() + "\\inverted_idx")
    utils.save_obj(indexer.docs_inverted, config.get_savedFileMainFolder() + "\\docs_inverted")

def load_index(config):
    inverted_index = utils.load_obj(config.get_savedFileMainFolder() + "\\" + "inverted_idx")
    print('Load inverted index')
    return inverted_index

def load_docs_index(config):
    inverted_docs = utils.load_obj(config.get_savedFileMainFolder() + "\\" + "docs_inverted")
    print('Load inverted docs index')
    return inverted_docs


def search_and_rank_query(config, query, inverted_index, inverted_docs, k, avg_doc_len):
    p = Parse(config)
    query_as_list = p.parse_sentence(query)[0]
    searcher = Searcher(config, inverted_index, inverted_docs)
    query_dict = searcher.get_query_dict(query_as_list)
    relevant_docs, query_vector = searcher.relevant_docs_from_posting(query_dict)
    ranked_docs = searcher.ranker.rank_relevant_docs(relevant_docs, query_vector, avg_doc_len)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


# def main(with_stem):
def main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve):

    # update configurations
    config = ConfigClass()
    config.set_corpusPath(corpus_path)
    config.set_toStem(stemming)
    config.set_savedFileMainFolder(output_path)

    # run_engine(config)

    # query = input("Please enter a query: ")
    # k = int(input("Please enter number of docs to retrieve: "))

    inverted_index = load_index(config)
    inverted_docs = load_docs_index(config)
    avg_doc_len = utils.load_obj(config.get_savedFileMainFolder() + "\\" + "data")

    if type(queries) is list:
        queries_list = queries
    else:
        queries_list = [line.strip() for line in open(queries, encoding="utf8")]

    for querie in queries_list:
        # TODO - check if it's ok to change parameters and
        # TODO - Decide k=1000 round_1 we? need to match for the requested final k (instructions 2000 top)

        round_1 = search_and_rank_query(config, querie, inverted_index, inverted_docs, 10, avg_doc_len)
        local_method_ranker = local_method(config, inverted_docs, inverted_index)
        expanded_query = local_method_ranker.expand_query(querie, round_1)
        for doc_tuple in search_and_rank_query(config, expanded_query, inverted_index, inverted_docs, num_docs_to_retrieve, avg_doc_len):
            print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
