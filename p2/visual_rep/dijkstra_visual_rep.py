import heapq
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Pseudocódigo original:
# DIJKSTRA(G, w, s)
# for vertice u E V[G]:
#     u.d = inf, u.pi = NULO
# s.d = 0
# Q = min-heap com todos os vértices
# while Q != []:
#     u = EXTRACT-MIN(Q)
#     for v in Adj[u]:
#         RELAX(u, v, w)   → if v.d > u.d + w(u,v): v.d = u.d + w(u,v), v.pi = u


def dijkstra(grafo, s):
    """
    Algoritmo de Dijkstra para caminhos mínimos de fonte única.

    grafo: dicionário de adjacências ponderadas  {vertice: [(vizinho, peso), ...]}
    s:     vértice de origem

    Retorna:
        dist - menor distância de s a cada vértice
        pai  - predecessor de cada vértice na árvore de caminhos mínimos
    """
    dist = {u: float("inf") for u in grafo}
    pai  = {u: None for u in grafo}

    dist[s] = 0
    heap = [(0, s)]

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue
        for v, peso in grafo[u]:
            if dist[u] + peso < dist[v]:
                dist[v] = dist[u] + peso
                pai[v]  = u
                heapq.heappush(heap, (dist[v], v))

    return dist, pai


def dijkstra_passos(grafo, s):
    """
    Igual ao Dijkstra, mas grava um snapshot do estado a cada evento relevante.
    Retorna lista de passos, cada um sendo um dict com:
        finalizado, dist, pai, heap, atual, vizinho, peso_aresta, descricao
    """
    dist       = {u: float("inf") for u in grafo}
    pai        = {u: None for u in grafo}
    finalizado = {u: False for u in grafo}

    dist[s] = 0
    heap = [(0, s)]

    passos = []

    def snapshot(atual, vizinho, peso_aresta, descricao):
        passos.append({
            "finalizado":  dict(finalizado),
            "dist":        dict(dist),
            "pai":         dict(pai),
            "heap":        list(heap),
            "atual":       atual,
            "vizinho":     vizinho,
            "peso_aresta": peso_aresta,
            "descricao":   descricao,
        })

    snapshot(s, None, None, f"Início: d[{s}]=0, todos os outros d=∞")

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            snapshot(u, None, None,
                     f"Extrai {u} (d_heap={d}) — entrada obsoleta, ignora")
            continue
        finalizado[u] = True
        snapshot(u, None, None,
                 f"Extrai {u} (d={dist[u]}) — finalizado, explorando vizinhos")
        for v, peso in grafo[u]:
            nova = dist[u] + peso
            if nova < dist[v]:
                dist[v] = nova
                pai[v]  = u
                heapq.heappush(heap, (dist[v], v))
                snapshot(u, v, peso,
                         f"Relaxa ({u}→{v}, w={peso}): d[{v}]={dist[v]}, pai={u}")
            else:
                snapshot(u, v, peso,
                         f"Aresta ({u}→{v}, w={peso}) não melhora d[{v}]={dist[v]}, ignora")

    return passos


def caminho(pai, s, v):
    """Reconstrói o caminho de s até v usando o dicionário de predecessores."""
    if v == s:
        return [s]
    if pai[v] is None:
        return []
    return caminho(pai, s, pai[v]) + [v]


