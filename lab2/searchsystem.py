import os
import re
import math

from avparser import Parser


annotation_coef = 3
general_text_coef = 1

annotations_label = 'annotation'
words_label = 'words'


split_words = '[^a-zA-Z]'


def get_files_list(path):
    files = []
    for r, d, f in os.walk(path):
        for file in f:
            if '.av' in file:
                files.append(os.path.join(r, file))
    return files


def get_words(node, parent=None):
    words = []
    annotations = []
    if not node.tag:
        t_words = re.split(split_words, node.content)
        if parent == 'bt':
            annotations = t_words
        else:
            words = t_words
    elif node.children:
        for child in node.children:
            t_words, t_annotations = get_words(child, node.tag)
            words.extend(t_words)
            annotations.extend(t_annotations)
    return words, annotations


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
            words, annotations = get_words(tree)
            self.docs[f] = {
                annotations_label: {
                    'coef': annotation_coef,
                    'words': list(filter(None, annotations))
                },
                words_label: {
                    'coef': general_text_coef,
                    'words': list(filter(None, words))
                }
            }

    def create_all_words_set(self):
        for name, words in self.docs.items():
            annotations = set(words[annotations_label]['words'])
            main_text = set(words[words_label]['words'])
            for word in list(annotations) + list(main_text):
                self.all_words.add(word)

    def calc_doc_len(self):
        avg_len = 0

        for name, doc in self.docs.items():
            annotations = doc[annotations_label]['words']
            main_text = doc[words_label]['words']

            doc_len = len(annotations) + len(main_text)
            self.doc_len[name] = doc_len
            avg_len += doc_len

        self.avg_len = avg_len / len(self.docs)

    def create_tf_index(self):
        self.init_dict(self.tf)
        for file, words in self.docs.items():
            annotations_part = words[annotations_label]
            annotations = annotations_part['words']
            annotations_coef = annotations_part['coef']
            annotations_set = set(annotations)

            main_text_part = words[words_label]
            main_text = main_text_part['words']
            main_text_coef = main_text_part['coef']
            main_text_set = set(main_text)

            doc_len = len(annotations) + len(main_text)

            for term in list(annotations_set) + list(main_text_set):
                self.tf[file][term] = 0

            for term in annotations_set:
                self.tf[file][term] += annotations_coef * annotations.count(term) / doc_len

            for term in main_text_set:
                self.tf[file][term] += main_text_coef * main_text.count(term) / doc_len

    def create_idf_index(self):
        self.init_dict(self.idf)
        len_docs = len(self.tf)

        for word in self.all_words:
            occurrence_in_docs = 0

            for tf in self.tf.values():
                if tf[word]:
                    occurrence_in_docs += 1

            self.idf[word] = math.log(len_docs / occurrence_in_docs) if occurrence_in_docs else 0

    def create_tf_idf_index(self):
        self.init_dict(self.tf_idf)
        for file, words in self.tf.items():
            for word in words:
                self.tf_idf[file][word] = self.tf[file][word] * self.idf[word]

    def init_dict(self, d):
        for name in self.docs:
            d[name] = {}

            for word in self.all_words:
                d[name][word] = 0


