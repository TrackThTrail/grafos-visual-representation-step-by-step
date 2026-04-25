def dfs_tarjan(v, grafo, tempo_entrada, tempo_saida, old, tempo, pilha, na_pilha,  componentes):
    tempo[0] += 1
    old[v] = tempo[0]
    tempo_entrada[v] = tempo[0]
    na_pilha[v] = True
    pilha.append(v)

    for vizinho in grafo[v]:
        if tempo_entrada[vizinho] == 0:
            #aresta da árvore, desce na DFS
            dfs_tarjan(vizinho, grafo, tempo_entrada, tempo_saida, old, tempo, pilha, na_pilha, componentes)
            old[v] = min(old[v], old[vizinho])
        
        elif tempo_saida[vizinho] == 0:
            #aresta de retorno, atualiza o old
            old[v] = min(old[v], tempo_entrada[vizinho])
        else:
            if tempo_entrada[v] < tempo_entrada[vizinho]:
                pass
            else:
                if na_pilha[vizinho]:
                    old[v] = min(old[v], tempo_entrada[vizinho])
    
    tempo[0] += 1
    tempo_saida[v] = tempo[0]

    if tempo_entrada[v] == old[v]:
        #encontrou cfc!
        componente = []
        while True:
            vert = pilha.pop()
            na_pilha[vert] = False
            componente.append(vert)
            if vert == v:
                break
        componentes.append(componente)

def resolver():
    n, m = 5, 4
    entradas = [(1, 2), (1, 3), (3, 4), (3, 5)]

    vertices = range(1, n + 1)

    tempo_entrada = {v:0 for v in vertices}
    tempo_saida = {v:0 for v in vertices}
    old = {v:0 for v in vertices}
    tempo = [0]
    componentes = []
    pilha = []
    na_pilha = {v: False for v in vertices}
    #transformo a entrada em grafo lista de adjacencias
    grafo = [[] for i in range(n + 1)]

    for origem, destino in entradas:
        grafo[origem].append(destino)

    #1 - Calcular componentes
    for v in vertices:
        if tempo_entrada[v] == 0:
            dfs_tarjan(v, grafo, tempo_entrada, tempo_saida, old, tempo,pilha, na_pilha, componentes)

    #2 - Descobrir componente_de
    componente_de = {v: 0 for v in vertices}
    for i, componente in enumerate(componentes):
        for vert in componente:
            componente_de[vert] = i

    menor_vertice = [float('inf')] * len(componentes) #[inf, inf, inf] no caso de 3 componentes

    #3 - Menor vértice de cada componente
    for i, componente in enumerate(componentes):
        for vert in componente:
            menor_vertice[i] = min(menor_vertice[i], vert)

    grau_entrada = [0] * len(componentes)
    #4 - Grau de entrada dos componentes para verificar se existe aresta entre componentes
    for u in range(1, n+1):
        for vert_dest in grafo[u]:
            if componente_de[vert_dest] != componente_de[u]:
                grau_entrada[componente_de[vert_dest]] += 1
    
    resposta = []
    for i in range(len(componentes)):
        if grau_entrada[i] == 0:
            resposta.append(menor_vertice[i])
    resposta.sort()
    print(*resposta)


# Passo a passo fica:
# 1 - Transformo grafo em lista de adjacencias
# 2 - Calculo as componentes
# 3 - Descubro de qual componente é cada vértice
# 4 - Um vértice de cada CFC é eleito
# 5 - Grau de entrada dos componentes
# 6 - Componentes com grau 0 são raízes e a resposta