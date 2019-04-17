from searchsystem import SearchSystem


def main():
    ss = SearchSystem('docs')

    for w in ['science', 'language', 'scientist', 'knowledge']:
        results = ss.search(w)
        print(f'"{w}" search results:')
        print(*results, sep='\n')
        print()


if __name__ == '__main__':
    main()
