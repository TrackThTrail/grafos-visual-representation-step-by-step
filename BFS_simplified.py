#grafo é lista de adjacencias

# grafo = {
#     1: [2,3],
#     2: [3,4],
#     3: []..
# }

def bfs(grafo, s):
    ja_pintados = []
    Q = []
    for u in grafo:
        for v in grafo[u]:
            if v != s and v not in ja_pintados:
                v.cor = BRANCO
                v.pai = None
                v.d = -1
                ja_pintados.append(v)
    
    s.cor = CINZA
    s.d = 0
    Q.append(s)

    while len(Q) > 0:
        vert = Q.pop(0)
        for v in grafo[vert]:
            if v.cor == BRANCO:
                v.cor = CINZA
                v.d = vert.d + 1
                v.pai = vert
                Q.append(v)
        vert.cor = PRETO

