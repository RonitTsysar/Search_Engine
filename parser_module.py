import re
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from stemmer import Stemmer


class Parse:
    THOUSAND = 1000
    MILLION = 1000000
    BILLION = 1000000000
    TRILLION = 1000000000000
    QUANTITIES = {'thousand': 'K', 'thousands': 'K',
                  'million': 'M', 'millions': 'M',
                  'billion': 'B', 'billions': 'B',
                  'trillion': 'TR', 'trillions': 'TR'}
    SIGNS = {'$': '$', 'usd': '$'}
    QUANTITIES_LIST = ['K', 'M', 'B', 'TR']

    def __init__(self, with_stem):
        self.with_stem = with_stem
        self.stemmer = Stemmer()
        self.stop_words = stopwords.words('english')
        self.stop_words.extend(['!', '?', '', ':', ';', '(', ')', '[', ']', '{', '}' '&', 'rt', ' ', '$', '.', '"', '“', "‘", "'", "`", '\'s', '\'ve', ])
        self.stop_words_dict = dict.fromkeys(self.stop_words)

        self.small_big_letters_dict = {}
        # TODO - check if need to save in dict {entity : counter}
        self.entities = []

        self.url_pattern = re.compile('http\S+')
        self.url_www_pattern = re.compile("[/://?=]")
        # TODO - fix numbers pattern
        # self.numbers_pattern_1 = re.compile('\d+[/|.|,]*\d+')
        # self.numbers_pattern_2 = re.compile('[\d+[/|.|,]?\d+]*')
        self.numbers_pattern = re.compile(('^\d+([/|.|,]?\d+)*'))
        # TODO - fix emoji to include all emojis
        self.emojis_pattern = re.compile(pattern="["
                                                u"\U0001F600-\U0001F64F"  # emoticons
                                                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                                u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                                u"\U00002500-\U00002BEF"  # chinese char
                                                u"\U00010000-\U0010ffff"
                                                u"\U0001f926-\U0001f937"
                                                u"\U000024C2-\U0001F251"
                                                u"\U00002702-\U000027B0"
                                                u"\u2640-\u2642"
                                                u"\u200d"
                                                u"\u23cf"
                                                u"\u23e9"
                                                u"\u231a"
                                                u"\ufe0f"
                                                u"\u3030"
                                                u"\u2600-\u2B55"
                                                "]+", flags=re.UNICODE)

    def parse_hashtag(self, all_tokens_list, token):
        t = []
        # --> #stay_at_home
        if '_' in token:
            t.append('#' + re.sub(r'_', '', token))
            t += re.split(r'_', token)
        else:
            # --> #stayAtHome
            if not token.isupper():
                t.append('#' + token)
                t += re.findall('[A-Z][^A-Z]*', token)
            # --> #ASD
            else:
                all_tokens_list.append('#' + token)
                return

        t = [x.lower() for x in t]
        all_tokens_list += t

    def parse_numbers(self, all_tokens_list, token, before_token, after_token, text_tokens):
        def helper(num):
            count = -1
            while num >= 1000:
                num /= 1000
                count += 1
            # fixed the case of 140.000K
            if num.is_integer():
                num = int(num)
                return num, count
            return ("%.3f" % num), count

        if '/' in token:
            all_tokens_list.append(token)
            return
        if ',' in token:
            token = token.replace(',', '')

        try:
            token = float(token)
        except:
            print('token --------------------> ' + token)
            # from this type - 10.07.2020
            all_tokens_list.append(token)
            return

        if token.is_integer():
            token = int(token)

        b_tok = None
        is_pers = None

        if before_token and before_token in Parse.SIGNS:
            b_tok = Parse.SIGNS[before_token]

        if after_token:
            after_token = after_token.lower()

            if after_token in Parse.QUANTITIES:

                if token < 1000:
                    if b_tok:
                        all_tokens_list.append(b_tok + str(token) + Parse.QUANTITIES[after_token])
                        return
                    else:
                        all_tokens_list.append(str(token) + Parse.QUANTITIES[after_token])
                        return
                # if we have after and token > 1000
                num, count = helper(token)
                i = Parse.QUANTITIES_LIST.index(Parse.QUANTITIES[after_token])
                after_token = Parse.QUANTITIES_LIST[i + count]
                all_tokens_list.append(str(num) + after_token)
                return

            if after_token == 'percent' or after_token == 'percentage' or after_token == '%':
                is_pers = True

        if token < 1000:
            final_t = str(token)
        else:
            num, count = helper(token)
            try:
                after = Parse.QUANTITIES_LIST[count]
                final_t = str(num) + after
            except:
                print("prblem in parse numbers: " + token)

        if b_tok:
            all_tokens_list.append(b_tok + str(final_t))
        elif is_pers:
            all_tokens_list.append(str(final_t) + '%')
        else:
            all_tokens_list.append(str(final_t))


    def parse_sentence(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        tokenized_text = []
        text_tokens = word_tokenize(text)
        entity = ''

        for i, term in enumerate(text_tokens):

            token = text_tokens[i]

            if self.with_stem:
                token = self.stemmer.stem_term(token)


            # if token in self.stop_words_dict:
            #     continue

            if token == ' ':
                continue

            # EMOJIS - extract the token without the emojis
            if re.match(self.emojis_pattern, token):
                token = self.emojis_pattern.sub(r'', token)
                tokenized_text.append(token)

                entity = ''
                continue

            if token == '@':
                if i < (len(text_tokens) - 1):
                    tokenized_text.append(token + text_tokens[i + 1])
                    text_tokens[i + 1] = ' ' # skip the next token

                    entity = ''
                    continue

            if token == '#':
                if i < (len(text_tokens) - 1):
                    self.parse_hashtag(tokenized_text, text_tokens[i + 1])
                    text_tokens[i + 1] = ' '  # skip the next token

                    entity = ''
                    continue

            # NUMBERS
            # number_match = self.numbers_pattern_1.match(token) or self.numbers_pattern_2.match(token)
            number_match = self.numbers_pattern.match(token)
            if number_match:
                # Numbers over TR
                if len(token) > 12:
                    tokenized_text.append(token)

                    entity = ''
                    continue
                start, stop = number_match.span()
                if (stop - start) == len(token):
                    before_t = None
                    after_t = None
                    if i < (len(text_tokens) - 1):
                        after_t = text_tokens[i + 1]
                    if i > 0:
                        before_t = text_tokens[i - 1]
                    self.parse_numbers(tokenized_text, token, before_t, after_t, text_tokens)

                    entity = ''
                    continue


            url_match = self.url_pattern.match(token)
            if url_match:
                if i+2 < len(text_tokens):
                    if text_tokens[i+2]:
                        tokenized_text += self.parse_url(text_tokens[i+2])
                        text_tokens[i + 1] = ' '  # skip the next token
                        text_tokens[i + 2] = ' '  # skip the next token

                        entity = ''
                        continue

            # TRUE - we sow lower case
            # FALSE - we didnt see lower case
            # combitation of ENTITY and small_big_letters
            if token.isalpha() and token.lower() not in self.stop_words:
                if token[0].isupper():
                    entity += token + ' '
                    if token.lower() not in self.small_big_letters_dict.keys():
                        self.small_big_letters_dict[token.lower()] = False
                else:
                    if len(entity) > 0:
                        self.entities.append(entity[:-1])
                        entity = ''
                    if token not in self.small_big_letters_dict.keys() or not self.small_big_letters_dict[token]:
                        self.small_big_letters_dict[token] = True

            '''if token.isalpha() and token.lower() not in self.stop_words:
                if token[0].islower():
                    if token not in self.small_big_letters_dict.keys() or not self.small_big_letters_dict[token]:
                        self.small_big_letters_dict[token] = True
                elif token.lower() not in self.small_big_letters_dict.keys():
                    self.small_big_letters_dict[token.lower()] = False

            # ENTITY
            if token.isalpha() and token[0].isupper() and token.lower() not in self.stop_words:
                entity += token + ' '
            else:
                if len(entity) > 0:
                    self.entities.append(entity[:-1])
                    entity = ''
                    '''

            #TODO check if lower is ok here
            # append all regular words
            token = token.lower()
            if token not in self.stop_words_dict:
                tokenized_text.append(token)

        # print(f'tokenized_text --> {tokenized_text}')
        return tokenized_text

    # TODO - fix urls
    # \\date=07-21-2020
    # 'https://www-foxnews-com.cdn.ampproject.org/c/s/www.foxnews.com/media/hydroxychloroquine-could-save-lives-ingraham-yale-professor.amp'
    # def parse_url(self, token):
    #     url = self.url_www_pattern.findall(token)
    #     for i, elem in enumerate(url):
    #         if 'www' in elem:
    #             split_address = url[i].split('.', 1)
    #             try:
    #                 url[i] = split_address[1]
    #                 url.insert(i, split_address[0])
    #             except:
    #                 print("problem with url in tweet: " +token)
    #     return url

    def parse_url(self, token):
        split_url = self.url_www_pattern.split(token)
        if 't.co' in split_url or 'twitter.com' in split_url:
            return [split_url[-1]]
        if len(split_url) > 3 and 'www.' in split_url[3]:
            split_url[3] = split_url[3][4:]
        return [t.lower() for t in split_url if (t != 'https' and t != '')]

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
                final_text += ' ' + text
        return final_text

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
        for (key, value) in urls.items():
            if value:
                tokenized_text += self.parse_url(value)
            elif key:
                tokenized_text += self.parse_url(key)

        all_texts = self.get_texts([full_text, quote_text, retweet_quoted_text])
        # remove urls from text, only if exist in url
        # TODO - think what else to remove
        if len(urls) > 0:
            all_texts = self.url_pattern.sub('', all_texts)

        # handle url
        tokenized_text = self.parse_sentence(all_texts)
        unique_terms = set(tokenized_text)

        doc_length = len(tokenized_text)  # after text operations.

        max_tf = 1

        # save only tf for each term in tweet
        for index, term in enumerate(tokenized_text):
            if term not in term_dict.keys():
                term_dict[term] = 1

            else:
                term_dict[term] += 1
                if term_dict[term] > max_tf:
                    max_tf = term_dict[term]

        # TODO - decide if save tf and locations for each term in tweet, or only tf
        # for index, term in enumerate(tokenized_text):
        #     if term not in term_dict.keys():
        #         term_dict[term] = [index]
        #
        #     else:
        #         term_dict[term].append(index)
        #         if len(term_dict[term]) > max_tf:
        #             max_tf = len(term_dict[term])



        # TODO - we need to think what send to the Document
        # self.unique_terms, self.entities - definition and location
        document = Document(tweet_id, max_tf, self.entities, self.small_big_letters_dict, len(unique_terms), tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)

        return document
