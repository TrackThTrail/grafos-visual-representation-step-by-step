import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Pseudocódigo original:
# BELLMAN-FORD(G, w, s)
# for vertice u E V[G]:
#     u.d = inf, u.pi = NULO
# s.d = 0
# for _ in range(n - 1):          ← iteração _
#     for u in range(n):           ← vértice fonte u
#         for v in adj[u]:         ← vizinho v
#             RELAX(u, v, w)   → if L[u] + W[(u,v)] < L[v]: L[v] = ..., pai[v] = u
# for u in range(n):               ← detecção de ciclo negativo
#     for v in adj[u]:
#         if L[u] + W[(u,v)] < L[v]: return None, None, True


def bellman_ford(adj, W, r):
    n   = len(adj)
    L   = [float("inf")] * n
    pai = [-1] * n
    L[r] = 0

    for _ in range(n - 1):
        for u in range(n):
            for v in adj[u]:
                if L[u] + W[(u, v)] < L[v]:
                    L[v]   = L[u] + W[(u, v)]
                    pai[v] = u

    for u in range(n):
        for v in adj[u]:
            if L[u] + W[(u, v)] < L[v]:
                return None, None, True

    return L, pai, False


def bellman_ford_passos(adj, W, r):
    """
    Igual ao Bellman-Ford, mas grava um snapshot a cada inspeção de aresta,
    incluindo a fase de detecção de ciclo negativo aresta por aresta.
    """
    n   = len(adj)
    L   = [float("inf")] * n
    pai = [-1] * n
    L[r] = 0

    passos = []

    def snap(iter_, u, v, melhorou, concluido, ciclo_detectado, fase, descricao):
        passos.append({
            "L":               list(L),
            "pai":             list(pai),
            "iter_":           iter_,
            "u":               u,
            "v":               v,
            "melhorou":        melhorou,
            "concluido":       concluido,
            "ciclo_detectado": ciclo_detectado,
            "fase":            fase,
            "descricao":       descricao,
        })

    snap(None, None, None, False, False, False, "relaxamento",
         f"Início: L[{r}]=0, todos os outros L=∞")

    for _ in range(n - 1):
        for u in range(n):
            for v in adj[u]:
                w    = W[(u, v)]
                nova = L[u] + w
                if nova < L[v]:
                    L[v]   = nova
                    pai[v] = u
                    snap(_, u, v, True, False, False, "relaxamento",
                         f"_={_}  u={u}  v={v}  →  L[{v}] = {L[v]}  (melhora!)")
                else:
                    snap(_, u, v, False, False, False, "relaxamento",
                         f"_={_}  u={u}  v={v}  →  L[{v}]={L[v]} já ≤ {nova}, sem melhora")

    # ── fase de detecção de ciclo aresta por aresta ────────────────────────
    snap(None, None, None, False, False, False, "deteccao",
         "Relaxamento concluído — iniciando detecção de ciclo negativo")

    for u in range(n):
        for v in adj[u]:
            w = W[(u, v)]
            if L[u] + w < L[v]:
                snap(None, u, v, True, True, True, "deteccao",
                     f"CICLO NEGATIVO! L[{u}]+{w:+d} = {L[u]+w} < L[{v}]={L[v]}")
                return passos, True
            else:
                snap(None, u, v, False, False, False, "deteccao",
                     f"Detecção: ({u}→{v}) L[{u}]+{w:+d} = {L[u]+w} ≥ L[{v}]={L[v]}, ok")

    snap(None, None, None, False, True, False, "deteccao",
         "Nenhum ciclo negativo detectado — distâncias corretas")
    return passos, False


def caminho(pai, r, v):
    """Reconstrói o caminho de r até v usando o vetor de predecessores."""
    if v == r:
        return [r]
    if pai[v] == -1:
        return []
    return caminho(pai, r, pai[v]) + [v]


