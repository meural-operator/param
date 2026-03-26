import sys
import os
import time

# Ensure the framework root resolves safely 
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if repo_root not in sys.path:
    sys.path.insert(0, repo_root)

from modules.continued_fractions.targets.publishable_targets import PiTarget, ETarget, CatalanTarget
from modules.continued_fractions.engines.GPUEfficientGCFEnumerator import GPUEfficientGCFEnumerator
from modules.continued_fractions.domains.NeuralMCTSPolyDomain import NeuralMCTSPolyDomain

def execute_discovery_run(target_instance, a_degree=3, b_degree=3, bound_radius=15, mcts_sims=500):
    print("\n" + "=" * 70)
    print(f"   TARGET LOCK: Searching for [{target_instance.name.upper()}] Discoveries")
    print("=" * 70)
    
    # 1. Fetch or Auto-Generate the LHS Hash Table
    print(f"[1/4] Retrieving or building Mobius transform Hash Table...")
    # Dynamic depth constraint to preserve RAM. Depth=20 guarantees millions of hits, 
    # but generates fast.
    lhs = target_instance.generate_lhs_hash_table(depth=20)
    print(f"       LHS table ready.")
    
    # 2. Setup the Deep Reinforcement Learning Native Bound Evaluator
    print("[2/4] Running Deep Reinforcement Learning (Neural MCTS) to bound search scope...")
    poly_search_domain = NeuralMCTSPolyDomain(
        a_deg=a_degree, a_coef_range=[-bound_radius, bound_radius],
        b_deg=b_degree, b_coef_range=[-bound_radius, bound_radius],
        target_val=target_instance._val,
        mcts_simulations=mcts_sims  
    )
    
    print(f"       AI-Optimized a_n structural bounds: {poly_search_domain.a_coef_range}")
    print(f"       AI-Optimized b_n structural bounds: {poly_search_domain.b_coef_range}")
    
    an_count = poly_search_domain.get_an_length()
    bn_count = poly_search_domain.get_bn_length()
    total_evals = an_count * bn_count
    print(f"       Refined Tensor Iteration Space: {an_count:,} × {bn_count:,} = {total_evals:,} GPU targeted GCF evaluations")
    
    # 3. Deploy GPU enumerator
    print("\n[3/4] Initializing GPU-accelerated GCF enumerator...")
    enumerator = GPUEfficientGCFEnumerator(
        lhs,
        poly_search_domain,
        [target_instance._val]
    )

    # 4. Execute full search
    print(f"[4/4] Executing full enumeration. Monitor GPU usage with nvidia-smi.")
    start_time = time.time()
    results = enumerator.full_execution()
    elapsed = time.time() - start_time
    
    # 5. Output Summary
    print("\n" + "-" * 50)
    print(f"   RESULTS FOR {target_instance.name.upper()}")
    print("-" * 50)
    if len(results) == 0:
        print("  No conjectures found within current search bounds.")
    else:
        print(f"  Found {len(results)} conjecture(s)!")
        enumerator.print_results(results)
    
    hours, remainder = divmod(elapsed, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"  Target runtime: {int(hours)}h {int(minutes)}m {seconds:.1f}s\n")
    return results

def main():
    print("=========================================================================")
    print("   Ramanujan@Home: Local Continuous Discovery Miner (High-Throughput)    ")
    print("=========================================================================\n")
    print(" This script bypasses the distributed Firebase network to perform")
    print(" consecutive, immediate brute-force search blocks on known constants.")
    print(" It leverages 100% of your local GPU's tensor-core boundaries.")
    
    # Configure the generic mathematically publishable targets
    targets = [
        CatalanTarget(),
        ETarget(),
        PiTarget()
    ]
    
    # Let the miner cycle through them endlessly or sequentially
    total_start = time.time()
    all_discoveries = 0
    
    for target in targets:
        # We use a smaller bounds search (d=2, R=25 or d=3, R=15) so it completes in hours instead of weeks
        # You can scale this up arbitrarily based on hardware.
        found = execute_discovery_run(
            target_instance=target, 
            a_degree=2, 
            b_degree=2, 
            bound_radius=25, 
            mcts_sims=500
        )
        all_discoveries += len(found)
        
    total_elapsed = time.time() - total_start
    h, r = divmod(total_elapsed, 3600)
    m, s = divmod(r, 60)
    
    print("=========================================================================")
    print("                            MINER COMPLETE")
    print("=========================================================================")
    print(f" Total Global Found : {all_discoveries} mathematical formulas")
    print(f" Total Global Time  : {int(h)}h {int(m)}m {s:.1f}s")
    print("=========================================================================")

if __name__ == '__main__':
    main()
