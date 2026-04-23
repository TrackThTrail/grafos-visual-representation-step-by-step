from collections import deque
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Pseudocódigo original:
# BFS(G, s)
# for vertice u E V[G] - {s}:
#     u.cor = BRANCO, u.d = inf, u.pi = NULO
# s.cor = CINZA, s.d = 0, s.pi = NULO
# Q = fila fifo
# ENFILEIRAR(Q, s)
# while Q != []:
#     u = DESENFILEIRAR(Q)
#     for v in Adj[u]:
#         if v.cor == BRANCO:
#             v.cor = CINZA, v.d = u.d+1, v.pi = u
#             ENFILEIRAR(Q, v)
#     u.cor = PRETO


def bfs(grafo, s):
    """
    Busca em Largura (BFS) a partir do vértice s.

    grafo: dicionário de adjacências  {vertice: [vizinhos]}
    s:     vértice de origem

    Retorna:
        cor  - cor final de cada vértice ('BRANCO', 'CINZA' ou 'PRETO')
        dist - distância (nº de arestas) da origem s a cada vértice
        pai  - predecessor de cada vértice na árvore BFS (None se raiz/não alcançado)
    """
    BRANCO, CINZA, PRETO = "BRANCO", "CINZA", "PRETO"

    cor  = {u: BRANCO for u in grafo}
    dist = {u: float("inf") for u in grafo}
    pai  = {u: None for u in grafo}

    cor[s]  = CINZA
    dist[s] = 0

    fila = deque([s])

    while fila:
        u = fila.popleft()                  # DESENFILEIRAR
        for v in grafo[u]:
            if cor[v] == BRANCO:
                cor[v]  = CINZA
                dist[v] = dist[u] + 1
                pai[v]  = u
                fila.append(v)              # ENFILEIRAR
        cor[u] = PRETO

    return cor, dist, pai


def bfs_passos(grafo, s):
    """
    Igual ao BFS, mas grava um snapshot do estado a cada evento relevante.
    Retorna lista de passos, cada um sendo um dict com:
        cor, dist, pai, fila, atual, vizinho, descricao
    """
    BRANCO, CINZA, PRETO = "BRANCO", "CINZA", "PRETO"

    cor  = {u: BRANCO for u in grafo}
    dist = {u: float("inf") for u in grafo}
    pai  = {u: None for u in grafo}

    cor[s]  = CINZA
    dist[s] = 0
    fila = deque([s])

    passos = []

    def snapshot(atual, vizinho, descricao):
        passos.append({
            "cor":       dict(cor),
            "dist":      dict(dist),
            "pai":       dict(pai),
            "fila":      list(fila),
            "atual":     atual,
            "vizinho":   vizinho,
            "descricao": descricao,
        })

    snapshot(s, None, f"Início: enfileira vértice {s}")

    while fila:
        u = fila.popleft()
        snapshot(u, None, f"Desenfileira {u} — explorando vizinhos")
        for v in grafo[u]:
            if cor[v] == BRANCO:
                cor[v]  = CINZA
                dist[v] = dist[u] + 1
                pai[v]  = u
                fila.append(v)
                snapshot(u, v, f"Descobre {v} (d={dist[v]}, pai={u}) → enfileira")
            else:
                snapshot(u, v, f"Vizinho {v} já visitado (cor={cor[v]}), ignora")
        cor[u] = PRETO
        snapshot(u, None, f"Finaliza {u} → PRETO")

    return passos


def caminho(pai, s, v):
    """Reconstrói o caminho de s até v usando o dicionário de predecessores."""
    if v == s:
        return [s]
    if pai[v] is None:
        return []                           # v não é alcançável a partir de s
    return caminho(pai, s, pai[v]) + [v]