# ── Exemplo de uso ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    # Ciclo negativo:  1 → 2 → 3 → 1  com custo 3 + (-5) + 1 = -1
    #
    #   0 → 1  (w=2)
    #   1 → 2  (w=3)
    #   2 → 3  (w=-5)  ← peso negativo
    #   3 → 1  (w=1)   ← fecha o ciclo
    #
    # A cada volta pelo ciclo L[1], L[2], L[3] diminuem 1 → nunca convergem.
    # O for de detecção pega isso na V-ésima iteração.
    n   = 4
    adj = [[1], [2], [3], [1]]
    W   = {(0,1): 2, (1,2): 3, (2,3): -5, (3,1): 1}
    r   = 0

    L, pai, ciclo_neg = bellman_ford(adj, W, r)
    print("Ciclo negativo:", ciclo_neg)
    print("L:", L)

    # ── Navegação por botões ──────────────────────────────────────────────────
    from matplotlib.widgets import Button

    passos, _ = bellman_ford_passos(adj, W, r)

    Gnx = nx.DiGraph()
    for u in range(n):
        for v in adj[u]:
            Gnx.add_edge(u, v, weight=W[(u, v)])

    pos         = nx.spring_layout(Gnx, seed=42)
    nos         = list(Gnx.nodes())
    edge_labels = {(u, v): d["weight"] for u, v, d in Gnx.edges(data=True)}

    COR_BRANCO = "#FFFFFF"   # L = ∞ (não alcançado)
    COR_CINZA  = "#F4A460"   # L < ∞ (alcançado)
    COR_PRETO  = "#4169E1"   # finalizado
    COR_CICLO  = "#FF4444"   # vértice do ciclo negativo detectado

    COR_BORDA_U      = "#FF0000"
    COR_BORDA_V      = "#FFD700"
    COR_BORDA_NORMAL = "#333333"

    estado = {"frame": 0}

    fig, ax = plt.subplots(figsize=(10, 7))
    fig.subplots_adjust(bottom=0.28)

    ax_prev  = fig.add_axes([0.25, 0.06, 0.2, 0.07])
    ax_next  = fig.add_axes([0.55, 0.06, 0.2, 0.07])
    btn_prev = Button(ax_prev, "◀  Retroceder", color="#FFCCCC", hovercolor="#FF9999")
    btn_next = Button(ax_next, "Avançar  ▶",    color="#CCFFCC", hovercolor="#99FF99")

    def _cor_no(v, p):
        if p["ciclo_detectado"] and v in (p["u"], p["v"]):
            return COR_CICLO
        if p["concluido"]:
            return COR_PRETO if p["L"][v] < float("inf") else COR_BRANCO
        return COR_BRANCO if p["L"][v] == float("inf") else COR_CINZA

    def desenha(frame):
        ax.clear()
        p = passos[frame]

        cores_nos = [_cor_no(v, p) for v in nos]
        bordas, larguras = [], []
        for v in nos:
            if v == p["u"]:
                bordas.append(COR_BORDA_U);      larguras.append(3.5)
            elif v == p["v"]:
                bordas.append(COR_BORDA_V);      larguras.append(3.5)
            else:
                bordas.append(COR_BORDA_NORMAL); larguras.append(1.5)

        arestas_arvore = [(p["pai"][v], v) for v in nos if p["pai"][v] != -1]
        aresta_ativa   = []
        if p["u"] is not None and p["v"] is not None:
            aresta_ativa = [(p["u"], p["v"])]
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
            if p["ciclo_detectado"]:
                cor_ativa = "#FF0000"
            elif p["melhorou"]:
                cor_ativa = "#00CC44"
            else:
                cor_ativa = "#FFD700"
            nx.draw_networkx_edges(Gnx, pos, edgelist=aresta_ativa,
                                   edge_color=cor_ativa, width=3, style="dashed",
                                   arrows=True, arrowsize=18, ax=ax)

        nx.draw_networkx_nodes(Gnx, pos, node_color=cores_nos,
                               node_size=800, edgecolors=bordas,
                               linewidths=larguras, ax=ax)
        nx.draw_networkx_labels(Gnx, pos, font_size=12, font_weight="bold", ax=ax)
        nx.draw_networkx_edge_labels(Gnx, pos, edge_labels=edge_labels,
                                     font_size=9, font_color="#555555", ax=ax)

        labels_L  = {v: (f"L={p['L'][v]}" if p["L"][v] != float("inf") else "L=∞")
                     for v in nos}
        pos_acima = {v: (x, y + 0.15) for v, (x, y) in pos.items()}
        nx.draw_networkx_labels(Gnx, pos_acima, labels=labels_L,
                                font_size=8, font_color="dimgray", ax=ax)

        fase_str  = "[ DETECÇÃO DE CICLO ]" if p["fase"] == "deteccao" else ""
        titulo_cor = "#CC0000" if p["ciclo_detectado"] else "black"
        ax.set_title(f"Passo {frame + 1}/{len(passos)}  {fase_str}\n{p['descricao']}",
                     fontsize=12, fontweight="bold", color=titulo_cor)

        # ── caixa de variáveis do loop ──────────────────────────────────────
        iter_str = str(p["iter_"]) if p["iter_"] is not None else "—"
        u_str    = str(p["u"])     if p["u"]     is not None else "—"
        v_str    = str(p["v"])     if p["v"]     is not None else "—"

        vars_txt = f"_  =  {iter_str}     u  =  {u_str}     v  =  {v_str}"
        ax.text(0.5, -0.05, vars_txt,
                transform=ax.transAxes, ha="center", fontsize=12,
                fontfamily="monospace",
                bbox=dict(boxstyle="round,pad=0.4", facecolor="#FFFACD", edgecolor="#888"))

        w_str = (f"W[({p['u']},{p['v']})] = {W[(p['u'],p['v'])]:+d}"
                 if p["u"] is not None and p["v"] is not None else "")
        ax.text(0.5, -0.12, w_str,
                transform=ax.transAxes, ha="center", fontsize=10,
                fontfamily="monospace", color="#555555")

        patches = [
            mpatches.Patch(facecolor=COR_BRANCO, edgecolor="#333", label="Não alcançado (L=∞)"),
            mpatches.Patch(facecolor=COR_CINZA,  edgecolor="#333", label="Alcançado"),
            mpatches.Patch(facecolor=COR_PRETO,  edgecolor="#333", label="Finalizado"),
            mpatches.Patch(facecolor=COR_CICLO,  edgecolor="#333", label="Vértice do ciclo negativo"),
            mpatches.Patch(color="#FF0000", label="Nó u / ciclo detectado"),
            mpatches.Patch(color="#FFD700", label="Nó v (destino)"),
            mpatches.Patch(color="#4169E1", label="Árvore de caminhos mínimos"),
            mpatches.Patch(color="#00CC44", label="Relaxamento com melhoria"),
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
