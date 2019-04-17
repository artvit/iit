import os
import re
import math

from avparser import Parser


annotation_coef = 3
general_text_coef = 1

annotations_label = 'annotation'
words_label = 'words'


split_words_regexp = '[^a-zA-Z]'


def get_files_list(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.av' in file:
                files.append(os.path.join(r, file))
    return files


def get_words(node):
    words = []
    if not node.tag:
        words = re.split(split_words_regexp, node.content)
    elif node.children:
        for child in node.children:
            words.extend(get_words(child))
    return words


def cosine_similarity(query_idf_dict, idf_dict):
    dot_product = 0
    for word in query_idf_dict:
        dot_product += query_idf_dict[word] * idf_dict[word]

    delimiter = l2_norm(query_idf_dict) * l2_norm(idf_dict)
    return dot_product / delimiter


def l2_norm(idf_dict):
    sum = 0
    for w in idf_dict:
        sum += idf_dict[w] ** 2
    return math.sqrt(sum)


class SearchSystem:
    def __init__(self, folder):
        self.files = {}
        self.docs = {}
        self.all_words = set()
        self.tf = {}
        self.idf = {}
        self.tf_idf = {}
        self.doc_len = {}
        self.avg_len = 0
        self.build_system(folder)

    def build_system(self, folder):
        files = get_files_list(folder)
        trees = []
        for file in files:
            with open(file, encoding='utf8') as f:
                trees.append(Parser().parse_file(f))
        for f, t in zip(files, trees):
            self.files[f] = t

        self.parse_docs()
        self.create_all_words_set()
        self.create_tf_index()
        self.create_idf_index()
        self.create_tf_idf_index()

    def parse_docs(self):
        for f, tree in self.files.items():
            words = get_words(tree)
            self.docs[f] = list(filter(None, words))

    def create_all_words_set(self):
        for name, words in self.docs.items():
            self.all_words.update(words)

    def create_tf_index(self):
        self.init_dict(self.tf)
        avg_len = 0
        for file, words in self.docs.items():
            words_set = set(words)

            doc_len = len(words)
            self.doc_len[file] = doc_len
            avg_len += doc_len

            for term in words:
                self.tf[file][term] = 0

            for term in words_set:
                self.tf[file][term] += words.count(term) / doc_len

        self.avg_len = float(avg_len) / len(self.docs)

    def create_idf_index(self):
        self.idf = {}
        len_docs = len(self.tf)

        for word in self.all_words:
            occurrence_in_docs = 0

            for words in self.docs.values():
                if word in words:
                    occurrence_in_docs += 1.0

            self.idf[word] = math.log(len_docs / occurrence_in_docs) + 1.0 if occurrence_in_docs else 0

    def create_tf_idf_index(self):
        self.init_dict(self.tf_idf)
        for file, words in self.tf.items():
            for word in words:
                self.tf_idf[file][word] = self.tf[file][word] * self.idf[word]

    def init_dict(self, d):
        for file in self.docs:
            d[file] = {}
            for word in self.all_words:
                d[file][word] = 0

    def search(self, query):
        relevance = dict()

        if query and query.strip():
            query_tf = self.calc_query_tf(query)
            query_tf_idf = self.calc_query_tf_idf(query_tf)
            relevance = self.calc_doc_relevance(query_tf_idf)

        return relevance

    def calc_query_tf(self, query):
        query_tf = {}

        query = query.lower().strip()
        terms = re.split(split_words_regexp, query)

        terms_len = len(terms)
        terms_set = set(terms)

        if not terms_len:
            return

        for term in terms_set:
            query_tf[term] = terms.count(term) / terms_len

        return query_tf

    def calc_query_tf_idf(self, query_tf):
        query_tf_idf = {}

        for word, tf in query_tf.items():
            if word in self.idf:
                query_tf_idf[word] = tf * self.idf[word]
            else:
                query_tf_idf[word] = 0

        return query_tf_idf

    def calc_doc_relevance(self, query_tf_idf):
        docs_rating = {}
        k1 = 2
        b = 0.75

        # for file, doc in self.docs.items():
        #     doc_score = 0
        #     for term in query_tf_idf:
        #         if term in self.idf:
        #             div = self.idf[term] * self.tf[file][term] * (k1 + 1)
        #             delim = (self.tf[file][term] + k1 * (1 - b + b * self.doc_len[file] / self.avg_len))
        #             doc_score += div / delim
        #
        #     docs_rating[file] = doc_score

        for file, tfidf_dict in self.tf_idf.items():
            docs_rating[file] = cosine_similarity(query_tf_idf, tfidf_dict)

        return sorted(docs_rating.items(), key=lambda a: a[1], reverse=True)


