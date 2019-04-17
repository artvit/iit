from node import Node


tag_html_map = {
    'doc': 'html',
    'title': 'h1',
    'heading': 'h3',
    'block': 'div',
    'link': 'a',
    'bt': 'b',
    'it': 'i',
    'ut': 'u',
    'mlist': 'ul',
    'nlist': 'ol',
    'item': 'li'
}

attr_map = {
    'src': 'href'
}

escape_map = {
    'obr': '{',
    'cbr': '}'
}


class HtmlConverter:
    def tree_to_html(self, root):
        return self.node_html(root)

    def node_html(self, node: Node):
        if not node.tag:
            return node.content
        if node.tag in escape_map:
            return escape_map[node.tag]
        content_html = ''
        attr_html = ''
        if node.children:
            content_html = ''.join([self.node_html(x) for x in node.children])
        elif node.content:
            content_html = node.content
        if len(node.data) > 0:
            attr_html = ' '.join([f'{attr_map[key]}="{value}"' for key, value in node.data.items()])

        tag_html = tag_html_map[node.tag]
        return f'<{tag_html} {attr_html}>{content_html}</{tag_html}>'

