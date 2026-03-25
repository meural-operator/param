"""
Ramanujan@Home — Firebase Work Queue Seeder
Seeds the /problems/euler-mascheroni/tasks/cursor path with initial work parameters
so that edge nodes can begin distributed computation immediately.

Usage:
    python scripts/seed_firebase_work.py
"""
import json
import urllib.request
import urllib.error
import sys
import os

# Use the same config the edge node uses
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'clients', 'firebase_config.json')

def main():
    print("==================================================")
    print("   Ramanujan@Home - Work Queue Seeder")
    print("==================================================")
    
    config_path = os.path.abspath(CONFIG_PATH)
    if not os.path.exists(config_path):
        print(f"[!] Missing {config_path}. Please run edge_node.py once first to generate it.")
        sys.exit(1)
    
    with open(config_path, "r") as f:
        config = json.load(f)
    
    api_key = config["apiKey"]
    db_url = config["databaseURL"]
    
    # 1. Authenticate anonymously
    print("[*] Authenticating with Firebase...")
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    req = urllib.request.Request(auth_url, data=b'{"returnSecureToken": true}', headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            auth_resp = json.loads(response.read().decode())
            id_token = auth_resp["idToken"]
            print("[+] Authenticated successfully.")
    except urllib.error.URLError as e:
        print(f"[!] Auth failed: {e}")
        sys.exit(1)
    
    # 2. Seed the cursor-based work queue for euler-mascheroni
    print("[*] Seeding work queue for euler-mascheroni...")
    
    cursor_data = {
        "current_a_pos": 0,
        "current_b_pos": 0,
        "degree": 2,
        "step_size": 10,
        "status": "active"
    }
    
    cursor_url = f"{db_url}/problems/euler-mascheroni/tasks/cursor.json?auth={id_token}"
    req = urllib.request.Request(
        cursor_url,
        data=json.dumps(cursor_data).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    try:
        with urllib.request.urlopen(req) as response:
            print("[+] Cursor seeded successfully.")
    except urllib.error.URLError as e:
        print(f"[!] Cursor seed failed: {e}")
        sys.exit(1)
    
    # 3. Set problem config
    print("[*] Setting problem config...")
    config_data = {
        "status": "active",
        "name": "euler-mascheroni",
        "description": "Generalized Continued Fraction search for Euler-Mascheroni constant",
        "created_at": int(__import__('time').time() * 1000)
    }
    
    config_url = f"{db_url}/problems/euler-mascheroni/config.json?auth={id_token}"
    req = urllib.request.Request(
        config_url,
        data=json.dumps(config_data).encode(),
        headers={'Content-Type': 'application/json'},
        method='PUT'
    )
    try:
        with urllib.request.urlopen(req) as response:
            print("[+] Problem config set.")
    except urllib.error.URLError as e:
        print(f"[!] Config seed failed: {e}")
    
    print("\n[+] Work queue ready! Edge nodes will now pick up work automatically.")

if __name__ == "__main__":
    main()
