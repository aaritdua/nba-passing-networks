from __future__ import annotations
from typing import Any


class _WeightedDirectedVertex:
    """A vertex in a weighted directed graph representing a player

    Instance Attributes:
        - item: The data stored in this vertex
        - neighbours: A dictionary mapping each adjacent vertex to the
          weight of the directed edge from this vertex to that vertex.

    Representation Invariants:
        - self not in self.neighbours
    """
    item: Any
    neighbours: dict[_WeightedDirectedVertex, float]

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.neighbours = {}


class WeightedDirectedGraph:
    """A graph used to represent a passing network.
    """
    # Private Instance Attributes:
    #     - _vertices:
    #         A collection of the vertices contained in this graph.
    #         Maps item to _WeightedDirectedVertex object.
    _vertices: dict[Any, _WeightedDirectedVertex]

    def __init__(self) -> None:
        """Initialize an empty graph (no vertices or edges)."""
        self._vertices = {}

    def add_vertex(self, item: Any) -> None:
        """Add a vertex with the given item to this graph.

        The new vertex is not adjacent to any other vertices.
        Do nothing if the given item is already in this graph.
        """
        if item not in self._vertices:
            self._vertices[item] = _WeightedDirectedVertex(item)

    def add_directed_edge(self, item1: Any, item2: Any, weight: float = 1.0) -> None:
        """Add a directed edge from the vertex given by item1 to the vertex given by item2 in this graph,
        with the given weight.

        Raise a ValueError if item1 or item2 do not appear as vertices in this graph.

        Preconditions:
            - item1 != item2
        """
        if item1 in self._vertices and item2 in self._vertices:
            v1 = self._vertices[item1]
            v2 = self._vertices[item2]

            # Add the new directed edge
            v1.neighbours[v2] = weight
        else:
            # We didn't find an existing vertex for both items.
            raise ValueError

    def get_out_neighbors(self, item: Any) -> set:
        """Return a set of the out-neighbours (A vertex that a given vertex has a directed edge to) of the given item.

        Note that the *items* are returned, not the _WeightedDirectedVertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            v = self._vertices[item]
            return {neighbour.item for neighbour in v.neighbours}
        else:
            raise ValueError

    def get_in_neighbors(self, item: Any) -> set:
        """Return a set of the in-neighbours (A vertex that has a directed edge to the given vertex) of the given item.

        Note that the *items* are returned, not the _WeightedDirectedVertex objects themselves.

        Raise a ValueError if item does not appear as a vertex in this graph.
        """
        if item in self._vertices:
            in_neighbors = set()
            v = self._vertices[item]
            for u in self._vertices.values():
                if v in u.neighbours:
                    in_neighbors.add(u.item)
            return in_neighbors
        else:
            raise ValueError
        
    def bfs(self, start: Any) -> dict[Any, int]:
        """
        Return a dictionary mapping each reachable vertex to its distance from start,
        measured in number of directed edges.
        
        The start vertex itself is included with distance 0. Only vertices reachable
        by following directed edges from start are included.
        
        Raise a ValueError if start does not appear as a vertex in this graph.
        """
        if start not in self._vertices:
            raise ValueError
        visited = {}
        queue = [start]
        visited[start] = 0
        while queue:
            v = queue.pop(0)
            vertex = self._vertices[v]
            for vert in vertex.neighbours:
                if vert.item not in visited:
                    visited[vert.item] = visited[v] + 1
                    queue.append(vert.item)
        return visited
    
    def dfs(self, start: Any) -> list:
        """
        Return a list of items visited in depth-first order starting from start.
        
        Follows directed edges as deep as possible before backtracking. Each item
        appears at most once in the returned list. The start vertex is included first.
        
        Raise a ValueError if start does not appear as a vertex in this graph.
        """
        if start not in self._vertices:
            raise ValueError
        visited = {}
        stack = [start]
        visited[start] = 0
        while stack:
            v = stack.pop()
            vertex = self._vertices[v]
            for vert in vertex.neighbours:
                if vert.item not in visited:
                    visited[vert.item] = visited[v] + 1
                    stack.append(vert.item)
        return list(visited.keys())
    
    def get_edges(self) -> list[tuple]:
        """
        Return a list of all directed edges in this graph as (item1, item2, weight) tuples, 
        where item1 -> item2 with the given weight.
        """
        edges = []
        for item in self._vertices:
            vertex = self._vertices[item]
            for vert in vertex.neighbours:
                edges.append((vertex.item, vert.item, vertex.neighbours[vert]))
        return edges
