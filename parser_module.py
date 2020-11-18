import re
from urllib.parse import urlparse
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
import timeit
from itertools import chain

class Parse:

    THOUSAND = 1000
    MILLION = 1000000
    BILLION = 1000000000
    TRILLION = 1000000000000

    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.stop_words.extend(['!', ':', '&'])

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
    def parse_url(self, token):
        url = re.findall(r"[\w'|.]+", token)

        for i, elem in enumerate(url):
            if 'www' in elem:
                split_address = url[i].split('.', 1)
                url[i] = split_address[1]
                url.insert(i, split_address[0])
        return url

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

        tokenized_text = []
        text_tokens = word_tokenize(text)

        for i, token in enumerate(text_tokens):

            if token in self.stop_words:
                continue

            if self.is_emoji(token):
                continue

            if token == '@':
                if i < (len(text) - 1):
                    tokenized_text.append(token + text_tokens[i+1])

            elif token == '#':
                self.parse_hashtag(tokenized_text, token)


            # TODO - still to finished

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

            if self.has_numbers(token):
                num_type = None
                if i < (len(text_tokens) - 1):
                    num_type = text_tokens[i + 1]
                self.parse_numbers(tokenized_text, token, num_type)

        return tokenized_text


    def get_urls(self, all_urls):
        urls = {}
        for url in all_urls:
            if url:
                urls.update(dict(json.loads(url)))
        return urls

    def get_texts(self, all_texts):
        final_text = ""
        for text in all_texts:
            if text:
               final_text += text
        return final_text

    def is_emoji(self, all_texts):

        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002500-\U00002BEF"  # chinese char
                                   u"\U00002702-\U000027B0"
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   u"\U0001f926-\U0001f937"
                                   u"\U00010000-\U0010ffff"
                                   u"\u2640-\u2642"
                                   u"\u2600-\u2B55"
                                   u"\u200d"
                                   u"\u23cf"
                                   u"\u23e9"
                                   u"\u231a"
                                   u"\ufe0f"  # dingbats
                                   u"\u3030"
                                   "]+", flags=re.UNICODE)
        return re.match(emoji_pattern, all_texts)

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
        # indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        # retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        # quote_indice = doc_as_list[10]
        retweet_quoted_text = doc_as_list[11]
        retweet_quoted_urls = doc_as_list[12]
        # retweet_quoted_indices = doc_as_list[13]
        term_dict = {}

        # TODO delete after QA
        # print(f'tweet_id -> {tweet_id}')
        # print(f'tweet_date -> {tweet_date}')
        # print('--- full_text ---')
        # print(full_text)
        # print('-----------------')
        # print('--- url ---')
        # print(url)
        # print('-----------------')
        # print('--- indices ---')
        # print(indices)
        # print('-----------------')
        # print('--- retweet_text ---')
        # print(retweet_text)
        # print('-----------------')
        # print('--- retweet_url ---')
        # print(retweet_url)
        # print('-----------------')
        # print('--- retweet_indices ---')
        # print(retweet_indices)
        # print('-----------------')
        # print('--- quote_text ---')
        # print(quote_text)
        # print('-----------------')
        # print('--- quote_url ---')
        # print(quote_url)
        # print('-----------------')
        # print('--- quote_indice ---')
        # print(quote_indice)
        # print('-----------------')
        # print('--- retweet_quoted_text ---')
        # print(retweet_quoted_text)
        # print('-----------------')
        # print('--- retweet_quoted_urls ---')
        # print(retweet_quoted_urls)
        # print('-----------------')
        # print('--- retweet_quoted_indices ---')
        # print(retweet_quoted_indices)
        # print('-----------------')

        tokenized_text = []
        # parse all urls
        urls = self.get_urls([url, retweet_url, quote_url, retweet_quoted_urls])
        for url in urls.values():
            tokenized_text += self.parse_url(url)

        all_texts = self.get_texts([full_text, quote_text, retweet_quoted_text])
        # all_texts = self.remove_emojis(all_texts)

        # TODO - maybe remove urls here
        tokenized_text = self.parse_sentence(all_texts)

        doc_length = len(tokenized_text)  # after text operations.

        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1

        # TODO - we need to think what send to the Document
        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)

        return document
