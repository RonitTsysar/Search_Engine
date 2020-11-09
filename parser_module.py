import re
from urllib.parse import urlparse

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    MINIMAL_NUMBER_LENGTH = 3

    def __init__(self):
        self.stop_words = stopwords.words('english')

    # TODO - check append instead of +=
    def parse_hashtag(self, all_tokens_list , token):
        final = [token]
        tok = token[1:]

        if '_' in token:
            final += tok.split('_')
        else:
            final += re.findall(r'[a-zA-Z0-9](?:[a-z0-9]+|[A-Z0-9]*(?=[A-Z]|$))', tok)

        final = [x.lower() for x in final]
        all_tokens_list += final

    def parse_url(self, all_tokens_list, token):
        url = re.split('[/://?=]', token)

        for i, elem in enumerate(url):
            if 'www' in elem:
                split_address = url[i].split('.', 1)
                url[i] = split_address[1]
                url.insert(i, split_address[0])
        all_tokens_list += url

    def parse_numbers(self, all_tokens_list, token, num_type):

        # not last token in the test
        if num_type:
            if num_type.lower() == 'percent' or num_type.lower() == 'percentage':
                all_tokens_list.append(token+'%')

        if '%' in token:
            all_tokens_list.append(token)
        if ',' in token:
            token = token.replace(',', '')
            if len(token > Parse.MINIMAL_NUMBER_LENGTH):
                short_num = self.handle_big_numbers(token)

    def has_numbers(self, input_string):
        return any(char.isdigit() for char in input_string)

    # ONLY BIG NUMBERS!
    def handle_big_numbers(self, big_number):
        len = len(big_number)
        # k
        big_number = big_number.strip('0')

        # if len > 3 and len < 7:
        return None

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # text_tokens = word_tokenize(text)
        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]

        tokenized_text = []

        # text_tokens = text.split(' ')
        text_tokens = re.split(' |\n\n|\n', text)
        # need to remove whitespace
        # text_tokens = re.split('[' '][\n\nn]', text)

        for i, token in enumerate(text_tokens):
            if token.startswith('#'):
                self.parse_hashtag(tokenized_text, token)
            elif token.startswith('@'):
                tokenized_text.append(token)
            # starts with http & https
            elif token.startswith('http'):
                self.parse_url(tokenized_text, token)
            elif self.has_numbers(token):
                num_type = None
                if i < (len(text_tokens) - 1):
                    num_type = text_tokens[i]
                self.parse_numbers(tokenized_text, token, num_type)


        return tokenized_text

        # return text_tokens_without_stopwords

    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        retweet_text = doc_as_list[4]
        retweet_url = doc_as_list[5]
        quote_text = doc_as_list[6]
        quote_url = doc_as_list[7]
        term_dict = {}
        tokenized_text = self.parse_sentence(full_text)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document


