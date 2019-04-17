from node import Node


class Parser:

    def parse_file(self, file):
        lines = file.read().splitlines()
        no_indent_lines = [' '.join(line.split()) for line in lines]
        text = ''.join(no_indent_lines)
        return self.parse_to_tree(text)

    def parse_to_tree(self, text):
        safe_text = text.replace('\\{', '{obr}{-obr}').replace('\\}', '{cbr}{-cbr}')
        result = self.parse_content(safe_text)
        return result if len(result) > 1 else result[0]

    def parse_content(self, text):
        tag_start_idx = text.find('{')
        result = []
        if tag_start_idx == -1:
            result.append(Node(content=text))
        else:
            if tag_start_idx > 0:
                result.append(Node(content=text[:tag_start_idx]))
            tag_end_idx = text.find('}')
            if tag_end_idx == -1:
                raise ValueError('Wrong format')
            tag_name = text[tag_start_idx+1: tag_end_idx]
            close_tag_start = find_closing_tag_pos(text[tag_end_idx+1:], tag_name) + tag_end_idx + 1
            tag_content = text[tag_end_idx+1:close_tag_start]

            if tag_name == 'link':
                result.append(get_link_node(tag_content))
            else:
                inner_nodes = self.parse_content(tag_content)
                result.append(Node(tag=tag_name, children=inner_nodes))

            next_content_start = close_tag_start + 3 + len(tag_name)
            if len(text[next_content_start:]) > 0:
                next_nodes = self.parse_content(text[next_content_start:])
                result.extend(next_nodes)

        return result


def get_link_node(content):
    idx = content.rfind('|')
    text = content[:idx]
    link = content[idx+1:]
    node = Node(tag='link', content=text)
    node.data['src'] = link
    return node


def find_closing_tag_pos(subcontent, tag_name):
    counter = 1
    open_tag = f'{{{tag_name}}}'
    close_tag = f'{{-{tag_name}}}'
    r_idx = 0
    while counter > 0:
        oi = subcontent.find(open_tag)
        ci = subcontent.find(close_tag)
        if -1 < oi < ci:
            counter += 1
            idx = oi + len(open_tag)
            r_idx += idx
        elif ci < oi or (oi == -1 and ci > -1):
            counter -= 1
            idx = ci + len(close_tag)
            r_idx += idx
        else:
            raise ValueError('Wrong format')
        subcontent = subcontent[idx:]

    return r_idx - len(close_tag)


# def test():
#     parser = Parser()
#     result = parser.parse_to_tree('{t}ssssss{t}iiiii{-t}eeee{-t}bbbbb{t}lllll{-t}')
#     # result = find_closing_tag_pos('ssssss{t}ssssss{-t}sssss{-t}sss{t}sssss{-t}', 't')
#     print(result)
#
#
# if __name__ == '__main__':
#     test()

