import heapq

def dijkstra(grafo, s):
    dist = {u: float("inf") for u in grafo}
    pai  = {u: None for u in grafo}

    dist[s] = 0
    heap = [(0, s)]  # (distância acumulada, vértice)

    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:   # entrada obsoleta, ignora
            continue
        for v, peso in grafo[u]:
            if dist[u] + peso < dist[v]:   # relaxamento
                dist[v] = dist[u] + peso
                pai[v]  = u
                heapq.heappush(heap, (dist[v], v))

    return dist, pai


grafo = {
    1: [(2, 4), (3, 1)],
    2: [(4, 1)],
    3: [(2, 2), (4, 5)],
    4: [],
}

dist, pai = dijkstra(grafo, 1)
print(dist)
