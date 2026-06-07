import networkx as nx
from typing import List, Dict, Any
import time
import pickle
import os

class RoutingEngine:
    def __init__(self):
        # We penalize recently used paths to avoid thundering herds.
        # Key: edge_id, Value: timestamp of last recommendation
        self.recent_paths_penalty: Dict[str, float] = {}
        self.PENALTY_DURATION_SEC = 30
        self.PENALTY_MULTIPLIER = 1.5
        
        # Load ML Multiplier
        self.ml_multiplier = 1.0
        model_path = os.path.join(os.path.dirname(__file__), 'visitor_model.pkl')
        if os.path.exists(model_path):
            try:
                with open(model_path, 'rb') as f:
                    data = pickle.load(f)
                    self.ml_multiplier = data.get('multiplier', 1.0)
            except Exception:
                pass

    def calculate_route(self, state, source_id: str, target_id: str) -> List[str]:
        """
        Calculates the safest route using NetworkX A* Algorithm.
        Expects state to be the GlobalState instance.
        """
        G = nx.Graph()

        # Add nodes with position for A* heuristic
        for node_id, node_data in state.nodes.items():
            G.add_node(node_id, pos=(node_data.get("latitude", 0), node_data.get("longitude", 0)))

        # Add edges with weights
        current_time = time.time()
        for edge_id, edge_data in state.edges.items():
            u = edge_data["source_id"]
            v = edge_data["target_id"]
            base_dist = edge_data["base_distance_meters"]
            
            u_score = state.nodes.get(u, {}).get("safety_score", 100)
            v_score = state.nodes.get(v, {}).get("safety_score", 100)
            
            if u_score < 30 or v_score < 30:
                congestion = 1000000 # Closed node!
            else:
                congestion = edge_data["current_congestion_multiplier"]
            
            # Base weight scaled by ML congestion multiplier
            weight = base_dist * congestion * self.ml_multiplier

            # Apply thundering herd penalty if recently recommended
            last_used = self.recent_paths_penalty.get(edge_id, 0)
            if current_time - last_used < self.PENALTY_DURATION_SEC:
                weight *= self.PENALTY_MULTIPLIER

            G.add_edge(u, v, weight=weight, id=edge_id)

        # A* Heuristic function using Euclidean distance approximation
        def dist_heuristic(n1, n2):
            try:
                lat1, lon1 = G.nodes[n1]['pos']
                lat2, lon2 = G.nodes[n2]['pos']
                # Approximate 1 degree ~ 111,000 meters. So Euclidean * 111000 = dist in meters.
                dist_meters = ((lat1 - lat2)**2 + (lon1 - lon2)**2)**0.5 * 111000
                return dist_meters * self.ml_multiplier
            except KeyError:
                return 0

        try:
            # Calculate shortest path based on dynamic weights using A*
            path = nx.astar_path(G, source=source_id, target=target_id, heuristic=dist_heuristic, weight='weight')
            
            # Record the edges used to penalize them for the next few seconds
            for i in range(len(path) - 1):
                u = path[i]
                v = path[i+1]
                edge_data = G.get_edge_data(u, v)
                if edge_data and "id" in edge_data:
                    self.recent_paths_penalty[edge_data["id"]] = current_time
                    
            return path
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return []

routing_engine = RoutingEngine()
