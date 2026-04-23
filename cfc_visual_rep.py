import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.widgets import Button
import textwrap

# Pseudocodigo original:
# dfs_cfc(v, adj, pe, ps, old, pai, t, Q, emQ, cfc):
#   t++ ; pe[v] = t ; old[v] = pe[v]
#   Q.append(v) ; emQ[v] = True
#   for w in adj[v]:
#     if pe[w] == 0:              -> aresta de arvore
#       pai[w] = v ; dfs_cfc(w,...) ; old[v] = min(old[v], old[w])
#     elif ps[w] == 0:            -> aresta de retorno
#       old[v] = min(old[v], pe[w])
#     else:
#       if pe[v] < pe[w]: pass    -> aresta de avanco
#       else:                     -> aresta de cruzamento
#         if emQ[w]: old[v] = min(old[v], pe[w])
#   t++ ; ps[v] = t
#   if old[v] == pe[v]:           -> v e raiz da CFC, pop da pilha ate v


# -- Algoritmo: DFS com calculo de OLD e identificacao de CFCs ----------------

def dfs_cfc_passos(adj):
    vertices = list(adj.keys())
    pe     = {v: 0    for v in vertices}
    ps     = {v: 0    for v in vertices}
    old    = {v: 0    for v in vertices}
    pai    = {v: None for v in vertices}
    cor    = {v: "BRANCO" for v in vertices}
    scc_id = {v: -1   for v in vertices}
    Q      = []
    emQ    = {v: False for v in vertices}
    cfc    = []
    t      = [0]
    passos = []

    def snapshot(atual, vizinho, descricao, aresta_tipo=None):
        passos.append({
            "pe":          dict(pe),
            "ps":          dict(ps),
            "old":         dict(old),
            "pai":         dict(pai),
            "cor":         dict(cor),
            "pilha":       list(Q),
            "emQ":         dict(emQ),
            "cfc":         [list(c) for c in cfc],
            "scc_id":      dict(scc_id),
            "atual":       atual,
            "vizinho":     vizinho,
            "aresta_tipo": aresta_tipo,
            "descricao":   descricao,
        })

    def dfs(v):
        t[0] += 1
        pe[v]  = t[0]
        old[v] = pe[v]
        cor[v] = "CINZA"
        Q.append(v)
        emQ[v] = True
        snapshot(v, None, f"Descobre {v}: pe[{v}]={pe[v]} (tempo de entrada). old[{v}]={old[v]} (o vertice mais antigo que {v} consegue alcancar, por enquanto e ele mesmo). Empilha {v}.")

        for w in adj[v]:
            if pe[w] == 0:
                pai[w] = v
                snapshot(v, w, f"Aresta de arvore {v}->{w}: {w} ainda nao visitado, entrando em {w}.", "arvore")
                dfs(w)
                old_v_antes = old[v]
                old[v] = min(old[v], old[w])
                snapshot(v, w, f"Retorno de {w}: old[{w}]={old[w]} significa que {w} (ou descendente) consegue alcancar o vertice com pe={old[w]}. Como {v} chegou a {w}, {v} tambem consegue alcancar esse vertice. old[{v}]=min({old_v_antes}, {old[w]})={old[v]}", "arvore")
            elif ps[w] == 0:
                old_v_antes = old[v]
                old[v] = min(old[v], pe[w])
                snapshot(v, w, f"Aresta de retorno {v}->{w}: {w} esta na pilha (ainda nao finalizado) com pe[{w}]={pe[w]}. Isso significa {v} consegue 'voltar' ao ancestral {w}. old[{v}]=min({old_v_antes}, pe[{w}]={pe[w]})={old[v]}", "retorno")
            else:
                if pe[v] < pe[w]:
                    snapshot(v, w, f"Aresta de avanco {v}->{w}: pe[{v}]={pe[v]} < pe[{w}]={pe[w]}, logo {v} e ancestral de {w}. Essa aresta nao afeta old (ja foi contabilizada na subarvore).", "avanco")
                else:
                    if emQ[w]:
                        old_v_antes = old[v]
                        old[v] = min(old[v], pe[w])
                        snapshot(v, w, f"Cruzamento {v}->{w}: pe[{v}]={pe[v]} > pe[{w}]={pe[w]} e {w} ainda esta na pilha (mesma CFC potencial). {v} pode alcancar {w} -> old[{v}]=min({old_v_antes}, pe[{w}]={pe[w]})={old[v]}", "cruzamento")
                    else:
                        snapshot(v, w, f"Cruzamento {v}->{w}: {w} ja foi removido da pilha (CFC propria ja fechada), logo {v} e {w} estao em CFCs diferentes. Ignora.", "cruzamento")

        t[0] += 1
        ps[v] = t[0]

        if old[v] == pe[v]:
            comp = []
            sid  = len(cfc)
            while True:
                u = Q.pop()
                emQ[u]    = False
                cor[u]    = "SCC"
                scc_id[u] = sid
                comp.append(u)
                if u == v:
                    break
            cfc.append(comp)
            snapshot(v, None, f"CFC {sid + 1} encontrada! old[{v}]={old[v]} == pe[{v}]={pe[v]}: nenhum descendente de {v} consegue alcancar um ancestral de {v}, logo {v} e a raiz da CFC. Desempilha ate {v}: {comp}", None)
        else:
            cor[v] = "PRETO"
            snapshot(v, None, f"Finaliza {v}: old[{v}]={old[v]} != pe[{v}]={pe[v]} -> existe caminho para um ancestral (pe={old[v]}), entao {v} NAO e raiz de CFC. Aguarda.", None)

    for v in vertices:
        if pe[v] == 0:
            dfs(v)

    return passos, cfc


