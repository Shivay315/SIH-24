import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
import requests
import threading

# Function to find the shortest path using BFS
def bfs_shortest_path(graph, start, goal):
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

# Function to draw the graph
def draw_graph(graph, path=None):
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
    
    return plt

# Function to handle the button click
def find_route():
    start = start_var.get()
    goal = goal_var.get()
    
    try:
        response = requests.get('http://127.0.0.1:5000/get_fantasy_graph')
        fantasy_graph = response.json()
    except Exception as e:
        messagebox.showerror("Error", "Could not fetch data from server.")
        return
    
    if start not in fantasy_graph or goal not in fantasy_graph:
        messagebox.showerror("Error", "Invalid start or goal location.")
        return
    
    route = bfs_shortest_path(fantasy_graph, start, goal)
    
    if route:
        route_str = ' -> '.join(route)
        result_text.set(f"The shortest route from {start} to {goal} is: {route_str}")
        
        # Draw the graph and route
        plt.figure(figsize=(8, 6))
        plt.clf()
        graph_plot = draw_graph(fantasy_graph, route)
        
        # Embed the plot in the Tkinter window
        canvas = FigureCanvasTkAgg(graph_plot.gcf(), master=app)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()
        
    else:
        result_text.set("No route found.")
        plt.close('all')

# Set up the main application window
app = tk.Tk()
app.title("Fantasy Distance Finder")
app.geometry("800x600")

# Dropdowns for start and goal locations
locations = []
start_var = tk.StringVar()
goal_var = tk.StringVar()

def update_locations():
    global locations
    try:
        response = requests.get('http://127.0.0.1:5000/get_fantasy_graph')
        fantasy_graph = response.json()
        locations = list(fantasy_graph.keys())
        start_var.set(locations[0])
        goal_var.set(locations[1])
        start_menu['menu'].delete(0, 'end')
        goal_menu['menu'].delete(0, 'end')
        for loc in locations:
            start_menu['menu'].add_command(label=loc, command=tk._setit(start_var, loc))
            goal_menu['menu'].add_command(label=loc, command=tk._setit(goal_var, loc))
    except Exception as e:
        messagebox.showerror("Error", "Could not fetch locations from server.")

update_locations()

start_label = tk.Label(app, text="Start Location:")
start_label.pack(pady=5)
start_menu = tk.OptionMenu(app, start_var, *locations)
start_menu.pack(pady=5)

goal_label = tk.Label(app, text="Goal Location:")
goal_label.pack(pady=5)
goal_menu = tk.OptionMenu(app, goal_var, *locations)
goal_menu.pack(pady=5)

# Button to trigger the route finding
find_button = tk.Button(app, text="Find Shortest Route", command=find_route)
find_button.pack(pady=20)

# Label to display the result
result_text = tk.StringVar()
result_label = tk.Label(app, textvariable=result_text, justify=tk.LEFT, anchor="w")
result_label.pack(pady=20, fill="both", expand=True)

def run_flask():
    import app
    app.app.run(debug=False, use_reloader=False)

# Start the Flask server in a separate thread
flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

# Start the Tkinter event loop
app.mainloop()
