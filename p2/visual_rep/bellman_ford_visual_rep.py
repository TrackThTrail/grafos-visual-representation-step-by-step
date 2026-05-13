import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Pseudocódigo original:
# BELLMAN-FORD(G, w, s)
# for vertice u E V[G]:
#     u.d = inf, u.pi = NULO
# s.d = 0
# for i = 1 to |V[G]| - 1:
#     for aresta (u, v) E E[G]:
#         RELAX(u, v, w)   → if v.d > u.d + w(u,v): v.d = u.d + w(u,v), v.pi = u
# for aresta (u, v) E E[G]:           ← detecção de ciclo negativo
#     if v.d > u.d + w(u,v): return FALSE


def bellman_ford(grafo, s):
    """
    Algoritmo de Bellman-Ford para caminhos mínimos de fonte única.
    Suporta arestas com pesos negativos e detecta ciclos negativos.

    grafo: dicionário de adjacências ponderadas  {vertice: [(vizinho, peso), ...]}
    s:     vértice de origem

    Retorna:
        dist      - menor distância de s a cada vértice
        pai       - predecessor de cada vértice na árvore de caminhos mínimos
        ciclo_neg - True se houver ciclo negativo alcançável a partir de s
    """
    dist = {u: float("inf") for u in grafo}
    pai  = {u: None for u in grafo}
    dist[s] = 0

    V      = len(grafo)
    arestas = [(u, v, w) for u in grafo for v, w in grafo[u]]

    for _ in range(V - 1):
        for u, v, w in arestas:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                pai[v]  = u

    ciclo_neg = any(dist[u] + w < dist[v] for u, v, w in arestas)
    return dist, pai, ciclo_neg


def bellman_ford_passos(grafo, s):
    """
    Igual ao Bellman-Ford, mas grava um snapshot do estado a cada evento relevante.
    Retorna lista de passos, cada um sendo um dict com:
        dist, pai, rodada, atual, vizinho, peso_aresta, melhorou, concluido, descricao
    """
    dist    = {u: float("inf") for u in grafo}
    pai     = {u: None for u in grafo}
    dist[s] = 0

    V       = len(grafo)
    arestas = [(u, v, w) for u in grafo for v, w in grafo[u]]
    passos  = []

    def snap(rodada, u, v, w, melhorou, concluido, descricao):
        passos.append({
            "dist":        dict(dist),
            "pai":         dict(pai),
            "rodada":      rodada,
            "atual":       u,
            "vizinho":     v,
            "peso_aresta": w,
            "melhorou":    melhorou,
            "concluido":   concluido,
            "descricao":   descricao,
        })

    snap(0, None, None, None, False, False,
         f"Início: d[{s}]=0, todos os outros d=∞")

    for rodada in range(1, V):
        alguma_melhoria = False
        for u, v, w in arestas:
            nova = dist[u] + w
            if nova < dist[v]:
                dist[v] = nova
                pai[v]  = u
                alguma_melhoria = True
                snap(rodada, u, v, w, True, False,
                     f"Rodada {rodada}: relaxa ({u}→{v}, w={w:+d}) → d[{v}]={dist[v]}")
            else:
                snap(rodada, u, v, w, False, False,
                     f"Rodada {rodada}: ({u}→{v}, w={w:+d}) não melhora d[{v}]")
        if not alguma_melhoria:
            break

    ciclo_neg = any(dist[u] + w < dist[v] for u, v, w in arestas)
    snap(V, None, None, None, False, True,
         "Ciclo negativo detectado!" if ciclo_neg
         else "Concluído! Distâncias mínimas encontradas")

    return passos, ciclo_neg


def caminho(pai, s, v):
    """Reconstrói o caminho de s até v usando o dicionário de predecessores."""
    if v == s:
        return [s]
    if pai[v] is None:
        return []
    return caminho(pai, s, pai[v]) + [v]


