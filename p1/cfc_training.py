def dfs_cfc(v, grafo, tempo_entrada, tempo_saida, pilha, na_pilha, old, tempo):
    tempo[0] += 1
    old[v] = tempo[0]
    tempo_entrada[v] = tempo[0]
    pilha.append(v)
    na_pilha[v] = True

    for vizinho in grafo.get(v, []):
        if tempo_entrada[vizinho] == 0:
            dfs_cfc(vizinho, grafo, tempo_entrada, tempo_saida, pilha, na_pilha, old, tempo)
            old[v] = min(old[v], old[vizinho])
        elif tempo_saida[vizinho] == 0:
            old[v] = min(old[v], tempo_entrada[vizinho])
        elif na_pilha[vizinho] == 0:
            old[v] = min(old[v], tempo_entrada[vizinho])

    tempo[0] += 1
    tempo_saida[v] = tempo[0]
    if old[v] == tempo_entrada[v]:
        cfc = []
        while True:
            i = pilha.pop()
            cfc.append(i)
            na_pilha[i] = False
            if i == v:
                break

def encontrar_cfcs(grafo):

    vertices = list(grafo.keys())

    tempo_entrada = {v: 0 for v in vertices}
    tempo_saida = {v: 0 for v in vertices}
    old = {v: 0 for v in vertices}
    na_pilha = {v: False for v in vertices}

    pilha = []
    tempo = [0]
    cfcs = []

    for v in vertices:
        if tempo_entrada[v] == 0:
            dfs(v, grafo, tempo_entrada, tempo_saida, na_pilha, old, tempo)
    return cfcs

