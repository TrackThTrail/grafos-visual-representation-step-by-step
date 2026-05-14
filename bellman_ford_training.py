def bellman_ford(adj, W, r):
    n = len(adj)
    L = [float('inf')] * n
    pai = [-1] * n
    L[r] = 0

    for _ in range(n-1):
        for u in range(n):
            for v in adj[u]:
                if L[u] + W[(u, v)] < L[v]:
                    L[v] =  L[u] + W[(u, v)]
                    pai[v] = u

    for u in range(n):
        for v in adj[u]:
            if L[u] + W[(u, v)] < L[v]:
                return None, None, True
    
    return L, pai, False