# ── Exemplo de uso ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Grafo direcionado com peso negativo na aresta 2→3.
    # Caminho mínimo até 3: 1→2→3, custo = 5 + (-4) = 1
    # (Dijkstra com conjunto de visitados finalizaria 3 em d=3 — ERRADO)
    G = {
        1: [(2,  5), (3, 3)],
        2: [(3, -4), (4, 2)],   # ← aresta com peso negativo
        3: [(4,  1)],
        4: [(5,  2)],
        5: [],
    }

    origem = 1
    dist, pai, ciclo_neg = bellman_ford(G, origem)

    print(f"Bellman-Ford a partir do vértice {origem}\n")
    print(f"{'Vértice':>8} | {'Distância':>9} | {'Pai':>4}")
    print("-" * 28)
    for v in sorted(G):
        p = pai[v] if pai[v] is not None else "-"
        d = dist[v] if dist[v] != float("inf") else "∞"
        print(f"{v:>8} | {str(d):>9} | {str(p):>4}")

    print(f"\nCiclo negativo: {ciclo_neg}")
    destino = 5
    print(f"Caminho de {origem} até {destino}: {caminho(pai, origem, destino)}")

    # ── Navegação por botões ──────────────────────────────────────────────────
    from matplotlib.widgets import Button

    passos, _  = bellman_ford_passos(G, origem)
    V          = len(G)

    Gnx = nx.DiGraph()
    for u in G:
        for v, w in G[u]:
            Gnx.add_edge(u, v, weight=w)
    for u in G:
        if u not in Gnx:
            Gnx.add_node(u)

    pos         = nx.spring_layout(Gnx, seed=7)
    nos         = list(Gnx.nodes())
    edge_labels = {(u, v): d["weight"] for u, v, d in Gnx.edges(data=True)}

    COR_BRANCO = "#FFFFFF"   # d = ∞ (não alcançado)
    COR_CINZA  = "#F4A460"   # d < ∞ (alcançado durante a execução)
    COR_PRETO  = "#4169E1"   # finalizado (última rodada concluída)

    COR_BORDA_ATUAL   = "#FF0000"
    COR_BORDA_VIZINHO = "#FFD700"
    COR_BORDA_NORMAL  = "#333333"

    estado = {"frame": 0}

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.subplots_adjust(bottom=0.22)

    ax_prev  = fig.add_axes([0.25, 0.06, 0.2, 0.07])
    ax_next  = fig.add_axes([0.55, 0.06, 0.2, 0.07])
    btn_prev = Button(ax_prev, "◀  Retroceder", color="#FFCCCC", hovercolor="#FF9999")
    btn_next = Button(ax_next, "Avançar  ▶",    color="#CCFFCC", hovercolor="#99FF99")

    def _cor_no(v, p):
        if p["concluido"]:
            return COR_PRETO if p["dist"][v] < float("inf") else COR_BRANCO
        return COR_BRANCO if p["dist"][v] == float("inf") else COR_CINZA

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
            cor_ativa = "#00CC44" if p["melhorou"] else "#FFD700"
            nx.draw_networkx_edges(Gnx, pos, edgelist=aresta_ativa,
                                   edge_color=cor_ativa, width=3, style="dashed",
                                   arrows=True, arrowsize=18, ax=ax)

        nx.draw_networkx_nodes(Gnx, pos, node_color=cores_nos,
                               node_size=800, edgecolors=bordas,
                               linewidths=larguras, ax=ax)
        nx.draw_networkx_labels(Gnx, pos, font_size=12, font_weight="bold", ax=ax)
        nx.draw_networkx_edge_labels(Gnx, pos, edge_labels=edge_labels,
                                     font_size=9, font_color="#555555", ax=ax)

        labels_d  = {v: (f"d={p['dist'][v]}" if p['dist'][v] != float("inf") else "d=∞")
                     for v in nos}
        pos_acima = {v: (x, y + 0.15) for v, (x, y) in pos.items()}
        nx.draw_networkx_labels(Gnx, pos_acima, labels=labels_d,
                                font_size=8, font_color="dimgray", ax=ax)

        rodada_str = f"Rodada {p['rodada']}/{V - 1}" if p["rodada"] > 0 else "Inicial"
        ax.set_title(f"Passo {frame + 1}/{len(passos)}  |  {rodada_str}\n{p['descricao']}",
                     fontsize=12, fontweight="bold")

        aresta_str = (
            f"({p['atual']}→{p['vizinho']}, w={p['peso_aresta']:+d})"
            if p["atual"] is not None and p["vizinho"] is not None else "—"
        )
        ax.text(0.5, -0.05, f"Aresta atual: {aresta_str}",
                transform=ax.transAxes, ha="center", fontsize=10,
                bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFACD", edgecolor="#888"))

        patches = [
            mpatches.Patch(facecolor=COR_BRANCO, edgecolor="#333", label="Não alcançado (d=∞)"),
            mpatches.Patch(facecolor=COR_CINZA,  edgecolor="#333", label="Alcançado"),
            mpatches.Patch(facecolor=COR_PRETO,  edgecolor="#333", label="Finalizado"),
            mpatches.Patch(color="#4169E1", label="Aresta da árvore de caminhos mínimos"),
            mpatches.Patch(color="#00CC44", label="Relaxamento com melhoria"),
            mpatches.Patch(color="#FFD700", label="Relaxamento sem melhoria"),
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
