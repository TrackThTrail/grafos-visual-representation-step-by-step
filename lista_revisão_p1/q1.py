def dfs_tarjan(v, grafo, tempo_descoberta, tempo_saida, old, pai, tempo, pilha, na_pilha, componentes):

    # marca descoberta
    tempo[0] += 1
    tempo_descoberta[v] = tempo[0]
    old[v] = tempo_descoberta[v]

    pilha.append(v)
    na_pilha[v] = True

    for vizinho in grafo[v]:

        if tempo_descoberta[vizinho] == 0:
            # aresta de árvore
            pai[vizinho] = v
            dfs_tarjan(vizinho, grafo, tempo_descoberta, tempo_saida,
                       old, pai, tempo, pilha, na_pilha, componentes)

            old[v] = min(old[v], old[vizinho])

        elif tempo_saida[vizinho] == 0:
            # aresta de retorno
            old[v] = min(old[v], tempo_descoberta[vizinho])

        else:
            # vizinho já terminou
            if tempo_descoberta[v] < tempo_descoberta[vizinho]:
                pass  # aresta de avanço
            else:
                # aresta de cruzamento  
                if na_pilha[vizinho]:
                    old[v] = min(old[v], tempo_descoberta[vizinho])

    # marca término
    tempo[0] += 1
    tempo_saida[v] = tempo[0]

    # se for raiz de uma CFC
    if old[v] == tempo_descoberta[v]:
        componente = []
        while True:
            u = pilha.pop()
            na_pilha[u] = False
            componente.append(u)
            if u == v:
                break
        componentes.append(componente)


def resolver():
    n, m = 5, 4
    entradas = [(1,2), (2,3), (4,5), (5,4)]

    # lista de adjacência
    grafo = [[] for item_entrada in range(n + 1)]

    for origem, destino in entradas:
        grafo[origem].append(destino)

    # opcional (deixa determinístico)
    for v in range(1, n + 1):
        grafo[v].sort()

    # estruturas
    tempo_descoberta = [0] * (n + 1)
    tempo_saida = [0] * (n + 1)
    old = [0] * (n + 1)
    pai = [-1] * (n + 1)

    tempo = [0]
    pilha = []
    na_pilha = [False] * (n + 1)
    componentes = []

    # 1) encontrar CFCs
    for v in range(1, n + 1):
        if tempo_descoberta[v] == 0:
            dfs_tarjan(v, grafo, tempo_descoberta, tempo_saida,
                       old, pai, tempo, pilha, na_pilha, componentes)

    # 2) mapear vértice -> componente
    componente_de = [-1] * (n    + 1)
    for i, comp in enumerate(componentes):
        for v in comp:
            componente_de[v] = i

    # 3) menor vértice de cada componente
    menor_vertice = [float('inf')] * len(componentes)
    for v in range(1, n + 1):
        c = componente_de[v]
        menor_vertice[c] = min(menor_vertice[c], v)

    # 4) grau de entrada das componentes
    grau_entrada = [0] * len(componentes)

    for u in range(1, n + 1):
        for v in grafo[u]:
            if componente_de[u] != componente_de[v]:
                grau_entrada[componente_de[v]] += 1

    # 5) resposta (componentes fonte)
    resposta = []
    for c in range(len(componentes)):
        if grau_entrada[c] == 0:
            resposta.append(menor_vertice[c])

    resposta.sort()
    print(*resposta)


# executar
resolver()


