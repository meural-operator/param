import sys
import os

# Ensure the framework root resolves safely 
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from engine_bridge.v3_executor import V3PipelineExecutor
from ramanujan.constants.euler_mascheroni import EulerMascheroniTarget
from ramanujan.enumerators.cuda_gcf import CUDAEnumerator
from ramanujan.math_ai.strategies.mcts_strategy import MCTSStrategy
from ramanujan.coordinators.firebase_coordinator import FirebaseCoordinator

def main():
    print("==================================================")
    print("        Ramanujan Engine V3 - Subspace Node       ")
    print("==================================================")
    
    config_path = "firebase_config.json"
    if not os.path.exists(config_path):
        print(f"[*] Missing {config_path}. Auto-generating default public access credentials...")
        import json
        default_config = {
            "apiKey": "AIzaSyCp1GpLSTGfjayQ-Yk0tW3dot1cOVpwxSE",
            "authDomain": "ramanujan-engine.firebaseapp.com",
            "databaseURL": "https://ramanujan-engine-default-rtdb.firebaseio.com",
            "projectId": "ramanujan-engine",
            "storageBucket": "ramanujan-engine.firebasestorage.app",
            "messagingSenderId": "662438808921",
            "appId": "1:662438808921:web:7d286acd925a08f1efd048",
            "measurementId": "G-LT414LS49S"
        }
        with open(config_path, "w") as f:
            json.dump(default_config, f, indent=4)
            
    print("[*] Instantiating Generalized Discovery Plugins...")
    target = EulerMascheroniTarget()
    network = FirebaseCoordinator(config_path)
    engine = CUDAEnumerator()
    
    # Check if AI weights are distributed, and dynamically snap them into the pipeline
    strategies = []
    mcts = MCTSStrategy(pt_filename="em_mcts.pt")
    if mcts.network is not None:
        strategies.append(mcts)
        print("[+] Deep Reinforcement Learning limits fully active.")
    else:
        print("[-] Deep limits degraded. Engine operating via brute force fallback.")
        
    executor = V3PipelineExecutor(
        target=target,
        strategies=strategies,
        engine=engine,
        network=network
    )
    
    executor.run_compute_loop()

if __name__ == "__main__":
    main()
