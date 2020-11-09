import os
import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_file(self, file_name):
        """
        This function is reading a parquet file contains several tweets
        The file location is given as a string as an input to this function.
        :param file_name: string - indicates the path to the file we wish to read.
        :return: a dataframe contains tweets.
        """
        full_path = os.path.join(self.corpus_path, file_name)
        df = pd.read_parquet(full_path, engine="pyarrow")
        return df.values.tolist()

    def read_corpus(self):
        """
        This function is reading the whole corpus data using read_file function
        :return: documents_list contains tweets df.
        """
        files_list = []
        for root, dirs, files in os.walk(self.corpus_path):
            for file in files:
                if file.endswith(".parquet"):
                    files_list.append(self.read_file(os.path.join(root, file)))
        return files_list