# -- Exemplo de uso e visualizacao --------------------------------------------

if __name__ == "__main__":
    # CFCs esperadas: {1,2,3} e {4,5,6}
    G_adj = {
        1: [2],
        2: [3, 4],
        3: [1],
        4: [5],
        5: [6],
        6: [4],
    }

    passos, cfcs = dfs_cfc_passos(G_adj)

    print("Componentes Fortemente Conexas encontradas:")
    for i, comp in enumerate(cfcs):
        print(f"  CFC {i + 1}: {comp}")

    Gnx = nx.DiGraph(G_adj)
    pos = nx.spring_layout(Gnx, seed=7)
    nos = list(Gnx.nodes())

    COR_MAP = {"BRANCO": "#FFFFFF", "CINZA": "#F4A460", "PRETO": "#AAAAAA"}
    SCC_CORES = ["#FF6B6B", "#6BCB77", "#4D96FF", "#FFD93D", "#C77DFF", "#FF9F1C"]
    COR_BORDA_ATUAL   = "#FF0000"
    COR_BORDA_VIZINHO = "#FFD700"
    COR_BORDA_NORMAL  = "#333333"
    COR_ARESTA = {
        "arvore":     "#4169E1",
        "retorno":    "#FF4500",
        "avanco":     "#32CD32",
        "cruzamento": "#FF00FF",
    }

    estado = {"frame": 0}
    fig, ax = plt.subplots(figsize=(11, 9))
    fig.subplots_adjust(bottom=0.40)

    ax_desc = fig.add_axes([0.02, 0.18, 0.96, 0.17])
    ax_prev  = fig.add_axes([0.25, 0.05, 0.2, 0.08])
    ax_next  = fig.add_axes([0.55, 0.05, 0.2, 0.08])
    btn_prev = Button(ax_prev, "< Retroceder", color="#FFCCCC", hovercolor="#FF9999")
    btn_next = Button(ax_next, "Avancar  >",   color="#CCFFCC", hovercolor="#99FF99")

    def cor_no(p, v):
        if p["cor"][v] == "SCC":
            return SCC_CORES[p["scc_id"][v] % len(SCC_CORES)]
        return COR_MAP.get(p["cor"][v], "#FFFFFF")

    def desenha(frame):
        ax.clear()
        ax_desc.clear()
        ax_desc.axis("off")
        p = passos[frame]

        cores_nos = [cor_no(p, v) for v in nos]
        bordas, larguras = [], []
        for v in nos:
            if v == p["atual"]:
                bordas.append(COR_BORDA_ATUAL);   larguras.append(3.5)
            elif v == p["vizinho"]:
                bordas.append(COR_BORDA_VIZINHO); larguras.append(3.5)
            else:
                bordas.append(COR_BORDA_NORMAL);  larguras.append(1.5)

        aresta_ativa = []
        aresta_cor   = "#FFD700"
        if p["atual"] is not None and p["vizinho"] is not None:
            aresta_ativa = [(p["atual"], p["vizinho"])]
            aresta_cor   = COR_ARESTA.get(p["aresta_tipo"], "#FFD700")

        arestas_outras = [e for e in Gnx.edges() if e not in aresta_ativa]

        nx.draw_networkx_edges(Gnx, pos, edgelist=arestas_outras,
                               edge_color="#CCCCCC", width=1.5, arrows=True,
                               arrowsize=15, connectionstyle="arc3,rad=0.08", ax=ax)
        if aresta_ativa:
            nx.draw_networkx_edges(Gnx, pos, edgelist=aresta_ativa,
                                   edge_color=aresta_cor, width=3, arrows=True,
                                   arrowsize=20, connectionstyle="arc3,rad=0.08", ax=ax)

        nx.draw_networkx_nodes(Gnx, pos, node_color=cores_nos, node_size=800,
                               edgecolors=bordas, linewidths=larguras, ax=ax)
        nx.draw_networkx_labels(Gnx, pos, font_size=12, font_weight="bold", ax=ax)

        labels_info = {}
        for v in nos:
            pev  = p["pe"][v]  if p["pe"][v]  != 0 else "?"
            psv  = p["ps"][v]  if p["ps"][v]  != 0 else "?"
            oldv = p["old"][v] if p["pe"][v]   != 0 else "?"
            labels_info[v] = f"pe={pev} | ps={psv} | old={oldv}"
        pos_acima = {v: (x, y + 0.22) for v, (x, y) in pos.items()}
        nx.draw_networkx_labels(Gnx, pos_acima, labels=labels_info,
                                font_size=6, font_color="dimgray", ax=ax)

        # expande os limites do eixo para que labels acima dos nos nao sejam cortados
        all_y = [y for x, y in pos.values()]
        ax.set_ylim(min(all_y) - 0.3, max(all_y) + 0.4)

        pilha_str = " | ".join(str(v) for v in p["pilha"]) or "vazia"
        cfc_str   = "  ".join(f"CFC{i+1}:{c}" for i, c in enumerate(p["cfc"])) or "nenhuma"
        ax.set_title(f"Passo {frame + 1}/{len(passos)}", fontsize=12, fontweight="bold")

        desc_wrapped = textwrap.fill(p['descricao'], width=105)
        ax_desc.text(0.5, 0.72, desc_wrapped,
                     ha="center", va="center", fontsize=9,
                     transform=ax_desc.transAxes,
                     bbox=dict(boxstyle="round,pad=0.5", facecolor="#E8F4FD",
                               edgecolor="#4A90D9", linewidth=1.5))
        ax_desc.text(0.5, 0.15, f"Pilha Q: [ {pilha_str} ]     CFCs: {cfc_str}",
                     ha="center", va="center", fontsize=9,
                     transform=ax_desc.transAxes,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="#FFFACD", edgecolor="#888"))

        patches = [
            mpatches.Patch(facecolor="#FFFFFF", edgecolor="#333", label="BRANCO - nao visitado"),
            mpatches.Patch(facecolor="#F4A460", edgecolor="#333", label="CINZA - na pilha"),
            mpatches.Patch(facecolor="#AAAAAA", edgecolor="#333", label="PRETO - finalizado"),
        ]
        for i, comp in enumerate(p["cfc"]):
            patches.append(mpatches.Patch(
                facecolor=SCC_CORES[i % len(SCC_CORES)], edgecolor="#333",
                label=f"CFC {i+1}: {comp}"
            ))
        patches += [
            mpatches.Patch(color=COR_ARESTA["arvore"],     label="Aresta de arvore"),
            mpatches.Patch(color=COR_ARESTA["retorno"],    label="Aresta de retorno"),
            mpatches.Patch(color=COR_ARESTA["avanco"],     label="Aresta de avanco"),
            mpatches.Patch(color=COR_ARESTA["cruzamento"], label="Aresta de cruzamento"),
        ]
        ax.legend(handles=patches, loc="upper left", fontsize=7)
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
