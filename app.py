import tkinter as tk
from tkinter import messagebox
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque

# Function to find the shortest path using BFS
def bfs_shortest_path(graph, start, goal):
    if start not in graph or goal not in graph:
        return None  # Return None if either start or goal is not in the graph
    
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
    
    # Debugging output
    print("Start:", start)
    print("Goal:", goal)
    print("Graph keys:", fantasy_graph.keys())
    
    if start not in fantasy_graph or goal not in fantasy_graph:
        messagebox.showerror("Error", "Invalid start or goal location.")
        return
    
    route = bfs_shortest_path(fantasy_graph, start, goal)
    
    if route:
        route_str = ' -> '.join(route)
        result_text.set(f"The shortest route from {start} to {goal} is: {route_str}")
        
        # Clear the previous plot
        plt.close('all')
        
        # Draw the new graph and route
        graph_plot = draw_graph(fantasy_graph, route)
        
        # Remove the previous canvas widget if it exists
        global canvas_widget
        if canvas_widget:
            canvas_widget.pack_forget()  # Hide the old canvas widget
        
        # Create and pack the new canvas widget
        canvas = FigureCanvasTkAgg(graph_plot.gcf(), master=app)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()
        
    else:
        result_text.set("No route found.")
        plt.close('all')

# Example fantasy graph with imaginary distances
fantasy_graph = {
    'Eldoria': {'Stormspire': 10, 'Verdant Hollow': 15, 'Dragon\'s Lair': 30},
    'Stormspire': {'Eldoria': 10, 'Verdant Hollow': 5, 'Obsidian Peaks': 20},
    'Verdant Hollow': {'Eldoria': 15, 'Stormspire': 5, 'Obsidian Peaks': 10, 'Celestia Bay': 25},
    'Obsidian Peaks': {'Stormspire': 20, 'Verdant Hollow': 10, 'Celestia Bay': 15, 'Shadowfen': 50},
    'Celestia Bay': {'Verdant Hollow': 25, 'Obsidian Peaks': 15, 'Shadowfen': 10},
    'Shadowfen': {'Obsidian Peaks': 50, 'Celestia Bay': 10}
}

# Set up the main application window
app = tk.Tk()
app.title("Fantasy Distance Finder")
app.geometry("800x600")

# Initialize canvas widget as None
canvas_widget = None

# Dropdowns for start and goal locations
locations = list(fantasy_graph.keys())
start_var = tk.StringVar(value=locations[0])
goal_var = tk.StringVar(value=locations[1])

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

# Start the Tkinter event loop
app.mainloop()
