from reader import ReadFile
from configuration import ConfigClass
from parser_module import Parse
from indexer import Indexer
from searcher import Searcher
import utils
import timeit
from tqdm import tqdm

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

    files_list = r.read_corpus()
    for file in files_list:
        # Iterate over every document in the file
        number_of_files += 1
        parsed_document = p.parse_doc(file[463])
        for idx, document in tqdm(enumerate(file)):
            # print(f' id: {idx}')
            # parse the document
            # print(number_of_documents)
            parsed_document = p.parse_doc(document)
            number_of_documents += 1
            # index the document data
            indexer.add_new_doc(parsed_document)

    print('Finished parsing and indexing. Starting to export files')

    # TODO delete after QA
    print(f'number_of_files : {number_of_files}')
    print(f'number_of_documents : {number_of_documents}')

    utils.save_obj(indexer.inverted_idx, "inverted_idx")
    utils.save_obj(indexer.postingDict, "posting")


def load_index():
    print('Load inverted index')
    inverted_index = utils.load_obj("inverted_idx")
    return inverted_index


def search_and_rank_query(query, inverted_index, k):
    p = Parse()
    query_as_list = p.parse_sentence(query)
    searcher = Searcher(inverted_index)
    relevant_docs = searcher.relevant_docs_from_posting(query_as_list)
    ranked_docs = searcher.ranker.rank_relevant_doc(relevant_docs)
    return searcher.ranker.retrieve_top_k(ranked_docs, k)


def main(with_stem):
    run_engine(with_stem)
    query = input("Please enter a query: ")
    k = int(input("Please enter number of docs to retrieve: "))
    inverted_index = load_index()
    for doc_tuple in search_and_rank_query(query, inverted_index, k):
        print('tweet id: {}, score (unique common words with query): {}'.format(doc_tuple[0], doc_tuple[1]))
