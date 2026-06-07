import networkx as nx
import time
import pickle
import random
import os

MODEL_PATH = '../backend/app/core/visitor_model.pkl'

def main():
    # Load ML Multiplier
    multiplier = 1.0
    if os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, 'rb') as f:
            data = pickle.load(f)
            multiplier = data.get('multiplier', 1.0)
            print(f"Loaded ML Congestion Multiplier: {multiplier:.2f}x")
    else:
        print("ML Model not found. Using default multiplier of 1.0x")
        
    print("\nGenerating massive Mahakumbh scale graph (5,000 nodes, 15,000 edges)...")
    # Generate a random spatial graph (similar to a city grid with diagonal paths)
    # Using a random geometric graph to simulate physical proximity
    G = nx.random_geometric_graph(5000, 0.05, seed=42)
    
    # Assign weights with the congestion multiplier
    for u, v in G.edges():
        base_distance = random.uniform(50.0, 500.0)
        # Apply the congestion multiplier to the distance to simulate walking difficulty
        G[u][v]['weight'] = base_distance * multiplier
        
    # Pick a random source and target that are connected
    source, target = list(G.nodes())[0], list(G.nodes())[-1]
    
    # Ensure they are connected, otherwise pick largest connected component
    if not nx.has_path(G, source, target):
        largest_cc = max(nx.connected_components(G), key=len)
        nodes = list(largest_cc)
        source, target = nodes[0], nodes[-1]
        
    print(f"\n--- Routing Algorithm Benchmarks (Source: {source} -> Target: {target}) ---")
    
    # 1. Dijkstra
    start_t = time.perf_counter()
    path_d = nx.dijkstra_path(G, source, target, weight='weight')
    time_d = time.perf_counter() - start_t
    print(f"Dijkstra's Algorithm   -> Time: {time_d*1000:.2f} ms | Path Length: {len(path_d)}")
    
    # 2. A* (A-Star)
    # A* requires a heuristic. For random geometric graphs, we can use euclidean distance between pos attributes
    def dist_heuristic(n1, n2):
        x1, y1 = G.nodes[n1]['pos']
        x2, y2 = G.nodes[n2]['pos']
        return ((x1 - x2)**2 + (y1 - y2)**2)**0.5 * 1000 * multiplier # scaled up heuristic
        
    start_t = time.perf_counter()
    path_a = nx.astar_path(G, source, target, heuristic=dist_heuristic, weight='weight')
    time_a = time.perf_counter() - start_t
    print(f"A* Search Algorithm    -> Time: {time_a*1000:.2f} ms | Path Length: {len(path_a)}")
    
    # 3. Bellman-Ford
    start_t = time.perf_counter()
    path_b = nx.bellman_ford_path(G, source, target, weight='weight')
    time_b = time.perf_counter() - start_t
    print(f"Bellman-Ford Algorithm -> Time: {time_b*1000:.2f} ms | Path Length: {len(path_b)}")
    
    # Determine winner
    times = {'Dijkstra': time_d, 'A*': time_a, 'Bellman-Ford': time_b}
    winner = min(times, key=times.get)
    print(f"\nWinning Algorithm: {winner}")
    print(f"We will implement {winner} into the FastAPI backend routing engine!")

if __name__ == "__main__":
    main()
