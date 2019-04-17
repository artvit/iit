from avparser import Parser
from avhtml import HtmlConverter
from pagegraph import PageGraph
from floydwarshall import FloydWarshall
import webbrowser
import sys


def to_html():
    filename = 'example.av'
    if len(sys.argv) > 1:
        filename = sys.argv[1]

    parser = Parser()
    with open(filename, encoding='utf8') as file:
        tree = parser.parse_file(file)
        converter = HtmlConverter()
        html = converter.tree_to_html(tree)

        ext_idx = filename.rfind('.av')
        html_filename = filename[:ext_idx] + '.html'

        with open(html_filename, mode='w') as html_file:
            print(html, file=html_file)
        webbrowser.open_new_tab(html_filename)


def find_shortest_paths():
    folder = 'path_data'
    page_graph = PageGraph(folder)
    alg = FloydWarshall(page_graph)
    alg.find_paths()
    paths = alg.get_paths()
    for path in paths:
        route = '->'.join(paths[path])
        print(f'{path} : {route}')


def main():
    to_html()
    find_shortest_paths()


if __name__ == '__main__':
    main()
