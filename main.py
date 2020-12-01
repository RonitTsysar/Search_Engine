import search_engine


if __name__ == '__main__':
    # corpus_path, output_path, stemming, queries, num_docs_to_retrieve
    corpus_path = 'C:\\Users\\tsysa\\Documents\\University\\3rd-year\\Data-Retrieval\\Data\\date=07-15-2020'
    output_path = 'out'
    stemming = False
    # queries = ['5G helps the spread of Covid-19', 'Herd immunity has been reached.']
    queries = 'queries.txt'
    num_docs_to_retrieve = 10
    search_engine.main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)