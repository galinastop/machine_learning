import random

# Примечание Приложение работает со следующими версиями компонентов dash:
# dash                 2.6.2
# dash-core-components 2.0.0
# dash-cytoscape       0.2.0
# dash-html-components 2.0.0
# dash-table           5.0.0

import dash
import dash_cytoscape as cyto

import networkx as nx
import numpy as np
from dash import html, Output, Input, State

knp_edges = []
matrix = []
n = 10
k = 3

styles = [
    # Class selectors
    {
        'selector': '.point',
        'style': {
            'background-color': '#7369c5',
            'line-color': '#7369c5'
        }
    },
    {
        'selector': '.edge',
        'style': {
            'background-color': '#acc5dd',
            'line-color': '#acc5dd',
            'label': 'data(weight)'
        }
    },
    {
        'selector': '.knp_edge',
        'style': {
            'line-color': 'red',
        }
    },
    {
        'selector': '.hidden',
        'style': {
            'display': 'none',
        }
    }
]

app = dash.Dash(__name__)
app.layout = html.Div([
    html.Div([
        html.H4('Алгоритм Кластеризации путем нахождения КНП', className='title'),
        html.Button('Начать', id='generate-new', className='custom-btn btn-6', n_clicks=0),
        html.Button('КНП', id='show-knp', className='custom-btn btn-6', n_clicks=0),
        html.Button('Кластеры', id='show-clusters', className='custom-btn btn-6', n_clicks=0),
        html.Button('Сбросить', id='reset', className='custom-btn btn-6', n_clicks=0)
    ], className='wrapper'),
    cyto.Cytoscape(
        id='graph',
        layout={'name': 'preset'},
        elements=list(),
        style={
            'width': 'auto',
            'height': '600px',
            'background-color': 'whitesmoke',
            'border': '2px solid #c5a6e8'
        },
        stylesheet=styles
    )]
)


def calculate_distance_matrix(n):
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            if random.randint(0, 1) == 1:
                matrix[i][j] = matrix[j][i] = "{:.2f}".format(random.uniform(10, 99))

    return matrix


def create_graph(matrix):
    return nx.from_numpy_array(matrix)


def getData(graph, matrix):
    points = nx.spring_layout(graph, dim=2)

    edges, nodes = [], []
    for id, position in points.items():
        point_metadata = {
            'data': {
                'id': id,
                'label': str(id)
            },
            'position': {
                'x': position[0] * 1000,
                'y': position[1] * 1000
            },
            'classes': 'point'
        }
        nodes.append(point_metadata)

    for edge in graph.edges():
        s = edge[0]
        t = edge[1]
        edge_metadata = {
            'data': {
                'source': s,
                'target': t,
                'weight': matrix[s][t]
            },
            'classes': 'edge'
        }
        edges.append(edge_metadata)

    return nodes.extend(edges)
    # {'data': {'source': 3, 'target': 4}}

@app.callback(Output('graph', 'elements'),
              Input('show-knp', 'n_clicks'),
              Input('show-clusters', 'n_clicks'),
              Input('generate-new', 'n_clicks'),
              Input('reset', 'n_clicks'),
              State('graph', 'elements'))
def update_elements(show_knp, show_clusters, generate_new, reset_btn, elements):
    triggered = dash.ctx.triggered_id if not None else 'No clicks yet'

    if triggered == 'generate-new':
        return gererate()
    if triggered == 'show-knp':
        return draw_knp(reset(elements))
    if triggered == 'show-clusters':
        return draw_clusts(reset(elements))
    if triggered == 'reset':
        return reset(elements)
    return elements


def gererate():
    global knp_edges
    global n
    matrix = calculate_distance_matrix(n)
    graph = nx.from_numpy_matrix(matrix)

    min_i, min_j = find_min_edge(matrix)
    knp_edges = knp(matrix, min_i, min_j)
    return getData(graph, matrix)


def draw_clusts(elements):
    knp_edges_copy = knp_edges.copy()

    knp_edges_copy = knp_edges_copy[:-k + 1]

    for element in elements:
        if 'source' in element['data']:
            if not contains(element, knp_edges_copy):
                element['classes'] = 'hidden'

    return elements


def contains(element, knp):
    s = int(element['data']['source'])
    t = int(element['data']['target'])
    for e in knp:
        if s == e[0] and t == e[1] or \
                s == e[1] and t == e[0]:
            knp.remove(e)
            return True
    return False


def draw_knp(elements):
    knp_edges_copy = knp_edges.copy()

    for element in elements:
        if 'source' in element['data']:
            if contains(element, knp_edges_copy):
                element['classes'] = element['classes'] + ' knp_edge'

    return elements


def reset(elements):
    for element in elements:
        if 'source' in element['data']:
            element['classes'] = 'edge'
    return elements


def knp(matrix, min_i, min_j):
    l = len(matrix)

    in_tree = {min_i, min_j}
    out_tree = set(i for i in range(0, l)).difference(in_tree)

    knp = [[min_i, min_j, matrix[min_i][min_j]]]
    while len(out_tree) > 0:
        closest_node_in = 0
        closest_node_out = 0
        min_l = float('inf')
        for node_out in out_tree:
            for node_in in in_tree:
                cur_l = matrix[node_out, node_in]
                if cur_l != 0 and cur_l < min_l:
                    min_l = cur_l
                    closest_node_in = node_in
                    closest_node_out = node_out

        in_tree.add(closest_node_out)
        out_tree.remove(closest_node_out)

        knp.append([closest_node_in, closest_node_out, min_l])

    # sort by weight
    for i in range(len(knp)):
        for j in range(i + 1, len(knp)):
            if knp[i][2] > knp[j][2]:
                t = knp[i]
                knp[i] = knp[j]
                knp[j] = t

    return knp


def find_min_edge(matrix):
    min_i = min_j = -1
    min_w = float('inf')
    l = len(matrix)

    for i in range(l):
        for j in range(i + 1, l):
            w = matrix[i][j]
            if w != 0 and w < min_w:
                min_i = i
                min_j = j
                min_w = w

    return min_i, min_j


if __name__ == '__main__':
    app.run_server(debug=True)
