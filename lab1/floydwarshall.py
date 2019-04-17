class FloydWarshall:

    def __init__(self, page_graph):
        self.graph = page_graph.graph
        self.next = {}
        self.init_next()

    def init_next(self):
        for i in self.graph:
            next_row = {}
            for j in self.graph:
                next_row[j] = j if self.graph[i][j] <= 1 else None
            self.next[i] = next_row

    def find_paths(self):
        graph = self.graph
        next = self.next

        for k in graph:
            for i in graph:
                for j in graph:
                    if graph[i][k] + graph[k][j] < graph[i][j]:
                        graph[i][j] = graph[i][k] + graph[k][j]
                        next[i][j] = k

    def get_paths(self):
        paths = {}
        for i in self.graph:
            for j in self.graph:
                if i != j:
                    paths[f'{i}->{j}'] = self.get_path(i, j)
        return paths

    def get_path(self, u, v):
        if not self.next[u][v]:
            return []
        path = [u]
        while u != v:
            u = self.next[u][v]
            path.append(u)
        return path
