import json
import os
import time
import requests
import pyrebase

class ServerCoordinator:
    """
    Handles the Cloud-Native Firebase Realtime Database syncing 
    along with Google Sign-In Authentication via Pyrebase4.
    """
    def __init__(self, config_path="firebase_config.json", token_path="user_token.json"):
        self.config_path = config_path
        self.token_path = token_path
        self.firebase = None
        self.auth = None
        self.db = None
        self.user = None
        self.id_token = None
        
        self._initialize_firebase()

    def _initialize_firebase(self):
        if not os.path.exists(self.config_path):
            print(f"[!] ERROR: {self.config_path} not found. Please create it first.")
            return
            
        with open(self.config_path, "r") as f:
            self.config = json.load(f)
            
        self.firebase = pyrebase.initialize_app(self.config)
        self.auth = self.firebase.auth()
        self.db = self.firebase.database()

    def authenticate_user(self):
        """
        Implements the 'Initial Web-Based Login with Refresh Tokens' flow.
        Returns the currently valid idToken.
        """
        if not self.auth:
            return None

        # 1. Check for Existing Refresh Token
        if os.path.exists(self.token_path):
            print("[*] Found existing user_token.json. Attempting to refresh session...")
            try:
                with open(self.token_path, "r") as f:
                    token_data = json.load(f)
                    refresh_token = token_data.get("refreshToken")
                    
                if refresh_token:
                    self.user = self.auth.refresh(refresh_token)
                    self.id_token = self.user['idToken']
                    
                    self._save_token({
                        "refreshToken": self.user['refreshToken'],
                        "localId": self.user.get('userId', self.user.get('localId')) 
                    })
                    print("[+] Firebase Session refreshed successfully.")
                    return self.id_token
                    
            except Exception as e:
                print(f"[-] Session refresh failed: {e}. Falling back to initial login.")
                try:
                    os.remove(self.token_path)
                except OSError:
                    pass

        # 2. Initial Google Sign-In (User-Guided)
        return self.perform_initial_google_login()

    def perform_initial_google_login(self):
        print("\n" + "="*50)
        print("          Ramanujan@Home - Authentication         ")
        print("="*50)
        print("1. Visit our Firebase Authentication portal via your web browser:")
        print("   https://ramanujan-engine.web.app (or your hosted Firebase page)")
        print("2. Sign in with your Google Account.")
        print("3. Copy the 'Firebase ID Token' displayed after login.")
        print("4. Paste that Token here to proceed.\n")
        
        # We need an id_token to exchange
        pasted_id_token = input("Paste your Firebase ID Token here: ").strip()
        
        if not pasted_id_token:
            print("[!] Authentication aborted.")
            return None
            
        try:
            print("[*] Exchanging ID Token for full Firebase Auth session...")
            # Use Pyrebase4 to authenticate. Usually custom tokens or direct web ID tokens 
            # might not have a dedicated pre-built function in pure Pyrebase, but we map 
            # to the identity toolkit directly.
            if hasattr(self.auth, 'sign_in_with_id_token'):
                self.user = self.auth.sign_in_with_id_token(pasted_id_token)
            else:
                url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithIdp?key={self.config['apiKey']}"
                payload = {
                    "postBody": f"id_token={pasted_id_token}&providerId=google.com",
                    "requestUri": "http://localhost",
                    "returnIdpCredential": True,
                    "returnSecureToken": True
                }
                res = requests.post(url, json=payload)
                if res.status_code == 200:
                    self.user = res.json()
                else:
                    # Fallback
                    self.user = self.auth.sign_in_with_custom_token(pasted_id_token)
            
            # Extract credentials depending on the wrapper variant used
            self.id_token = self.user.get('idToken', pasted_id_token)
            refresh_token = self.user.get('refreshToken')
            local_id = self.user.get('localId', self.user.get('userId'))

            if not refresh_token:
                print("[!] Error: No refresh token received from Identity Provider.")
                return None

            # 3. Save the refreshToken in user_token.json
            self._save_token({
                "refreshToken": refresh_token,
                "localId": local_id
            })
            
            print("[+] Authentication complete and token saved securely!")
            return self.id_token
            
        except Exception as e:
            print(f"[!] Authentication failed: {e}")
            return None

    def _save_token(self, token_data):
        with open(self.token_path, "w") as f:
            json.dump(token_data, f, indent=4)

    def request_work_unit(self):
        if not self.id_token:
            print("[!] ERROR: Not authenticated.")
            return None

        print("[*] Querying Firebase for pending work units...")
        try:
            # Query the Realtime Database for work_units where status is "pending"
            work_units_query = self.db.child("work_units").order_by_child("status").equal_to("pending").limit_to_first(5).get(self.id_token)
            
            if not work_units_query.val():
                print("[-] No pending work units available.")
                return None
                
            # Iterate through pending units to find one we can claim
            for unit in work_units_query.each():
                unit_id = unit.key()
                unit_data = unit.val()
                
                print(f"[*] Attempting to claim Work Unit: {unit_id}")
                
                user_uid = self.user.get('localId', self.user.get('userId'))
                
                # Update its status to "assigned", set assigned_to to Firebase UID
                update_data = {
                    "status": "assigned",
                    "assigned_to": user_uid,
                    "time_assigned": int(time.time())
                }
                
                # Attempt the atomic-like update using the idToken and precise Security Rules
                try:
                    self.db.child("work_units").child(unit_id).update(update_data, self.id_token)
                    print(f"[+] Successfully claimed Work Unit {unit_id}!")
                    
                    if "id" not in unit_data:
                        unit_data["id"] = unit_id
                        
                    return unit_data
                except Exception as update_err:
                    print(f"[-] Someone else claimed {unit_id} first or permission denied. Trying next...")
                    continue
                    
            print("[-] Flushed pending queue, but could not claim a unit.")
            return None
            
        except Exception as e:
            print(f"[!] Failed to fetch work units: {e}")
            return None

    def submit_results(self, work_unit_id, hits):
        if not self.id_token:
            return False
            
        print(f"[*] Submitting {len(hits)} verified results to Firebase...")
        user_uid = self.user.get('localId', self.user.get('userId'))
        
        try:
            for hit in hits:
                result_data = {
                    "lhs_key": str(hit.lhs_key),
                    "rhs_an_poly": str(hit.rhs_an_poly),
                    "rhs_bn_poly": str(hit.rhs_bn_poly),
                    "client_id": user_uid,
                    "timestamp": int(time.time())
                }
                
                # Push the atomic hit object, relying on security rules to lock it eternally 
                self.db.child("results").push(result_data, self.id_token)
            
            # Finalize the workload block as completed
            self.db.child("work_units").child(work_unit_id).update({
                "status": "completed"
            }, self.id_token)
            
            print(f"[+] Successfully submitted {len(hits)} results and marked Work Unit {work_unit_id} as completed.")
            return True
            
        except Exception as e:
            print(f"[!] Error submitting results: {e}")
            return False
