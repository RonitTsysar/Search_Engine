import os
import pandas as pd


class ReadFile:
    def __init__(self, corpus_path):
        self.corpus_path = corpus_path

    def read_corpus(self):
        for root, dirs, files in os.walk(self.corpus_path):
            for file in files:
                if file.endswith(".parquet"):
                    full_path = os.path.join(self.corpus_path, os.path.join(root, file))
                    df = pd.read_parquet(full_path, engine="pyarrow")
                    yield df.values.tolist()