# ── Exemplo de uso ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Grafo não-direcionado representado como lista de adjacências
    G = {
        1: [2, 3],
        2: [1, 4, 5],
        3: [1, 6],
        4: [2],
        5: [2, 6],
        6: [3, 5],
    }

    origem = 1
    cor, dist, pai = bfs(G, origem)

    print(f"BFS a partir do vértice {origem}\n")
    print(f"{'Vértice':>8} | {'Distância':>9} | {'Pai':>4} | Cor")
    print("-" * 38)
    for v in sorted(G):
        p = pai[v] if pai[v] is not None else "-"
        print(f"{v:>8} | {dist[v]:>9} | {str(p):>4} | {cor[v]}")

    print()
    destino = 6
    print(f"Caminho de {origem} até {destino}: {caminho(pai, origem, destino)}")

    # ── Navegação por botões ──────────────────────────────────────────────────
    from matplotlib.widgets import Button

    passos = bfs_passos(G, origem)
    Gnx    = nx.Graph(G)
    pos    = nx.spring_layout(Gnx, seed=42)
    nos    = list(Gnx.nodes())

    COR_MAP = {
        "BRANCO": "#FFFFFF",
        "CINZA":  "#F4A460",
        "PRETO":  "#4169E1",
    }
    COR_BORDA_ATUAL   = "#FF0000"
    COR_BORDA_VIZINHO = "#FFD700"
    COR_BORDA_NORMAL  = "#333333"

    estado = {"frame": 0}

    fig, ax = plt.subplots(figsize=(9, 7))
    fig.subplots_adjust(bottom=0.22)

    ax_prev = fig.add_axes([0.25, 0.06, 0.2, 0.07])
    ax_next = fig.add_axes([0.55, 0.06, 0.2, 0.07])
    btn_prev = Button(ax_prev, "◀  Retroceder", color="#FFCCCC", hovercolor="#FF9999")
    btn_next = Button(ax_next, "Avançar  ▶",   color="#CCFFCC", hovercolor="#99FF99")

    def desenha(frame):
        ax.clear()
        p = passos[frame]

        cores_nos = [COR_MAP[p["cor"][v]] for v in nos]
        bordas, larguras = [], []
        for v in nos:
            if v == p["atual"]:
                bordas.append(COR_BORDA_ATUAL);   larguras.append(3.5)
            elif v == p["vizinho"]:
                bordas.append(COR_BORDA_VIZINHO); larguras.append(3.5)
            else:
                bordas.append(COR_BORDA_NORMAL);  larguras.append(1.5)

        arestas_arvore = [(p["pai"][v], v) for v in nos if p["pai"][v] is not None]
        arestas_outras = [e for e in Gnx.edges()
                          if e not in arestas_arvore
                          and (e[1], e[0]) not in arestas_arvore]

        aresta_ativa = []
        if p["atual"] is not None and p["vizinho"] is not None:
            aresta_ativa   = [(p["atual"], p["vizinho"])]
            arestas_outras = [e for e in arestas_outras
                              if e not in aresta_ativa
                              and (e[1], e[0]) not in aresta_ativa]

        nx.draw_networkx_edges(Gnx, pos, edgelist=arestas_outras,
                               edge_color="#CCCCCC", width=2, ax=ax)
        nx.draw_networkx_edges(Gnx, pos, edgelist=arestas_arvore,
                               edge_color="#4169E1", width=3, ax=ax)
        if aresta_ativa:
            nx.draw_networkx_edges(Gnx, pos, edgelist=aresta_ativa,
                                   edge_color="#FFD700", width=3, style="dashed", ax=ax)

        nx.draw_networkx_nodes(Gnx, pos, node_color=cores_nos,
                               node_size=800, edgecolors=bordas,
                               linewidths=larguras, ax=ax)
        nx.draw_networkx_labels(Gnx, pos, font_size=12, font_weight="bold", ax=ax)

        labels_d  = {v: (f"d={p['dist'][v]}" if p['dist'][v] != float("inf") else "d=∞") for v in nos}
        pos_acima = {v: (x, y + 0.14) for v, (x, y) in pos.items()}
        nx.draw_networkx_labels(Gnx, pos_acima, labels=labels_d,
                                font_size=8, font_color="dimgray", ax=ax)

        fila_str = " → ".join(str(v) for v in p["fila"]) or "vazia"
        ax.set_title(f"Passo {frame + 1}/{len(passos)}\n{p['descricao']}",
                     fontsize=12, fontweight="bold")
        ax.text(0.5, -0.05, f"Fila: [ {fila_str} ]",
                transform=ax.transAxes, ha="center", fontsize=11,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFACD", edgecolor="#888"))

        patches = [
            mpatches.Patch(facecolor=COR_MAP["BRANCO"], edgecolor="#333", label="BRANCO — não visitado"),
            mpatches.Patch(facecolor=COR_MAP["CINZA"],  edgecolor="#333", label="CINZA — na fila"),
            mpatches.Patch(facecolor=COR_MAP["PRETO"],  edgecolor="#333", label="PRETO — finalizado"),
            mpatches.Patch(color="#4169E1", label="Aresta da árvore BFS"),
            mpatches.Patch(color="#FFD700", label="Aresta sendo inspecionada"),
        ]
        ax.legend(handles=patches, loc="upper left", fontsize=8)
        ax.axis("off")

        # Habilita/desabilita botões nas extremidades
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



