import search_engine


if __name__ == '__main__':
    # corpus_path, output_path, stemming, queries, num_docs_to_retrieve
    corpus_path = 'C:\\Gal\\University\\Third_year\\semA\\InformationRetrieval\\SearchEngineProject\\Data\\Data\\date=07-27-2020'
    output_path = 'out'
    stemming = False
    queries = ['5G helps the spread of Covid-19']
    # queries = 'queries.txt'
    num_docs_to_retrieve = 2000
    search_engine.main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)