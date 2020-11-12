import re
from urllib.parse import urlparse

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document


class Parse:

    THOUSAND = 1000
    MILLION = 1000000
    BILLION = 1000000000
    TRILLION = 1000000000000

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.small_big_letters_dict = {}

    def parse_hashtag(self, all_tokens_list, token):
        t = []
        # --> #stay_at_home
        if '_' in token:
            t.append(re.sub(r'_', '', token))
            token = token[1:]
            t += re.split(r'_', token)
        else:
            # --> #stayAtHome
            if not token.isupper():
                t.append(token)
                t += re.findall('[A-Z][^A-Z]*', token)
            # --> #ASD
            else:
                all_tokens_list.append(token)
                return

        t = [x.lower() for x in t]
        all_tokens_list += t

    # TODO - recheck
    def parse_url(self, all_tokens_list, token):
        url = re.findall(r"[\w'|.]+", token)

        for i, elem in enumerate(url):
            if 'www' in elem:
                split_address = url[i].split('.', 1)
                url[i] = split_address[1]
                url.insert(i, split_address[0])
        all_tokens_list += url

    # TODO - recheck
    def parse_numbers(self, all_tokens_list, token, num_type):

        def convert_to_final(token, start, end, type):
            if token in range(start, end):
                token /= start
                if token.is_integer():
                    token = int(token)
                all_tokens_list.append(str(token) + type)

        # not last token in the test
        if num_type:
            l_num_type = num_type.lower()

        if num_type:
            if l_num_type == 'percent' or l_num_type == 'percentage':
                all_tokens_list.append(token+'%')

        if '%' in token:
            all_tokens_list.append(token)
        elif ',' in token:
            token = token.replace(',', '')
        try:
            token = float(token)
        except:
            return
        if num_type:
            if l_num_type.startswith('thousand'):
                token *= Parse.THOUSAND
            elif l_num_type.startswith('million'):
                token *= Parse.MILLION
            elif l_num_type.startswith('billion'):
                token *= Parse.BILLION

        if token in range(0, Parse.THOUSAND):
            if token.is_integer():
                token = int(token)
                if num_type:
                    t = re.match('\d+/\d+', num_type)
                    if t:
                        all_tokens_list.append(f'{token} {t}')
            all_tokens_list.append(str(token))
        elif token in range(Parse.THOUSAND, Parse.MILLION):
            convert_to_final(token, Parse.THOUSAND, Parse.MILLION, 'K')
        elif token in range(Parse.MILLION, Parse.BILLION):
            convert_to_final(token, Parse.MILLION, Parse.BILLION, 'M')
        elif token in range(Parse.BILLION, Parse.TRILLION):
            convert_to_final(token, Parse.BILLION, Parse.TRILLION, 'B')


    def has_numbers(self, input_string):
        return any(char.isdigit() for char in input_string)


    # @Gal
    '''def update_upper_letter_dict(self, token):
        l_token = token.lower()
        if l_token in Parse.upper_letter:
            seen_lower = Parse.upper_letter[l_token]
            if seen_lower == False and token[0].islower():
                Parse.upper_letter[l_token] = True
        else:
            Parse.upper_letter[l_token] = token[0].islower()'''

    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        # text_tokens = word_tokenize(text)
        # text_tokens_without_stopwords = [w.lower() for w in text_tokens if w not in self.stop_words]

        tokenized_text = []

        text_tokens = re.split(' |\n\n|\n', text)
        # need to remove whitespace
        # text_tokens = re.split('[' '][\n\nn]', text)

        for i, token in enumerate(text_tokens):

            # maintain doc
            # TRUE - we sow lower case
            # FALSE - we didnt see lower case
            if token.isalpha():
                if token[0].islower():
                    if token not in self.small_big_letters_dict.keys() or not self.small_big_letters_dict[token]:
                        self.small_big_letters_dict[token] = True
                elif token.lower() not in self.small_big_letters_dict.keys():
                    self.small_big_letters_dict[token.lower()] = False
            # @GAL
            '''if token.isalpha():
                self.update_upper_letter_dict(token)'''

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
                    num_type = text_tokens[i + 1]
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
