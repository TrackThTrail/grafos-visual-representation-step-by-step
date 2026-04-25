BRANCO, CINZA, PRETO = 0, 1, 2

def bfs(grafo, s):
    cor  = {u: BRANCO for u in grafo}
    dist = {u: float("inf") for u in grafo}
    pai  = {u: None for u in grafo}

    Q = []
    cor[s] = CINZA
    dist[s] = 0
    Q.append(s)

    while Q:
        vert = Q.pop(0)
        for v in grafo[vert]:
            if cor[v] == BRANCO:
                cor[v] = CINZA
                dist[v] = dist[vert] + 1
                pai[v] = vert
                Q.append(v)
        cor[vert] = PRETO

    return cor, dist, pai


grafo = {1: [2, 3], 2: [3, 4], 3: [], 4: []}
cor, dist, pai = bfs(grafo, 1)
print(dist)