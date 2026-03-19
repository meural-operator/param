import time
import sys
import os

from network.coordinator import ServerCoordinator
from engine_bridge.executor import RamanujanExecutor

def main():
    print("==================================================")
    print("           Ramanujan@Home - Compute Node          ")
    print("==================================================")
    
    config_path = "firebase_config.json"
    if not os.path.exists(config_path):
        print(f"[!] ERROR: {config_path} not found.")
        print("[*] Please create 'firebase_config.json' and add your Google Firebase Web SDK credentials.")
        return
    
    # Initialize the Firebase REST coordinator
    coordinator = ServerCoordinator(config_path=config_path)
    
    # 1. Authentication
    id_token = coordinator.authenticate_user()
    if not id_token:
        print("[!] Client shutting down due to authentication failure.")
        sys.exit(1)
        
    print(f"[*] Authenticated as UID: {coordinator.user.get('localId', coordinator.user.get('userId'))}")
        
    # Initialize the PyTorch Execution Bridge
    executor = RamanujanExecutor()
    
    print("[*] Engine V2 Initialized. Entering Community compute loop...\n")
    
    try:
        while True:
            # Step 1: Request a mutually-exclusive Tensor bounds matrix from the server
            work_unit = coordinator.request_work_unit()
            
            if work_unit is None:
                print("[-] Sleeping for 60 seconds before checking for new Work Units...")
                time.sleep(60)
                continue
                
            # Step 2: Spin up the Async Dual-Thread GPU engine over the bounded space
            hits = executor.execute_work_unit(work_unit)
            
            # Step 3: Serialize and submit the verified math hits backwards
            sync_success = coordinator.submit_results(work_unit, hits)
            
            if not sync_success:
                print("[!] Warning: Failed to sync results to the Cloud database.")
                
            print("\n[*] Ready for next computation partition...\n")
            
    except KeyboardInterrupt:
        print("\n[!] KeyboardInterrupt detected! Gracefully shutting down Ramanujan@Home client.")
        sys.exit(0)

if __name__ == "__main__":
    main()
