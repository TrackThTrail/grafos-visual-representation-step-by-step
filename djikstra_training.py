import heapq


def djikstra(grafo, root):
    dist = {u: float("inf") for u in grafo}
    pai = {u: None for u in grafo}

    heap = [(0, root)]

    dist[root] = 0

    while heap:
        d, node = heapq.heappop(heap)
        if d > dist[node]: # entrada obsoleta, ignora
            continue
        for vizinho, peso in grafo[node]:
            if dist[node] + peso < dist[vizinho]: #custa menos, relaxa a aresta
                dist[vizinho] = dist[node] + peso
                pai[v] = node
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