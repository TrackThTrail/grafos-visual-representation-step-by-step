def dfs_cfc(vertice, grafo, tempo_entrada, tempo_saida, old, pilha, na_pilha, cfcs, tempo):
    # --- ao descobrir o vertice ---
    tempo[0] += 1
    tempo_entrada[vertice] = tempo[0]   # marca quando entrou na DFS
    old[vertice]           = tempo[0]   # por enquanto, o mais antigo que alcanca e ele mesmo
    pilha.append(vertice)
    na_pilha[vertice] = True

    # --- visita cada vizinho ---
    for vizinho in grafo.get(vertice, []):

        if tempo_entrada[vizinho] == 0:
            # ARESTA DE ARVORE: vizinho ainda nao foi visitado -> desce na DFS
            dfs_cfc(vizinho, grafo, tempo_entrada, tempo_saida, old, pilha, na_pilha, cfcs, tempo)
            # ao voltar, herda o melhor valor da subarvore de vizinho
            old[vertice] = min(old[vertice], old[vizinho])

        elif tempo_saida[vizinho] == 0:
            # ARESTA DE RETORNO: vizinho ja foi visitado mas ainda nao terminou
            # isso significa que vizinho e um ANCESTRAL de vertice na DFS
            # -> vertice consegue "voltar" ate vizinho
            old[vertice] = min(old[vertice], tempo_entrada[vizinho])

        elif na_pilha[vizinho]:
            # ARESTA DE CRUZAMENTO: vizinho ja terminou mas ainda esta na pilha
            # -> vizinho e da mesma CFC potencial
            old[vertice] = min(old[vertice], tempo_entrada[vizinho])

        # caso vizinho ja saiu da pilha (CFC fechada): ignora, sao CFCs diferentes

    # --- ao terminar o vertice ---
    tempo[0] += 1
    tempo_saida[vertice] = tempo[0]

    # SE old[vertice] == tempo_entrada[vertice]:
    #   nenhum descendente consegue alcancar um ancestral de vertice
    #   -> vertice e a RAIZ da CFC -> desempilha tudo ate vertice
    if old[vertice] == tempo_entrada[vertice]:
        componente = []
        while True:
            # import ipdb; ipdb.set_trace()
            cfc_item = pilha.pop()
            na_pilha[cfc_item] = False
            componente.append(cfc_item)
            if cfc_item == vertice:
                break
        cfcs.append(componente)


def encontrar_cfcs(grafo):
    vertices = list(grafo.keys())

    # tempo de entrada: quando o vertice foi descoberto pela DFS (0 = nao visitado)
    tempo_entrada = {v: 0     for v in vertices}
    # tempo de saida: quando o vertice terminou de processar todos os vizinhos (0 = nao terminou)
    tempo_saida   = {v: 0     for v in vertices}
    # old: menor tempo_entrada alcancavel a partir deste vertice
    old           = {v: 0     for v in vertices}
    # na_pilha: controla se o vertice ainda esta na pilha auxiliar
    na_pilha      = {v: False for v in vertices}

    pilha = []   # pilha auxiliar para identificar a CFC
    cfcs  = []   # lista de CFCs encontradas
    tempo = [0]  # contador de tempo (dentro de lista para poder ser modificado na funcao interna)

    for v in vertices:
        if tempo_entrada[v] == 0:   # so visita vertices ainda nao descobertos
            dfs_cfc(v, grafo, tempo_entrada, tempo_saida, old, pilha, na_pilha, cfcs, tempo)

    return cfcs


# --- exemplo ---
grafo = {
    1: [2],
    2: [3, 4],
    3: [1],
    4: [5],
    5: [6],
    6: [4],
}
import ipdb; ipdb.set_trace()
for i, componente in enumerate(encontrar_cfcs(grafo)):
    print(f"CFC {i+1}: {componente}")
