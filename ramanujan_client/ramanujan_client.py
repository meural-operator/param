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
            
            # Step 2.5: FATAL DATA LOSS PREVENTION - Save verified hits locally!
            if len(hits) > 0:
                print(f"\n[!!!] CRITICAL: {len(hits)} VERIFIED MATHEMATICAL HITS DISCOVERED!")
                print(f"[*] Writing to permanent local backup...")
                with open("ramanujan_discoveries.log", "a", encoding="utf-8") as f:
                    for ht in hits:
                        f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] CONSTANT: {work_unit.get('constant_name', 'Unknown')} | LHS: {ht.lhs_key} | a(n): {ht.rhs_an_poly} | b(n): {ht.rhs_bn_poly}\n")
                print(f"[+] Local backup secured at ramanujan_discoveries.log\n")
            
            # Step 3: Serialize and submit the verified math hits backwards (with Retry)
            retries = 0
            sync_success = False
            while not sync_success and retries < 5:
                sync_success = coordinator.submit_results(work_unit, hits)
                if not sync_success:
                    retries += 1
                    print(f"[-] Cloud Sync failed (Attempt {retries}/5). Retrying in 10 seconds...")
                    time.sleep(10)
            
            if not sync_success:
                print("[!] FATAL: Failed to sync results to the Cloud database after 5 attempts.")
                print("[*] Chunk will be automatically recovered and re-computed by Dead Letter peers later.")
                
            print("\n[*] Ready for next computation partition...\n")
            
    except KeyboardInterrupt:
        print("\n[!] KeyboardInterrupt detected! Gracefully shutting down Ramanujan@Home client.")
        sys.exit(0)

if __name__ == "__main__":
    main()