# ── Exemplo de uso ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    G = {
        1: [(2, 4), (3, 1)],
        2: [(4, 1)],
        3: [(2, 2), (4, 5)],
        4: [(5, 3)],
        5: [],
    }

    origem = 1
    dist, pai = dijkstra(G, origem)

    print(f"Dijkstra a partir do vértice {origem}\n")
    print(f"{'Vértice':>8} | {'Distância':>9} | {'Pai':>4}")
    print("-" * 28)
    for v in sorted(G):
        p = pai[v] if pai[v] is not None else "-"
        d = dist[v] if dist[v] != float("inf") else "∞"
        print(f"{v:>8} | {str(d):>9} | {str(p):>4}")

    print()
    destino = 5
    print(f"Caminho de {origem} até {destino}: {caminho(pai, origem, destino)}")

    # ── Navegação por botões ──────────────────────────────────────────────────
    from matplotlib.widgets import Button

    passos = dijkstra_passos(G, origem)

    # Monta grafo direcionado para networkx
    Gnx = nx.DiGraph()
    for u in G:
        for v, w in G[u]:
            Gnx.add_edge(u, v, weight=w)
    for u in G:
        if u not in Gnx:
            Gnx.add_node(u)

    pos  = nx.spring_layout(Gnx, seed=42)
    nos  = list(Gnx.nodes())
    edge_labels = {(u, v): d["weight"] for u, v, d in Gnx.edges(data=True)}

    COR_BRANCO = "#FFFFFF"   # não visitado / não finalizado
    COR_CINZA  = "#F4A460"   # no heap
    COR_PRETO  = "#4169E1"   # finalizado

    COR_BORDA_ATUAL   = "#FF0000"
    COR_BORDA_VIZINHO = "#FFD700"
    COR_BORDA_NORMAL  = "#333333"

    estado = {"frame": 0}

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.subplots_adjust(bottom=0.22)

    ax_prev = fig.add_axes([0.25, 0.06, 0.2, 0.07])
    ax_next = fig.add_axes([0.55, 0.06, 0.2, 0.07])
    btn_prev = Button(ax_prev, "◀  Retroceder", color="#FFCCCC", hovercolor="#FF9999")
    btn_next = Button(ax_next, "Avançar  ▶",    color="#CCFFCC", hovercolor="#99FF99")

    def _cor_no(v, p):
        if p["finalizado"][v]:
            return COR_PRETO
        # considera "no heap" se dist < inf (foi inserido pelo menos uma vez)
        if p["dist"][v] < float("inf"):
            return COR_CINZA
        return COR_BRANCO

    def desenha(frame):
        ax.clear()
        p = passos[frame]

        cores_nos = [_cor_no(v, p) for v in nos]
        bordas, larguras = [], []
        for v in nos:
            if v == p["atual"]:
                bordas.append(COR_BORDA_ATUAL);   larguras.append(3.5)
            elif v == p["vizinho"]:
                bordas.append(COR_BORDA_VIZINHO); larguras.append(3.5)
            else:
                bordas.append(COR_BORDA_NORMAL);  larguras.append(1.5)

        # Arestas da árvore de caminhos mínimos (pai)
        arestas_arvore = [(p["pai"][v], v) for v in nos if p["pai"][v] is not None]
        aresta_ativa   = []
        if p["atual"] is not None and p["vizinho"] is not None:
            aresta_ativa = [(p["atual"], p["vizinho"])]

        arestas_outras = [
            e for e in Gnx.edges()
            if e not in arestas_arvore and e not in aresta_ativa
        ]

        nx.draw_networkx_edges(Gnx, pos, edgelist=arestas_outras,
                               edge_color="#CCCCCC", width=1.5,
                               arrows=True, arrowsize=15, ax=ax)
        nx.draw_networkx_edges(Gnx, pos, edgelist=arestas_arvore,
                               edge_color="#4169E1", width=3,
                               arrows=True, arrowsize=18, ax=ax)
        if aresta_ativa:
            nx.draw_networkx_edges(Gnx, pos, edgelist=aresta_ativa,
                                   edge_color="#FFD700", width=3, style="dashed",
                                   arrows=True, arrowsize=18, ax=ax)

        nx.draw_networkx_nodes(Gnx, pos, node_color=cores_nos,
                               node_size=800, edgecolors=bordas,
                               linewidths=larguras, ax=ax)
        nx.draw_networkx_labels(Gnx, pos, font_size=12, font_weight="bold", ax=ax)
        nx.draw_networkx_edge_labels(Gnx, pos, edge_labels=edge_labels,
                                     font_size=9, font_color="#555555", ax=ax)

        # Rótulos de distância acima de cada nó
        labels_d  = {v: (f"d={p['dist'][v]}" if p['dist'][v] != float("inf") else "d=∞")
                     for v in nos}
        pos_acima = {v: (x, y + 0.15) for v, (x, y) in pos.items()}
        nx.draw_networkx_labels(Gnx, pos_acima, labels=labels_d,
                                font_size=8, font_color="dimgray", ax=ax)

        # Heap atual (ordenado)
        heap_ord  = sorted(p["heap"])
        heap_str  = " → ".join(f"({d},{v})" for d, v in heap_ord) or "vazio"
        ax.set_title(f"Passo {frame + 1}/{len(passos)}\n{p['descricao']}",
                     fontsize=12, fontweight="bold")
        ax.text(0.5, -0.05, f"Heap (min): [ {heap_str} ]",
                transform=ax.transAxes, ha="center", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFACD", edgecolor="#888"))

        patches = [
            mpatches.Patch(facecolor=COR_BRANCO, edgecolor="#333", label="Não visitado"),
            mpatches.Patch(facecolor=COR_CINZA,  edgecolor="#333", label="No heap"),
            mpatches.Patch(facecolor=COR_PRETO,  edgecolor="#333", label="Finalizado"),
            mpatches.Patch(color="#4169E1", label="Aresta da árvore de caminhos mínimos"),
            mpatches.Patch(color="#FFD700", label="Aresta sendo relaxada"),
        ]
        ax.legend(handles=patches, loc="upper left", fontsize=8)
        ax.axis("off")

        btn_prev.ax.set_visible(frame > 0)
        btn_next.ax.set_visible(frame < len(passos) - 1)
        fig.canvas.draw_idle()

    def avancar(event):
        if estado["frame"] < len(passos) - 1:
            estado["frame"] += 1
            desenha(estado["frame"])

    def retroceder(event):
        if estado["frame"] > 0:
            estado["frame"] -= 1
            desenha(estado["frame"])

    btn_next.on_clicked(avancar)
    btn_prev.on_clicked(retroceder)

    desenha(0)
    plt.show()
