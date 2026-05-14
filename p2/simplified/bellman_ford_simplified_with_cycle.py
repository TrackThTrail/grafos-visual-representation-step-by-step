def bellman_ford(adj, W, r):

    n = len(adj)

    # L[v] = distância de r até v
    L = [float('inf')] * n

    # pai[v] = predecessor de v
    pai = [-1] * n

    L[r] = 0

    # relaxa todas as arestas |V| - 1 vezes
    for _ in range(n - 1):

        for u in range(n):

            for v in adj[u]:

                if L[u] + W[(u, v)] < L[v]:

                    L[v] = L[u] + W[(u, v)]
                    pai[v] = u

    # verifica ciclo negativo
    for u in range(n):

        for v in adj[u]:

            if L[u] + W[(u, v)] < L[v]:

                return None, None, True

    return L, pai, False