import networkx as nx
from plotly.graph_objs import Scatter, Figure
from graph import WeightedDirectedGraph
import algorithms


def visualize_graph(graph: WeightedDirectedGraph,
                    layout: str = 'spring_layout') -> None:
    """Use plotly and networkx to visualize the given graph.

    Optional arguments:
    - layout: which graph layout algorithm to use
    """
    graph_nx = graph.to_networkx()

    pos = getattr(nx, layout)(graph_nx)

    # Edge trace
    x_edges = []
    y_edges = []

    for u, v in graph_nx.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        x_edges.extend([x0, x1, None])
        y_edges.extend([y0, y1, None])

    trace_edges = Scatter(
        x=x_edges,
        y=y_edges,
        mode='lines',
        name='edges',
        line=dict(width=1),
        hoverinfo='none'
    )

    # Node trace
    centrality_score = algorithms.weighted_centrality(graph)

    x_nodes = []
    y_nodes = []
    node_text = []
    node_sizes = []

    for node in graph_nx.nodes():
        x, y = pos[node]
        x_nodes.append(x)
        y_nodes.append(y)

        c = centrality_score[node]
        node_text.append(f'Player: {node}<br>Centrality: {c:.3f}')
        node_sizes.append(20 + 40 * c)

    trace_nodes = Scatter(x=x_nodes,
                          y=y_nodes,
                          mode='markers+text',
                          text=[str(node) for node in graph_nx.nodes()],
                          textposition='top center',
                          hoverinfo='text',
                          hovertext=node_text,
                          marker=dict(
                              size=node_sizes,
                              line=dict(width=1)
                          )
                          )

    data1 = [trace_edges, trace_nodes]
    fig = Figure(data=data1)
    fig.update_layout({'showlegend': False})
    fig.update_xaxes(showgrid=False, zeroline=False, visible=False)
    fig.update_yaxes(showgrid=False, zeroline=False, visible=False)
    fig.show()


if __name__ == '__main__':
    import doctest

    # import python_ta
    #
    # python_ta.check_all(config={
    #     'max-line-length': 120,
    #     'disable': ['static_type_checker'],
    #     'extra-imports': ['csv', 'networkx'],
    #     'allowed-io': ['load_review_graph'],
    #     'max-nested-blocks': 4
    # })
