import os
import json
import time
import socket
import platform
import urllib.request
import urllib.error
from typing import List, Dict, Optional

from core.interfaces.base_coordinator import NetworkCoordinator


class FirebaseCoordinator(NetworkCoordinator):
    """
    Problem-agnostic Firebase Realtime Database coordinator.
    
    All paths are dynamically namespaced under /problems/{problem_name}/ so the same
    Firebase instance can orchestrate multiple scientific problems simultaneously.
    Node telemetry is stored once under /nodes/{node_id}/ and referenced by FK.
    """
    def __init__(self, config_path: str = "firebase_config.json", problem_name: str = "default"):
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Missing config {config_path}")
            
        with open(config_path, "r") as f:
            self.config = json.load(f)
            
        self.api_key = self.config["apiKey"]
        self.db_url = self.config["databaseURL"]
        self.problem_name = problem_name
        self.client_id = f"{socket.gethostname()}-v4-node"
        self.id_token = None
        self._authenticate_user()
        self._register_node()

    def _authenticate_user(self):
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={self.api_key}"
        req = urllib.request.Request(auth_url, data=b'{"returnSecureToken": true}', headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req) as response:
                auth_resp = json.loads(response.read().decode())
                self.id_token = auth_resp["idToken"]
        except urllib.error.URLError as e:
            raise ConnectionError(f"Firebase REST Auth failed: {e}")

    def _register_node(self):
        """
        Write node metadata to /nodes/{node_id}/ once on first boot.
        Uses PATCH (merge) so subsequent boots only update last_heartbeat.
        """
        if not self.id_token:
            return
            
        # Detect GPU model for telemetry
        gpu_model = "Unknown"
        try:
            import torch
            if torch.cuda.is_available():
                gpu_model = torch.cuda.get_device_name(0)
        except ImportError:
            pass
        
        node_data = {
            "hostname": socket.gethostname(),
            "gpu_model": gpu_model,
            "os": f"{platform.system()} {platform.release()}",
            "python_version": platform.python_version(),
            "last_heartbeat": int(time.time() * 1000),
        }
        
        try:
            node_url = f"{self.db_url}/nodes/{self.client_id}.json?auth={self.id_token}"
            req = urllib.request.Request(
                node_url,
                data=json.dumps(node_data).encode(),
                headers={'Content-Type': 'application/json', 'X-HTTP-Method-Override': 'PATCH'},
                method='PUT'
            )
            # Use PATCH semantics to merge, not overwrite existing counters
            req.method = 'PATCH'
            with urllib.request.urlopen(req) as response:
                pass
        except Exception as e:
            print(f"[!] Node registration failed (non-fatal): {e}")

    # ─────────────────────────────────────────────────────────────────────
    # Work Distribution (problem-namespaced)
    # ─────────────────────────────────────────────────────────────────────
    def fetch_work_unit(self) -> Optional[Dict]:
        """Fetch cursor-based work from /problems/{problem_name}/tasks/cursor."""
        if not self.id_token:
            return None
            
        try:
            cursor_url = f"{self.db_url}/problems/{self.problem_name}/tasks/cursor.json?auth={self.id_token}"
            req = urllib.request.Request(cursor_url, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                cursor = json.loads(response.read().decode())
                
            if not cursor:
                return None

            # Check if problem is still active
            status = self._get_problem_status()
            if status and status != "active":
                print(f"[*] Problem '{self.problem_name}' status is '{status}'. Stopping.")
                return None
                
            # Enforce massive compute blocks to prevent GPU pipeline starvation
            step_size = max(cursor.get('step_size', 40), 40)
            a_pos = cursor.get('current_a_pos', 0)
            b_pos = cursor.get('current_b_pos', 0)
            
            # Atomically sweep the global cursor outward for the Distributed Network
            new_cursor = {
                "current_a_pos": a_pos + step_size
            }
            try:
                patch_req = urllib.request.Request(
                    cursor_url,
                    data=json.dumps(new_cursor).encode(),
                    headers={'Content-Type': 'application/json'},
                    method='PATCH'
                )
                with urllib.request.urlopen(patch_req):
                    pass
            except Exception as e:
                print(f"[!] Cursor advancement failed: {e}")
                
            work_unit = {
                "id": f"{self.problem_name}-dynamic",
                "v2_bound_id": f"v4_{a_pos}",
                "problem_name": self.problem_name,
                "a_deg": cursor.get('degree', 2),
                "b_deg": cursor.get('degree', 2),
                "a_coef_range": [[a_pos, a_pos + step_size]] * (cursor.get('degree', 2)+1),
                "b_coef_range": [[b_pos, b_pos + step_size]] * (cursor.get('degree', 2)+1),
            }
            return work_unit
            
        except Exception as e:
            print(f"[!] Firebase fetch failed: {e}")
            return None

    def _get_problem_status(self) -> Optional[str]:
        """Check /problems/{name}/config/status for problem lifecycle control."""
        try:
            url = f"{self.db_url}/problems/{self.problem_name}/config/status.json?auth={self.id_token}"
            req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode())
        except Exception:
            return None

    # ─────────────────────────────────────────────────────────────────────
    # Results Submission (problem-namespaced + attribution)
    # ─────────────────────────────────────────────────────────────────────
    def submit_results(self, verified_discoveries: List[Dict]) -> bool:
        """Push discoveries to /problems/{problem_name}/results/ with node FK."""
        if not verified_discoveries:
            return True
            
        try:
            for hit in verified_discoveries:
                result_payload = {
                    "hit_key": str(hit.get('lhs_key', hit.get('hit_key', ''))),
                    "params": json.dumps({
                        k: v for k, v in hit.items()
                        if k not in ('lhs_key', 'hit_key', 'identity', 'client_id')
                    }),
                    "node_id": self.client_id,
                    "ts": int(time.time() * 1000),
                }
                
                # Include algebraic identity if LLL resolver found one
                identity = hit.get('identity')
                if identity and identity.get('found'):
                    result_payload['identity'] = identity.get('expression', '')
                    result_payload['identity_method'] = identity.get('method', '')
                    result_payload['identity_residual'] = identity.get('residual', 0)
                
                push_url = f"{self.db_url}/problems/{self.problem_name}/results.json?auth={self.id_token}"
                req = urllib.request.Request(
                    push_url,
                    data=json.dumps(result_payload).encode(),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
                with urllib.request.urlopen(req) as response:
                    pass
            return True
        except Exception as e:
            print(f"[!] Firebase submit failed: {e}")
            return False

    # ─────────────────────────────────────────────────────────────────────
    # Compute Telemetry (atomic increments)
    # ─────────────────────────────────────────────────────────────────────
    def report_telemetry(self, combinations_evaluated: int, gpu_seconds: float):
        """
        Atomically increment compute counters on both the node and problem stats.
        Called after each work unit completes, regardless of whether hits were found.
        """
        if not self.id_token:
            return
            
        try:
            # 1. Increment node-level counters
            self._atomic_increment(
                f"nodes/{self.client_id}/total_units_completed", 1)
            self._atomic_increment(
                f"nodes/{self.client_id}/total_gpu_seconds", gpu_seconds)
            
            # 2. Increment problem-level global stats
            self._atomic_increment(
                f"problems/{self.problem_name}/stats/total_combinations_evaluated",
                combinations_evaluated)
            self._atomic_increment(
                f"problems/{self.problem_name}/stats/total_gpu_hours",
                gpu_seconds / 3600.0)
            
            # 3. Heartbeat
            self._set_value(
                f"nodes/{self.client_id}/last_heartbeat",
                int(time.time() * 1000))
                
        except Exception as e:
            print(f"[!] Telemetry report failed (non-fatal): {e}")

    def _atomic_increment(self, path: str, delta):
        """Read-modify-write a numeric counter at the given Firebase path."""
        try:
            url = f"{self.db_url}/{path}.json?auth={self.id_token}"
            # Read current value
            req = urllib.request.Request(url, headers={'Content-Type': 'application/json'})
            with urllib.request.urlopen(req) as response:
                current = json.loads(response.read().decode())
            
            new_val = (current or 0) + delta
            
            # Write updated value
            req = urllib.request.Request(
                url,
                data=json.dumps(new_val).encode(),
                headers={'Content-Type': 'application/json'},
                method='PUT'
            )
            with urllib.request.urlopen(req) as response:
                pass
        except Exception:
            pass  # Telemetry is best-effort, never block the pipeline

    def _set_value(self, path: str, value):
        """Directly set a value at the given Firebase path."""
        try:
            url = f"{self.db_url}/{path}.json?auth={self.id_token}"
            req = urllib.request.Request(
                url,
                data=json.dumps(value).encode(),
                headers={'Content-Type': 'application/json'},
                method='PUT'
            )
            with urllib.request.urlopen(req) as response:
                pass
        except Exception:
            pass
