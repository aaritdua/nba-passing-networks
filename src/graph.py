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
    neighbours: dict[_WeightedDirectedVertex, int]

    def __init__(self, item: Any) -> None:
        """Initialize a new vertex with the given item

        This vertex is initialized with no neighbours.
        """
        self.item = item
        self.neighbours = {}


class WeightedDirectedGraphs:
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

    def add_directed_edge(self, item1: Any, item2: Any, weight: int = 1) -> None:
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
