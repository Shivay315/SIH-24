from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from collections import deque

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///foo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.String(200), nullable=False)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_fantasy_graph', methods=['GET'])
def get_fantasy_graph():
    fantasy_graph = {
        'Eldoria': {'Stormspire': 10, 'Verdant Hollow': 15, 'Dragon\'s Lair': 30},
        'Stormspire': {'Eldoria': 10, 'Verdant Hollow': 5, 'Obsidian Peaks': 20},
        'Verdant Hollow': {'Eldoria': 15, 'Stormspire': 5, 'Obsidian Peaks': 10, 'Celestia Bay': 25},
        'Obsidian Peaks': {'Stormspire': 20, 'Verdant Hollow': 10, 'Celestia Bay': 15, 'Shadowfen': 50},
        'Celestia Bay': {'Verdant Hollow': 25, 'Obsidian Peaks': 15, 'Shadowfen': 10},
        'Shadowfen': {'Obsidian Peaks': 50, 'Celestia Bay': 10}
    }
    return jsonify(fantasy_graph)

@app.route('/find_route', methods=['POST'])
def find_route():
    data = request.json
    start = data.get('start')
    goal = data.get('goal')

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
            
            for neighbor in graph[current_node]:
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return None

    route = bfs_shortest_path(fantasy_graph, start, goal)
    
    if route:
        route_str = ' -> '.join(route)
        return jsonify({'route': route_str})
    else:
        return jsonify({'route': 'No route found'})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)  # use_reloader=False to avoid running twice in debug mode
