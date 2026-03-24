import time
import json
import sqlite3
from typing import List

from core.interfaces.base_problem import TargetProblem
from core.interfaces.base_strategy import BoundingStrategy
from core.interfaces.base_engine import ExecutionEngine
from core.interfaces.base_coordinator import NetworkCoordinator

class UniversalPipelineRouter:
    """
    The V4 decoupled universal routing pipeline.
    Arbitrarily shuttles workload dimensions between any combination of scientific
    targets, AI heuristics, GPU tensor arrays, and network states.
    
    Fully problem-agnostic: the problem type is derived from target.name and
    flows through the database layer automatically.
    """
    def __init__(self, 
                 target: TargetProblem, 
                 strategies: List[BoundingStrategy], 
                 engine: ExecutionEngine, 
                 network: NetworkCoordinator):
        self.target = target
        self.strategies = strategies
        self.engine = engine
        self.network = network

    def execute_work_unit(self, work_unit) -> List[dict]:
        print(f"\n==================================================")
        print(f"[*] Engine V4: Universal Pipeline Mode")
        print(f"[*] Problem: {self.target.name} [Precision: {self.target.precision}]")
        print(f"==================================================\n")
        
        a_bounds = work_unit.get('a_coef_range')
        b_bounds = work_unit.get('b_coef_range')
        
        # 1. Pipe boundaries through sequential AI/Mathematics reduction heuristics
        for strat in self.strategies:
            print(f"[*] Dispatching Phase-Space to strategy plugin: {strat.strategy_name}")
            a_bounds, b_bounds = strat.prune_bounds(a_bounds, b_bounds)
            print(f"    -> Dynamically refined a: {a_bounds}")
            print(f"    -> Dynamically refined b: {b_bounds}")
            
        # 2. Dispatch surviving bound constraints into Bare-Metal compute
        t0 = time.time()
        print(f"[*] Sinking tightly constrained subspace into Engine plugin: {self.engine.engine_id}")
        verified_discoveries = self.engine.batch_evaluate(a_bounds, b_bounds, self.target)
        gpu_seconds = time.time() - t0
        
        # Estimate combinations evaluated from bounds
        combinations = 1
        for bound in (a_bounds or []) + (b_bounds or []):
            combinations *= max(1, bound[1] - bound[0] + 1)
        
        print(f"\n[+] Pipeline execution finished. Verified formulas: {len(verified_discoveries)} "
              f"({combinations:,} combinations in {gpu_seconds:.2f}s)")
        return verified_discoveries, gpu_seconds, combinations
        
    def run_compute_loop(self, sqlite_path="v4_pending_discoveries.db"):
        problem_name = self.target.name
        print(f"[*] Universal Discovery Framework Initialized.")
        print(f"[*] Problem: {problem_name} | Entering distributed compute loop...\n")
        
        conn = sqlite3.connect(sqlite_path)
        c = conn.cursor()
        
        # Generic schema: works for any problem type
        c.execute('''CREATE TABLE IF NOT EXISTS pending_hits (
                        problem_type TEXT,
                        hit_key TEXT,
                        params_json TEXT,
                        node_id TEXT,
                        ts REAL)''')
        conn.commit()

        try:
            while True:
                # 1. Sync pending local discoveries to Firebase
                c.execute("SELECT rowid, * FROM pending_hits WHERE problem_type = ?", (problem_name,))
                pending_rows = c.fetchall()
                if pending_rows:
                    # Reconstruct dicts from the generic schema
                    hits_to_submit = []
                    for row in pending_rows:
                        hit = json.loads(row[3])  # params_json
                        hit['hit_key'] = row[2]   # hit_key
                        hits_to_submit.append(hit)
                    
                    if self.network.submit_results(hits_to_submit):
                        success_ids = [str(r[0]) for r in pending_rows]
                        c.execute(
                            f"DELETE FROM pending_hits WHERE rowid IN ({','.join('?'*len(success_ids))})",
                            success_ids)
                        conn.commit()
                        print(f"[*] Edge Storage Synced. Flushed {len(success_ids)} "
                              f"verified {problem_name} targets to global state.")
                
                # 2. Fetch Abstract Payload
                unit = self.network.fetch_work_unit()
                if not unit:
                    print("[-] Decentralized Work Queue exhausted. Delaying constraint polling 60s...")
                    time.sleep(60)
                    continue
                    
                # 3. Pipeline Execution Hook
                hits, gpu_seconds, combinations = self.execute_work_unit(unit)
                
                # 4. Report compute telemetry (best-effort, never blocks)
                if hasattr(self.network, 'report_telemetry'):
                    self.network.report_telemetry(combinations, gpu_seconds)
                
                # 5. Process discoveries
                if hits:
                    print(f"\n[!!!] CRITICAL: {len(hits)} VERIFIED HITS DISCOVERED!")
                    
                    # 5a. LLL/PSLQ Algebraic Identity Resolution
                    try:
                        from modules.continued_fractions.utils.lll_identity_resolver import (
                            resolve_identity, format_identity_report
                        )
                        print(f"[*] Running LLL/PSLQ integer relation detection on {len(hits)} hits...")
                        for ht in hits:
                            identity = resolve_identity(
                                float(str(ht.get('lhs_key', '0')).replace('_', '.')),
                                basis_constants={'gamma', 'pi', 'log2', 'zeta2', 'zeta3', '1'}
                            )
                            ht['identity'] = identity
                            report = format_identity_report(ht, identity)
                            print(report)
                    except Exception as e:
                        print(f"[!] LLL resolver unavailable ({e}), skipping identity resolution.")
                    
                    # 5b. Generic local SQLite backup
                    print(f"[*] Writing to permanent local SQLite backup...")
                    for ht in hits:
                        params = json.dumps({
                            k: v for k, v in ht.items()
                            if k not in ('identity',)
                        })
                        c.execute("INSERT INTO pending_hits VALUES (?, ?, ?, ?, ?)", 
                                  (problem_name,
                                   str(ht.get('lhs_key', ht.get('hit_key', ''))),
                                   params,
                                   self.network.client_id if hasattr(self.network, 'client_id') else "edge-node",
                                   time.time()))
                    conn.commit()
                print("\n[*] Ready for next computational block...\n")
                
        except KeyboardInterrupt:
            print("\n[!] Gracefully shutting down Universal Discovery Framework.")
            conn.close()
