import os
import math

from avparser import Parser
from node import Node


def get_files_list(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for file in f:
            if '.av' in file:
                files.append(os.path.join(r, file))
    return files


def get_links(file):
    with open(file, encoding='utf8') as file:
        tree = Parser().parse_file(file)
        return find_links_in_tree(tree)


def find_links_in_tree(node: Node):
    links = []
    if node.tag == 'link':
        links.append(node.data['src'])
    elif node.children:
        for child in node.children:
            links.extend(find_links_in_tree(child))
    return links


class PageGraph:

    def __init__(self, path):
        self.graph = {}
        files = get_files_list(path)
        filenames = [file[file.rfind('\\')+1:] for file in files]
        link_dict = {}
        for f, name in zip(files, filenames):
            link_dict[name] = get_links(f)
        self.init_graph(filenames)
        self.fill_graph(link_dict)

    def init_graph(self, files):
        for i in files:
            r = {}
            for j in files:
                r[j] = 0 if i == j else math.inf
            self.graph[i] = r

    def fill_graph(self, link_dict):
        for source, target_list in link_dict.items():
            for target in target_list:
                if source != target:
                    self.graph[source][target] = 1

