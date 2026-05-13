from collections import deque

def reconstruir_caminho(x, pai):
    caminho = []
    while x != -1:
        caminho.append(x)
        x = pai[x]
    caminho.reverse()
    return caminho


def resolve():
    # leitura
    n, m = map(int, input().split())

    grafo = [[] for _ in range(n+1)]

    for _ in range(m):
        u, v = map(int, input().split())
        grafo[u].append(v)

    x = int(input())

    # ordenar vizinhos (importante pro enunciado)
    for v in range(1, n+1):
        grafo[v].sort()

    # estruturas (equivalente ao que você já usava)
    visitado = [False]*(n+1)
    pai = [-1]*(n+1)
    nivel = [-1]*(n+1)
    tempo = [0]*(n+1)

    instante = 0  # tempo global

    # 🔥 MÚLTIPLAS BFS
    for a in range(1, n+1):
        if not visitado[a]:

            fila = deque()
            fila.append(a)

            visitado[a] = True
            nivel[a] = 0

            instante += 1
            tempo[a] = instante

            maior_tempo = tempo[a]

            while fila:
                v = fila.popleft()

                for w in grafo[v]:
                    if not visitado[w]:
                        visitado[w] = True
                        pai[w] = v
                        nivel[w] = nivel[v] + 1

                        # tempo baseado na raiz da BFS atual
                        tempo[w] = tempo[a] + nivel[w]

                        if tempo[w] > maior_tempo:
                            maior_tempo = tempo[w]

                        fila.append(w)

            # ⏱ próxima BFS começa depois dessa terminar
            instante = maior_tempo

    # resultado para x
    caminho = reconstruir_caminho(x, pai)
    tempo_x = tempo[x]

    # tempo final (quando tudo caiu)
    tempo_final = max(tempo)

    # saída
    print(tempo_x)
    print(*caminho)
    print(tempo_final)


resolve()