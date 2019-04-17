class Node:
    def __init__(self, tag=None, content=None, children=None,):
        self.tag = tag
        self.content = content
        self.children = children
        self.data = {}

    def __str__(self):
        return f'{"{" + self.tag + "}" if self.tag else ""}{" " + self.content if self.content else ""}'
