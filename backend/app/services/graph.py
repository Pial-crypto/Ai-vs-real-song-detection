"""Graph and network analysis utilities."""

from __future__ import annotations

import heapq
import math
from collections import defaultdict, deque
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np


class Graph:
    def __init__(self, directed: bool = False) -> None:
        self.directed = directed
        self.adj: Dict[Any, List[Tuple[Any, float]]] = defaultdict(list)
        self.nodes: set = set()
        self.edges: List[Tuple[Any, Any, float]] = []

    def add_node(self, node: Any) -> None:
        self.nodes.add(node)
        self.adj.setdefault(node, [])

    def add_edge(self, u: Any, v: Any, weight: float = 1.0) -> None:
        self.add_node(u)
        self.add_node(v)
        self.adj[u].append((v, weight))
        self.edges.append((u, v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    def remove_edge(self, u: Any, v: Any) -> None:
        self.adj[u] = [(n, w) for n, w in self.adj[u] if n != v]
        if not self.directed:
            self.adj[v] = [(n, w) for n, w in self.adj[v] if n != u]
        self.edges = [e for e in self.edges if not (e[0] == u and e[1] == v)]

    def remove_node(self, node: Any) -> None:
        self.nodes.discard(node)
        self.adj.pop(node, None)
        for n in list(self.adj.keys()):
            self.adj[n] = [(v, w) for v, w in self.adj[n] if v != node]
        self.edges = [e for e in self.edges if e[0] != node and e[1] != node]

    def neighbors(self, node: Any) -> List[Tuple[Any, float]]:
        return self.adj.get(node, [])

    def degree(self, node: Any) -> int:
        return len(self.adj.get(node, []))

    def in_degree(self, node: Any) -> int:
        if self.directed:
            return sum(1 for u, v, w in self.edges if v == node)
        return self.degree(node)

    def out_degree(self, node: Any) -> int:
        return len(self.adj.get(node, []))

    def has_edge(self, u: Any, v: Any) -> bool:
        return any(n == v for n, w in self.adj.get(u, []))

    def edge_weight(self, u: Any, v: Any) -> Optional[float]:
        for n, w in self.adj.get(u, []):
            if n == v:
                return w
        return None

    def num_nodes(self) -> int:
        return len(self.nodes)

    def num_edges(self) -> int:
        return len(self.edges)

    def density(self) -> float:
        n = self.num_nodes()
        if n < 2:
            return 0.0
        max_edges = n * (n - 1) if self.directed else n * (n - 1) / 2
        return self.num_edges() / max_edges if max_edges > 0 else 0.0

    def adjacency_matrix(self) -> np.ndarray:
        nodes = sorted(self.nodes, key=lambda x: str(x))
        idx = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        m = np.zeros((n, n))
        for u, v, w in self.edges:
            m[idx[u], idx[v]] = w
        return m

    def laplacian_matrix(self) -> np.ndarray:
        A = self.adjacency_matrix()
        D = np.diag(A.sum(axis=1))
        return D - A

    def normalized_laplacian(self) -> np.ndarray:
        A = self.adjacency_matrix()
        d = A.sum(axis=1)
        d_inv_sqrt = np.where(d > 0, 1.0 / np.sqrt(d), 0.0)
        D = np.diag(d_inv_sqrt)
        return np.eye(len(d)) - D @ A @ D

    def to_dict(self) -> Dict[str, Any]:
        return {
            "nodes": list(self.nodes),
            "edges": self.edges,
            "directed": self.directed,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Graph":
        g = cls(directed=data.get("directed", False))
        for n in data.get("nodes", []):
            g.add_node(n)
        for u, v, w in data.get("edges", []):
            g.add_edge(u, v, w)
        return g

    @classmethod
    def from_adjacency_matrix(cls, m: np.ndarray, directed: bool = False) -> "Graph":
        g = cls(directed=directed)
        n = m.shape[0]
        for i in range(n):
            g.add_node(i)
        for i in range(n):
            for j in range(n):
                if m[i, j] != 0:
                    g.add_edge(i, j, float(m[i, j]))
        return g

    def subgraph(self, nodes: List[Any]) -> "Graph":
        g = Graph(directed=self.directed)
        node_set = set(nodes)
        for n in nodes:
            g.add_node(n)
        for u, v, w in self.edges:
            if u in node_set and v in node_set:
                g.add_edge(u, v, w)
        return g

    def induced_subgraph(self, nodes: List[Any]) -> "Graph":
        return self.subgraph(nodes)

    def complement(self) -> "Graph":
        g = Graph(directed=self.directed)
        for n in self.nodes:
            g.add_node(n)
        nodes = list(self.nodes)
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j and not self.has_edge(nodes[i], nodes[j]):
                    g.add_edge(nodes[i], nodes[j], 1.0)
        return g

    def copy(self) -> "Graph":
        return Graph.from_dict(self.to_dict())

    def clear(self) -> None:
        self.adj.clear()
        self.nodes.clear()
        self.edges.clear()


def bfs(graph: Graph, start: Any) -> List[Any]:
    visited = set()
    order = []
    queue = deque([start])
    visited.add(start)
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
    return order


def dfs(graph: Graph, start: Any) -> List[Any]:
    visited = set()
    order = []

    def _dfs(node):
        visited.add(node)
        order.append(node)
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                _dfs(neighbor)

    _dfs(start)
    return order


def dfs_iterative(graph: Graph, start: Any) -> List[Any]:
    visited = set()
    order = []
    stack = [start]
    while stack:
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                stack.append(neighbor)
    return order


def dijkstra(graph: Graph, start: Any) -> Dict[Any, float]:
    dist = {n: float("inf") for n in graph.nodes}
    dist[start] = 0
    pq = [(0, start)]
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist[u]:
            continue
        for v, w in graph.neighbors(u):
            nd = d + w
            if nd < dist.get(v, float("inf")):
                dist[v] = nd
                heapq.heappush(pq, (nd, v))
    return dist


def bellman_ford(graph: Graph, start: Any) -> Dict[Any, float]:
    dist = {n: float("inf") for n in graph.nodes}
    dist[start] = 0
    for _ in range(graph.num_nodes() - 1):
        for u, v, w in graph.edges:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    return dist


def floyd_warshall(graph: Graph) -> np.ndarray:
    n = graph.num_nodes()
    nodes = sorted(graph.nodes, key=lambda x: str(x))
    idx = {node: i for i, node in enumerate(nodes)}
    INF = float("inf")
    D = np.full((n, n), INF)
    np.fill_diagonal(D, 0)
    for u, v, w in graph.edges:
        D[idx[u], idx[v]] = min(D[idx[u], idx[v]], w)
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if D[i, k] + D[k, j] < D[i, j]:
                    D[i, j] = D[i, k] + D[k, j]
    return D


def a_star(graph: Graph, start: Any, goal: Any, heuristic: Callable = None) -> List[Any]:
    if heuristic is None:
        def heuristic(n):
            return 0
    g_score = {n: float("inf") for n in graph.nodes}
    g_score[start] = 0
    f_score = {n: float("inf") for n in graph.nodes}
    f_score[start] = heuristic(start)
    came_from = {}
    open_set = [(f_score[start], start)]
    while open_set:
        _, current = heapq.heappop(open_set)
        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            return path[::-1]
        for neighbor, w in graph.neighbors(current):
            tentative = g_score[current] + w
            if tentative < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative
                f_score[neighbor] = tentative + heuristic(neighbor)
                heapq.heappush(open_set, (f_score[neighbor], neighbor))
    return []


def prim_mst(graph: Graph) -> List[Tuple[Any, Any, float]]:
    if graph.num_nodes() == 0:
        return []
    start = next(iter(graph.nodes))
    visited = {start}
    edges = []
    pq = []
    for v, w in graph.neighbors(start):
        heapq.heappush(pq, (w, start, v))
    while pq and len(visited) < graph.num_nodes():
        w, u, v = heapq.heappop(pq)
        if v in visited:
            continue
        visited.add(v)
        edges.append((u, v, w))
        for n, nw in graph.neighbors(v):
            if n not in visited:
                heapq.heappush(pq, (nw, v, n))
    return edges


def kruskal_mst(graph: Graph) -> List[Tuple[Any, Any, float]]:
    parent = {n: n for n in graph.nodes}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        parent[rx] = ry
        return True

    sorted_edges = sorted(graph.edges, key=lambda e: e[2])
    mst = []
    for u, v, w in sorted_edges:
        if union(u, v):
            mst.append((u, v, w))
            if len(mst) == graph.num_nodes() - 1:
                break
    return mst


def topological_sort(graph: Graph) -> List[Any]:
    in_deg = {n: graph.in_degree(n) for n in graph.nodes}
    queue = deque([n for n in graph.nodes if in_deg[n] == 0])
    order = []
    while queue:
        node = queue.popleft()
        order.append(node)
        for neighbor, _ in graph.neighbors(node):
            in_deg[neighbor] -= 1
            if in_deg[neighbor] == 0:
                queue.append(neighbor)
    return order


def detect_cycle(graph: Graph) -> bool:
    visited = set()
    rec_stack = set()

    def _dfs(node):
        visited.add(node)
        rec_stack.add(node)
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                if _dfs(neighbor):
                    return True
            elif neighbor in rec_stack:
                return True
        rec_stack.discard(node)
        return False

    for node in graph.nodes:
        if node not in visited:
            if _dfs(node):
                return True
    return False


def is_dag(graph: Graph) -> bool:
    return not detect_cycle(graph)


def connected_components(graph: Graph) -> List[List[Any]]:
    visited = set()
    components = []

    def _bfs(start):
        comp = []
        queue = deque([start])
        visited.add(start)
        while queue:
            node = queue.popleft()
            comp.append(node)
            for neighbor, _ in graph.neighbors(node):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)
        return comp

    for node in graph.nodes:
        if node not in visited:
            components.append(_bfs(node))
    return components


def strongly_connected_components(graph: Graph) -> List[List[Any]]:
    # Tarjan's algorithm simplified
    index_counter = [0]
    stack = []
    lowlink = {}
    index = {}
    on_stack = {}
    result = []

    def strongconnect(v):
        index[v] = index_counter[0]
        lowlink[v] = index_counter[0]
        index_counter[0] += 1
        stack.append(v)
        on_stack[v] = True
        for w, _ in graph.neighbors(v):
            if w not in index:
                strongconnect(w)
                lowlink[v] = min(lowlink[v], lowlink[w])
            elif on_stack.get(w, False):
                lowlink[v] = min(lowlink[v], index[w])
        if lowlink[v] == index[v]:
            comp = []
            while True:
                w = stack.pop()
                on_stack[w] = False
                comp.append(w)
                if w == v:
                    break
            result.append(comp)

    for v in graph.nodes:
        if v not in index:
            strongconnect(v)
    return result


def articulation_points(graph: Graph) -> List[Any]:
    # simplified: nodes whose removal increases components
    result = []
    for node in graph.nodes:
        g2 = graph.copy()
        g2.remove_node(node)
        if len(connected_components(g2)) > len(connected_components(graph)):
            result.append(node)
    return result


def bridges(graph: Graph) -> List[Tuple[Any, Any]]:
    result = []
    for u, v, w in list(graph.edges):
        g2 = graph.copy()
        g2.remove_edge(u, v)
        # check if u and v still connected
        if v not in bfs(g2, u):
            result.append((u, v))
    return result


def node_betweenness(graph: Graph) -> Dict[Any, float]:
    betweenness = {n: 0.0 for n in graph.nodes}
    for s in graph.nodes:
        # BFS
        stack = []
        pred = {v: [] for v in graph.nodes}
        sigma = {v: 0 for v in graph.nodes}
        dist = {v: -1 for v in graph.nodes}
        sigma[s] = 1
        dist[s] = 0
        queue = deque([s])
        while queue:
            v = queue.popleft()
            stack.append(v)
            for w, _ in graph.neighbors(v):
                if dist[w] < 0:
                    dist[w] = dist[v] + 1
                    queue.append(w)
                if dist[w] == dist[v] + 1:
                    sigma[w] += sigma[v]
                    pred[w].append(v)
        delta = {v: 0.0 for v in graph.nodes}
        while stack:
            w = stack.pop()
            for v in pred[w]:
                delta[v] += (sigma[v] / sigma[w]) * (1 + delta[w])
            if w != s:
                betweenness[w] += delta[w]
    # normalize
    n = graph.num_nodes()
    if n > 2:
        for v in betweenness:
            betweenness[v] /= ((n - 1) * (n - 2))
    return betweenness


def edge_betweenness(graph: Graph) -> Dict[Tuple[Any, Any], float]:
    # simplified: count
    result = {}
    for u, v, w in graph.edges:
        result[(u, v)] = 0.0
    return result


def pagerank(graph: Graph, damping: float = 0.85, max_iter: int = 100, tol: float = 1e-6) -> Dict[Any, float]:
    n = graph.num_nodes()
    if n == 0:
        return {}
    pr = {node: 1.0 / n for node in graph.nodes}
    for _ in range(max_iter):
        new_pr = {}
        for node in graph.nodes:
            s = 0.0
            for u in graph.nodes:
                if graph.has_edge(u, node):
                    out_deg = graph.out_degree(u)
                    if out_deg > 0:
                        s += pr[u] / out_deg
            new_pr[node] = (1 - damping) / n + damping * s
        # check convergence
        diff = sum(abs(new_pr[n] - pr[n]) for n in graph.nodes)
        pr = new_pr
        if diff < tol:
            break
    return pr


def hits(graph: Graph, max_iter: int = 100) -> Tuple[Dict[Any, float], Dict[Any, float]]:
    hubs = {n: 1.0 for n in graph.nodes}
    authorities = {n: 1.0 for n in graph.nodes}
    for _ in range(max_iter):
        new_auth = {}
        new_hub = {}
        for n in graph.nodes:
            new_auth[n] = sum(hubs[u] for u, v, w in graph.edges if v == n)
            new_hub[n] = sum(authorities[v] for u, v, w in graph.edges if u == n)
        # normalize
        na = sum(new_auth.values()) or 1
        nh = sum(new_hub.values()) or 1
        authorities = {n: new_auth[n] / na for n in graph.nodes}
        hubs = {n: new_hub[n] / nh for n in graph.nodes}
    return hubs, authorities


def eigenvector_centrality(graph: Graph, max_iter: int = 100) -> Dict[Any, float]:
    nodes = list(graph.nodes)
    n = len(nodes)
    {node: i for i, node in enumerate(nodes)}
    A = graph.adjacency_matrix()
    v = np.ones(n) / n
    for _ in range(max_iter):
        v = A @ v
        nv = np.linalg.norm(v)
        if nv > 0:
            v = v / nv
    return {nodes[i]: float(v[i]) for i in range(n)}


def closeness_centrality(graph: Graph) -> Dict[Any, float]:
    result = {}
    for node in graph.nodes:
        dists = dijkstra(graph, node)
        total = sum(d for d in dists.values() if d != float("inf"))
        n_reach = sum(1 for d in dists.values() if d != float("inf"))
        if total > 0 and n_reach > 1:
            result[node] = (n_reach - 1) / total
        else:
            result[node] = 0.0
    return result


def degree_centrality(graph: Graph) -> Dict[Any, float]:
    n = graph.num_nodes()
    if n <= 1:
        return {node: 0.0 for node in graph.nodes}
    return {node: graph.degree(node) / (n - 1) for node in graph.nodes}


def clustering_coefficient(graph: Graph, node: Any) -> float:
    neighbors = [n for n, w in graph.neighbors(node)]
    k = len(neighbors)
    if k < 2:
        return 0.0
    edges_between = 0
    for i in range(k):
        for j in range(i + 1, k):
            if graph.has_edge(neighbors[i], neighbors[j]):
                edges_between += 1
    max_edges = k * (k - 1) / 2
    return edges_between / max_edges if max_edges > 0 else 0.0


def average_clustering(graph: Graph) -> float:
    if graph.num_nodes() == 0:
        return 0.0
    return sum(clustering_coefficient(graph, n) for n in graph.nodes) / graph.num_nodes()


def transitivity(graph: Graph) -> float:
    triangles = 0
    triples = 0
    for node in graph.nodes:
        neighbors = [n for n, w in graph.neighbors(node)]
        k = len(neighbors)
        triples += k * (k - 1) / 2
        for i in range(k):
            for j in range(i + 1, k):
                if graph.has_edge(neighbors[i], neighbors[j]):
                    triangles += 1
    triangles /= 3
    if triples == 0:
        return 0.0
    return 3 * triangles / triples


def assortativity(graph: Graph) -> float:
    # degree assortativity
    edges = graph.edges
    if not edges:
        return 0.0
    deg = {n: graph.degree(n) for n in graph.nodes}
    num = 0.0
    den1 = 0.0
    den2 = 0.0
    for u, v, w in edges:
        num += deg[u] * deg[v]
        den1 += deg[u] ** 2
        den2 += deg[v] ** 2
    m = len(edges)
    if m == 0:
        return 0.0
    num /= m
    den1 /= m
    den2 /= m
    denom = (den1 * den2) ** 0.5
    if denom == 0:
        return 0.0
    return (num - den1 * den2) / denom


def modularity(graph: Graph, communities: List[List[Any]]) -> float:
    m = graph.num_edges()
    if m == 0:
        return 0.0
    Q = 0.0
    deg = {n: graph.degree(n) for n in graph.nodes}
    for comm in communities:
        set(comm)
        for u in comm:
            for v in comm:
                a_uv = 1 if graph.has_edge(u, v) else 0
                Q += a_uv - deg[u] * deg[v] / (2 * m)
    return Q / (2 * m)


def community_louvain(graph: Graph) -> List[List[Any]]:
    # simplified: each node its own community, then merge
    communities = [[n] for n in graph.nodes]
    # try merging
    improved = True
    while improved:
        improved = False
        for i in range(len(communities)):
            for j in range(i + 1, len(communities)):
                merged = communities[i] + communities[j]
                q_before = modularity(graph, communities)
                new_comms = [c for k, c in enumerate(communities) if k not in (i, j)] + [merged]
                q_after = modularity(graph, new_comms)
                if q_after > q_before:
                    communities = new_comms
                    improved = True
                    break
            if improved:
                break
    return communities


def label_propagation(graph: Graph, max_iter: int = 100) -> Dict[Any, int]:
    labels = {n: i for i, n in enumerate(graph.nodes)}
    for _ in range(max_iter):
        changed = False
        for node in graph.nodes:
            if not graph.neighbors(node):
                continue
            # most common label among neighbors
            from collections import Counter
            neighbor_labels = [labels[n] for n, w in graph.neighbors(node)]
            if not neighbor_labels:
                continue
            most_common = Counter(neighbor_labels).most_common(1)[0][0]
            if labels[node] != most_common:
                labels[node] = most_common
                changed = True
        if not changed:
            break
    return labels


def girvan_newman(graph: Graph, n_communities: int = 2) -> List[List[Any]]:
    g = graph.copy()
    while len(connected_components(g)) < n_communities:
        bs = bridges(g)
        if not bs:
            break
        u, v = bs[0]
        g.remove_edge(u, v)
    return connected_components(g)


def spectral_clustering(graph: Graph, n_clusters: int = 2) -> List[int]:
    L = graph.laplacian_matrix()
    # eigenvalues
    eigvals, eigvecs = np.linalg.eigh(L)
    # k smallest
    idx = np.argsort(eigvals)[:n_clusters]
    X = eigvecs[:, idx]
    # kmeans
    from sklearn.cluster import KMeans
    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    return km.fit_predict(X).tolist()


def graph_embedding(graph: Graph, dim: int = 2) -> Dict[Any, List[float]]:
    A = graph.adjacency_matrix()
    # simple: use eigenvectors of adjacency
    eigvals, eigvecs = np.linalg.eigh(A)
    idx = np.argsort(eigvals)[::-1][:dim]
    X = eigvecs[:, idx]
    nodes = sorted(graph.nodes, key=lambda x: str(x))
    return {nodes[i]: X[i].tolist() for i in range(len(nodes))}


def node2vec_embedding(graph: Graph, dim: int = 2, walk_length: int = 10, num_walks: int = 5) -> Dict[Any, List[float]]:
    # simplified random walk + PCA
    walks = []
    for _ in range(num_walks):
        for start in graph.nodes:
            walk = [start]
            cur = start
            for _ in range(walk_length):
                nbrs = graph.neighbors(cur)
                if not nbrs:
                    break
                nxt = np.random.choice([n for n, w in nbrs])
                walk.append(nxt)
                cur = nxt
            walks.append(walk)
    # count co-occurrences
    nodes = list(graph.nodes)
    idx = {n: i for i, n in enumerate(nodes)}
    n = len(nodes)
    cooc = np.zeros((n, n))
    for walk in walks:
        for i, node in enumerate(walk):
            for j in range(max(0, i - 2), min(len(walk), i + 3)):
                if i != j:
                    cooc[idx[node], idx[walk[j]]] += 1
    # SVD
    U, s, Vt = np.linalg.svd(cooc, full_matrices=False)
    X = U[:, :dim]
    return {nodes[i]: X[i].tolist() for i in range(n)}


def deepwalk_embedding(graph: Graph, dim: int = 2) -> Dict[Any, List[float]]:
    return node2vec_embedding(graph, dim=dim)


def graph_convolution(graph: Graph, features: np.ndarray, weights: np.ndarray) -> np.ndarray:
    A = graph.adjacency_matrix()
    # add self loops
    A = A + np.eye(A.shape[0])
    D = np.diag(1.0 / np.sqrt(A.sum(axis=1)))
    A_hat = D @ A @ D
    return A_hat @ features @ weights


def gcn_layer(features: np.ndarray, adj: np.ndarray, weights: np.ndarray) -> np.ndarray:
    # normalized adjacency
    D = np.diag(1.0 / np.sqrt(adj.sum(axis=1) + 1e-9))
    A_norm = D @ adj @ D
    return np.tanh(A_norm @ features @ weights)


def graph_attention(features: np.ndarray, adj: np.ndarray, weights: np.ndarray) -> np.ndarray:
    # simple attention
    n = features.shape[0]
    out = np.zeros_like(features)
    for i in range(n):
        nbrs = np.where(adj[i] > 0)[0]
        if len(nbrs) == 0:
            nbrs = [i]
        # attention weights
        att = np.exp(features[i] @ features[nbrs].T)
        att = att / (att.sum() + 1e-9)
        out[i] = (att[:, None] * features[nbrs]).sum(axis=0)
    return out @ weights


def message_passing(graph: Graph, features: np.ndarray, num_iters: int = 3) -> np.ndarray:
    A = graph.adjacency_matrix()
    # normalize
    D = np.diag(1.0 / (A.sum(axis=1) + 1e-9))
    A_norm = D @ A
    out = features.copy()
    for _ in range(num_iters):
        out = A_norm @ out
    return out


def aggregate_neighbors(graph: Graph, features: np.ndarray, agg: str = "mean") -> np.ndarray:
    A = graph.adjacency_matrix()
    out = np.zeros_like(features)
    for i in range(len(features)):
        nbrs = np.where(A[i] > 0)[0]
        if len(nbrs) == 0:
            out[i] = features[i]
            continue
        if agg == "mean":
            out[i] = features[nbrs].mean(axis=0)
        elif agg == "sum":
            out[i] = features[nbrs].sum(axis=0)
        elif agg == "max":
            out[i] = features[nbrs].max(axis=0)
        elif agg == "min":
            out[i] = features[nbrs].min(axis=0)
    return out


def graph_pooling(features: np.ndarray, clusters: List[int]) -> np.ndarray:
    # pool features by cluster assignment
    n_clusters = max(clusters) + 1
    out = np.zeros((n_clusters, features.shape[1]))
    counts = np.zeros(n_clusters)
    for i, c in enumerate(clusters):
        out[c] += features[i]
        counts[c] += 1
    counts = np.where(counts == 0, 1, counts)
    return out / counts[:, None]


def global_pool(features: np.ndarray, method: str = "mean") -> np.ndarray:
    if method == "mean":
        return features.mean(axis=0)
    if method == "sum":
        return features.sum(axis=0)
    if method == "max":
        return features.max(axis=0)
    if method == "min":
        return features.min(axis=0)
    return features.mean(axis=0)


def read_graph(path: str) -> Graph:
    import json

    with open(path) as f:
        data = json.load(f)
    return Graph.from_dict(data)


def write_graph(path: str, graph: Graph) -> None:
    import json

    with open(path, "w") as f:
        json.dump(graph.to_dict(), f)


def generate_random_graph(n: int, p: float = 0.3, directed: bool = False, seed: int = 42) -> Graph:
    rng = np.random.default_rng(seed)
    g = Graph(directed=directed)
    for i in range(n):
        g.add_node(i)
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < p:
                w = float(rng.random())
                g.add_edge(i, j, w)
    return g


def generate_scale_free_graph(n: int, m: int = 2, seed: int = 42) -> Graph:
    # Barabasi-Albert
    rng = np.random.default_rng(seed)
    g = Graph(directed=False)
    for i in range(m + 1):
        g.add_node(i)
    for i in range(m + 1):
        for j in range(i + 1, m + 1):
            g.add_edge(i, j, 1.0)
    # attach new nodes
    for new in range(m + 1, n):
        g.add_node(new)
        # preferential attachment
        degs = np.array([g.degree(nd) for nd in sorted(g.nodes)])
        probs = degs / degs.sum() if degs.sum() > 0 else None
        targets = rng.choice(sorted(g.nodes), size=min(m, len(g.nodes)), replace=False, p=probs)
        for t in targets:
            g.add_edge(new, t, 1.0)
    return g


def generate_small_world_graph(n: int, k: int = 4, p: float = 0.1, seed: int = 42) -> Graph:
    rng = np.random.default_rng(seed)
    g = Graph(directed=False)
    for i in range(n):
        g.add_node(i)
    # ring
    for i in range(n):
        for j in range(1, k // 2 + 1):
            g.add_edge(i, (i + j) % n, 1.0)
    # rewire
    for u, v, w in list(g.edges):
        if rng.random() < p:
            g.remove_edge(u, v)
            new_v = int(rng.integers(0, n))
            if new_v != u:
                g.add_edge(u, new_v, 1.0)
    return g


def generate_complete_graph(n: int) -> Graph:
    g = Graph(directed=False)
    for i in range(n):
        g.add_node(i)
    for i in range(n):
        for j in range(i + 1, n):
            g.add_edge(i, j, 1.0)
    return g


def generate_path_graph(n: int) -> Graph:
    g = Graph(directed=False)
    for i in range(n):
        g.add_node(i)
    for i in range(n - 1):
        g.add_edge(i, i + 1, 1.0)
    return g


def generate_cycle_graph(n: int) -> Graph:
    g = generate_path_graph(n)
    if n > 2:
        g.add_edge(n - 1, 0, 1.0)
    return g


def generate_star_graph(n: int) -> Graph:
    g = Graph(directed=False)
    for i in range(n):
        g.add_node(i)
    for i in range(1, n):
        g.add_edge(0, i, 1.0)
    return g


def generate_bipartite_graph(n1: int, n2: int, p: float = 0.3, seed: int = 42) -> Graph:
    rng = np.random.default_rng(seed)
    g = Graph(directed=False)
    for i in range(n1):
        g.add_node(("a", i))
    for j in range(n2):
        g.add_node(("b", j))
    for i in range(n1):
        for j in range(n2):
            if rng.random() < p:
                g.add_edge(("a", i), ("b", j), 1.0)
    return g


def generate_grid_graph(rows: int, cols: int) -> Graph:
    g = Graph(directed=False)
    for r in range(rows):
        for c in range(cols):
            g.add_node((r, c))
    for r in range(rows):
        for c in range(cols):
            if r + 1 < rows:
                g.add_edge((r, c), (r + 1, c), 1.0)
            if c + 1 < cols:
                g.add_edge((r, c), (r, c + 1), 1.0)
    return g


def generate_tree_graph(n: int, seed: int = 42) -> Graph:
    rng = np.random.default_rng(seed)
    g = Graph(directed=False)
    for i in range(n):
        g.add_node(i)
    for i in range(1, n):
        parent = int(rng.integers(0, i))
        g.add_edge(parent, i, 1.0)
    return g


def generate_forest_graph(n: int, n_trees: int = 3, seed: int = 42) -> Graph:
    rng = np.random.default_rng(seed)
    g = Graph(directed=False)
    for i in range(n):
        g.add_node(i)
    # assign to trees
    tree_id = rng.integers(0, n_trees, size=n)
    for t in range(n_trees):
        members = [i for i in range(n) if tree_id[i] == t]
        for i in range(1, len(members)):
            parent = members[rng.integers(0, i)]
            g.add_edge(parent, members[i], 1.0)
    return g


def compute_graph_stats(graph: Graph) -> Dict[str, Any]:
    return {
        "num_nodes": graph.num_nodes(),
        "num_edges": graph.num_edges(),
        "density": graph.density(),
        "avg_degree": sum(graph.degree(n) for n in graph.nodes) / graph.num_nodes() if graph.num_nodes() > 0 else 0.0,
        "avg_clustering": average_clustering(graph),
        "transitivity": transitivity(graph),
        "assortativity": assortativity(graph),
        "num_components": len(connected_components(graph)),
        "is_dag": is_dag(graph),
        "has_cycle": detect_cycle(graph),
    }


def compute_node_stats(graph: Graph) -> Dict[Any, Dict[str, Any]]:
    bc = node_betweenness(graph)
    cc = closeness_centrality(graph)
    dc = degree_centrality(graph)
    ec = eigenvector_centrality(graph)
    pr = pagerank(graph)
    hubs, auths = hits(graph)
    out = {}
    for n in graph.nodes:
        out[n] = {
            "degree": graph.degree(n),
            "betweenness": bc[n],
            "closeness": cc[n],
            "degree_centrality": dc[n],
            "eigenvector": ec[n],
            "pagerank": pr[n],
            "hub": hubs[n],
            "authority": auths[n],
            "clustering": clustering_coefficient(graph, n),
        }
    return out


def find_shortest_path(graph: Graph, start: Any, end: Any) -> List[Any]:
    dijkstra(graph, start)
    # reconstruct not stored; use BFS for unweighted
    # simple reconstruction via parent
    parent = {start: None}
    visited = {start}
    queue = deque([start])
    while queue:
        u = queue.popleft()
        if u == end:
            break
        for v, w in graph.neighbors(u):
            if v not in visited:
                visited.add(v)
                parent[v] = u
                queue.append(v)
    if end not in parent:
        return []
    path = []
    cur = end
    while cur is not None:
        path.append(cur)
        cur = parent[cur]
    return path[::-1]


def find_all_paths(graph: Graph, start: Any, end: Any, max_depth: int = 10) -> List[List[Any]]:
    result = []
    path = [start]
    visited = {start}

    def _dfs(node, depth):
        if depth > max_depth:
            return
        if node == end and len(path) > 1:
            result.append(list(path))
            return
        for neighbor, _ in graph.neighbors(node):
            if neighbor not in visited:
                visited.add(neighbor)
                path.append(neighbor)
                _dfs(neighbor, depth + 1)
                path.pop()
                visited.discard(neighbor)

    _dfs(start, 0)
    return result


def find_k_shortest_paths(graph: Graph, start: Any, end: Any, k: int = 3) -> List[List[Any]]:
    # Yen's algorithm simplified: just find k via removing edges
    paths = []
    first = find_shortest_path(graph, start, end)
    if not first:
        return []
    paths.append(first)
    # generate alternatives by removing edges
    for _ in range(k - 1):
        # remove an edge from last path
        if len(paths[-1]) < 2:
            break
        # try removing each edge
        found = None
        for i in range(len(paths[-1]) - 1):
            u, v = paths[-1][i], paths[-1][i + 1]
            g2 = graph.copy()
            g2.remove_edge(u, v)
            p = find_shortest_path(g2, start, end)
            if p and p not in paths:
                found = p
                break
        if found:
            paths.append(found)
        else:
            break
    return paths


def min_cut(graph: Graph, s: Any, t: Any) -> float:
    # Stoer-Wagner simplified: use max flow (Edmonds-Karp)
    return max_flow(graph, s, t)


def max_flow(graph: Graph, source: Any, sink: Any) -> float:
    # Edmonds-Karp
    g = graph.copy()
    # build residual
    cap = defaultdict(lambda: defaultdict(float))
    for u, v, w in g.edges:
        cap[u][v] += w
        cap[v][u] += 0.0
    flow = 0.0
    while True:
        # BFS
        parent = {source: None}
        queue = deque([source])
        while queue and sink not in parent:
            u = queue.popleft()
            for v, w in g.neighbors(u):
                if v not in parent and cap[u][v] > 1e-9:
                    parent[v] = u
                    queue.append(v)
                    if v == sink:
                        break
        if sink not in parent:
            break
        # find augmenting path capacity
        v = sink
        aug = float("inf")
        while parent[v] is not None:
            u = parent[v]
            aug = min(aug, cap[u][v])
            v = u
        # update
        v = sink
        while parent[v] is not None:
            u = parent[v]
            cap[u][v] -= aug
            cap[v][u] += aug
            v = u
        flow += aug
    return flow


def min_cut_value(graph: Graph) -> float:
    nodes = list(graph.nodes)
    if len(nodes) < 2:
        return 0.0
    best = float("inf")
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            c = max_flow(graph, nodes[i], nodes[j])
            if c < best:
                best = c
    return best if best != float("inf") else 0.0


def graph_coloring(graph: Graph) -> Dict[Any, int]:
    # greedy
    colors = {}
    for node in sorted(graph.nodes, key=lambda x: -graph.degree(x)):
        used = {colors[n] for n, w in graph.neighbors(node) if n in colors}
        c = 0
        while c in used:
            c += 1
        colors[node] = c
    return colors


def chromatic_number(graph: Graph) -> int:
    coloring = graph_coloring(graph)
    return max(coloring.values()) + 1 if coloring else 0


def is_bipartite(graph: Graph) -> bool:
    color = {}
    for start in graph.nodes:
        if start in color:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            u = queue.popleft()
            for v, w in graph.neighbors(u):
                if v not in color:
                    color[v] = 1 - color[u]
                    queue.append(v)
                elif color[v] == color[u]:
                    return False
    return True


def is_planar(graph: Graph) -> bool:
    # simplified: check Euler formula
    n = graph.num_nodes()
    m = graph.num_edges()
    if n < 4:
        return True
    # Kuratowski: e <= 3v - 6 for planar
    return m <= 3 * n - 6


def graph_diameter(graph: Graph) -> int:
    maxd = 0
    for n in graph.nodes:
        dists = dijkstra(graph, n)
        finite = [d for d in dists.values() if d != float("inf")]
        if finite:
            maxd = max(maxd, max(finite) if finite else 0)
    return int(maxd)


def graph_radius(graph: Graph) -> int:
    eccs = []
    for n in graph.nodes:
        dists = dijkstra(graph, n)
        finite = [d for d in dists.values() if d != float("inf")]
        if finite:
            eccs.append(max(finite))
    return int(min(eccs)) if eccs else 0


def graph_center(graph: Graph) -> List[Any]:
    ecc = {}
    for n in graph.nodes:
        dists = dijkstra(graph, n)
        finite = [d for d in dists.values() if d != float("inf")]
        ecc[n] = max(finite) if finite else 0
    if not ecc:
        return []
    r = min(ecc.values())
    return [n for n, e in ecc.items() if e == r]


def graph_periphery(graph: Graph) -> List[Any]:
    ecc = {}
    for n in graph.nodes:
        dists = dijkstra(graph, n)
        finite = [d for d in dists.values() if d != float("inf")]
        ecc[n] = max(finite) if finite else 0
    if not ecc:
        return []
    d = max(ecc.values())
    return [n for n, e in ecc.items() if e == d]


def average_path_length(graph: Graph) -> float:
    total = 0.0
    count = 0
    for s in graph.nodes:
        dists = dijkstra(graph, s)
        for t, d in dists.items():
            if s != t and d != float("inf"):
                total += d
                count += 1
    return total / count if count > 0 else 0.0


def global_efficiency(graph: Graph) -> float:
    n = graph.num_nodes()
    if n < 2:
        return 0.0
    total = 0.0
    for s in graph.nodes:
        dists = dijkstra(graph, s)
        for t, d in dists.items():
            if s != t and d != float("inf") and d > 0:
                total += 1.0 / d
    return total / (n * (n - 1))


def local_efficiency(graph: Graph, node: Any) -> float:
    nbrs = [n for n, w in graph.neighbors(node)]
    if len(nbrs) < 2:
        return 0.0
    sub = graph.subgraph(nbrs)
    return global_efficiency(sub)


def average_local_efficiency(graph: Graph) -> float:
    if graph.num_nodes() == 0:
        return 0.0
    return sum(local_efficiency(graph, n) for n in graph.nodes) / graph.num_nodes()


def rich_club_coefficient(graph: Graph, k: int) -> float:
    nodes = [n for n in graph.nodes if graph.degree(n) > k]
    if len(nodes) < 2:
        return 0.0
    sub = graph.subgraph(nodes)
    m = sub.num_edges()
    n = len(nodes)
    max_e = n * (n - 1) / 2
    return m / max_e if max_e > 0 else 0.0


def degree_distribution(graph: Graph) -> Dict[int, int]:
    from collections import Counter

    return dict(Counter(graph.degree(n) for n in graph.nodes))


def degree_histogram(graph: Graph) -> Tuple[List[int], List[int]]:
    dist = degree_distribution(graph)
    degs = sorted(dist.keys())
    counts = [dist[d] for d in degs]
    return degs, counts


def power_law_fit(graph: Graph) -> Dict[str, float]:
    degs = [graph.degree(n) for n in graph.nodes]
    from collections import Counter

    c = Counter(degs)
    # simple: fit log-log
    xs = np.array(sorted(c.keys()))
    ys = np.array([c[x] for x in xs])
    if len(xs) < 2:
        return {"alpha": 0.0, "xmin": 0}
    # filter zeros
    mask = (xs > 0) & (ys > 0)
    xs = xs[mask]
    ys = ys[mask]
    if len(xs) < 2:
        return {"alpha": 0.0, "xmin": 0}
    logx = np.log(xs)
    logy = np.log(ys)
    slope = np.polyfit(logx, logy, 1)[0]
    return {"alpha": float(-slope), "xmin": int(xs.min())}


def small_world_coefficient(graph: Graph) -> float:
    # sigma = (C/C_rand) / (L/L_rand)
    C = average_clustering(graph)
    L = average_path_length(graph)
    n = graph.num_nodes()
    if n < 2:
        return 0.0
    # random graph estimates
    p = graph.density()
    C_rand = p
    L_rand = math.log(n) / math.log(n * p) if (n * p) > 1 else 1.0
    if C_rand == 0 or L_rand == 0:
        return 0.0
    return (C / C_rand) / (L / L_rand)


def graph_entropy(graph: Graph) -> float:
    # degree entropy
    dist = degree_distribution(graph)
    n = graph.num_nodes()
    if n == 0:
        return 0.0
    probs = [v / n for v in dist.values()]
    return float(-sum(p * math.log(p) for p in probs if p > 0))


def von_neumann_entropy(graph: Graph) -> float:
    L = graph.laplacian_matrix()
    eigvals = np.linalg.eigvalsh(L)
    eigvals = np.clip(eigvals, 0, None)
    # normalize
    s = eigvals.sum()
    if s == 0:
        return 0.0
    p = eigvals / s
    p = p[p > 0]
    return float(-np.sum(p * np.log(p)))


def spectral_gap(graph: Graph) -> float:
    L = graph.laplacian_matrix()
    eigvals = np.sort(np.linalg.eigvalsh(L))
    if len(eigvals) < 2:
        return 0.0
    return float(eigvals[1] - eigvals[0])


def algebraic_connectivity(graph: Graph) -> float:
    return spectral_gap(graph)


def spectral_radius(graph: Graph) -> float:
    A = graph.adjacency_matrix()
    eigvals = np.linalg.eigvals(A)
    return float(np.max(np.abs(eigvals)))


def largest_eigenvalue(graph: Graph) -> float:
    A = graph.adjacency_matrix()
    eigvals = np.linalg.eigvals(A)
    return float(np.max(eigvals.real))


def trace_matrix(graph: Graph) -> float:
    A = graph.adjacency_matrix()
    return float(np.trace(A))


def determinant_matrix(graph: Graph) -> float:
    A = graph.adjacency_matrix()
    return float(np.linalg.det(A))


def main():
    print("graph module loaded")


if __name__ == "__main__":
    main()
