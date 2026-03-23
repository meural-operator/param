import json
import os
import urllib.request
import urllib.error

def reset_and_expand_cursor():
    config_path = "../ramanujan_client/firebase_config.json"
    
    if not os.path.exists(config_path):
        print(f"[!] Please run this from the scripts folder. Could not find {config_path}")
        return
        
    with open(config_path, "r") as f:
        config = json.load(f)
        
    api_key = config["apiKey"]
    database_url = config["databaseURL"]
    
    # Authenticate anonymously using REST API
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
    req = urllib.request.Request(auth_url, data=b'{"returnSecureToken": true}', headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            auth_resp = json.loads(response.read().decode())
    except urllib.error.URLError as e:
        print("[!] Authentication failed", e)
        return
        
    id_token = auth_resp["idToken"]
    print("[*] Authenticated via REST...")
    
    new_cursor_state = {
        "degree": 2,
        "chunk_width": 30,     
        "a_min": -100000,
        "a_max": 100000,
        "b_min": -100000,
        "b_max": 100000,
        "current_a_pos": -100000, 
        "current_b_pos": -100000  
    }
    
    print(f"[*] Overwriting V2 Dynamic Task Cursor on Firebase Realtime DB...")
    db_url = f"{database_url}/v2_dynamic_tasks/cursor.json?auth={id_token}"
    req = urllib.request.Request(db_url, data=json.dumps(new_cursor_state).encode(), headers={'Content-Type': 'application/json'}, method='PUT')
    try:
        with urllib.request.urlopen(req) as response:
            print("[+] Cursor successfully expanded with Chunk width 30! Your clients will now resume computing.")
    except urllib.error.URLError as e:
        print("[!] Failed to update database:", e)

if __name__ == "__main__":
    reset_and_expand_cursor()
