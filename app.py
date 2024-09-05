from flask import Flask, render_template, request, jsonify
import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from collections import deque

app = Flask(__name__)

# Example fantasy graph with imaginary distances
fantasy_graph = {
    'Eldoria': {'Stormspire': 10, 'Verdant Hollow': 15, 'Dragon\'s Lair': 30},
    'Stormspire': {'Eldoria': 10, 'Verdant Hollow': 5, 'Obsidian Peaks': 20},
    'Verdant Hollow': {'Eldoria': 15, 'Stormspire': 5, 'Obsidian Peaks': 10, 'Celestia Bay': 25},
    'Obsidian Peaks': {'Stormspire': 20, 'Verdant Hollow': 10, 'Celestia Bay': 15, 'Shadowfen': 50},
    'Celestia Bay': {'Verdant Hollow': 25, 'Obsidian Peaks': 15, 'Shadowfen': 10},
    'Shadowfen': {'Obsidian Peaks': 50, 'Celestia Bay': 10}
}

def bfs_shortest_path(graph, start, goal):
    if start not in graph or goal not in graph:
        return None
    
    queue = deque([(start, [start])])
    visited = set()
    
    while queue:
        (current_node, path) = queue.popleft()
        
        if current_node in visited:
            continue
        
        visited.add(current_node)
        
        if current_node == goal:
            return path
        
        for neighbor in graph.get(current_node, {}):
            if neighbor not in visited:
                queue.append((neighbor, path + [neighbor]))
    
    return None

def draw_graph(graph, path=None):
    import matplotlib
    matplotlib.use('Agg')  # Use a non-GUI backend
    G = nx.Graph()
    
    # Add nodes and edges
    for node, neighbors in graph.items():
        for neighbor, distance in neighbors.items():
            G.add_edge(node, neighbor, weight=distance)
    
    pos = nx.spring_layout(G)
    plt.figure(figsize=(8, 6))
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=10, font_weight='bold')
    
    if path:
        edges = list(zip(path, path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color='r', width=2, style='dashed')
    
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    
    plt.title("Fantasy Locations and Routes")
    plt.axis('off')
    
    # Save the plot to a BytesIO object and encode it as base64
    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()
    plt.close('all')
    
    return plot_url

@app.route('/')
def index():
    locations = list(fantasy_graph.keys())
    return render_template('index.html', locations=locations)

@app.route('/find_route', methods=['POST'])
def find_route():
    start = request.form.get('start')
    goal = request.form.get('goal')
    
    if start not in fantasy_graph or goal not in fantasy_graph:
        return jsonify({"error": "Invalid start or goal location."})
    
    route = bfs_shortest_path(fantasy_graph, start, goal)
    
    if route:
        route_str = ' -> '.join(route)
        plot_url = draw_graph(fantasy_graph, route)
        return jsonify({"route": route_str, "plot_url": plot_url})
    else:
        return jsonify({"route": "No route found.", "plot_url": None})

if __name__ == '__main__':
    app.run(debug=True)
