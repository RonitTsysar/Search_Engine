import search_engine
import utils

if __name__ == '__main__':
    corpus_path = 'C:\\Gal\\University\\Third_year\\semA\\InformationRetrieval\\SearchEngineProject\\Data\\Data'
    output_path = 'out'
    stemming = True
    queries = ['Dr. Anthony Fauci wrote in a 2005 paper published in Virology Journal that hydroxychloroquine was effective in treating SARS.']
    # queries = 'queries.txt'
    num_docs_to_retrieve = 2000

    search_engine.main(corpus_path, output_path, stemming, queries, num_docs_to_retrieve)