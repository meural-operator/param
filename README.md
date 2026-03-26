# Ramanujan@Home: Universal Distributed Scientific Computing Framework

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![PyTorch CUDA](https://img.shields.io/badge/PyTorch-CUDA_Ready-EE4C2C.svg)](https://pytorch.org/)
[![Distributed Compute](https://img.shields.io/badge/Computing-Distributed_Edge-yellow.svg)](https://firebase.google.com/)
[![Tests](https://img.shields.io/badge/Tests-22%2F22_Passing-brightgreen.svg)](#-testing)
[![AlphaEvolve](https://img.shields.io/badge/AlphaEvolve-LLM_Guided-blueviolet.svg)](#-alphaevolve--llm-guided-evolutionary-search)

A globally distributed, GPU-accelerated computing framework that orchestrates **Deep Reinforcement Learning**, **LLM-Guided Evolutionary Search**, and **High-Performance Tensor Operations** to solve complex scientific problems at scale. Originally founded for **mathematical constant discovery** via Generalized Continued Fractions (GCFs), **Ramanujan@Home** has evolved into a universal engine capable of orchestrating any pluggable scientific domain.

---

## Table of Contents

- [Core Features](#-core-features)
- [Requirements](#-requirements)
- [Quickstart](#-quickstart)
- [Architecture & Hierarchy](#%EF%B8%8F-architecture--hierarchy)
- [AlphaEvolve — LLM-Guided Evolutionary Search](#-alphaevolve--llm-guided-evolutionary-search)
- [Available Modules](#%EF%B8%8F-available-modules)
- [RL Agent & Training](#-rl-agent--training)
- [Full Setup Guide](#-full-setup-guide)
- [Directory Structure](#-directory-structure)
- [Database Architecture](#%EF%B8%8F-database-architecture)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [Citation](#-citation)
- [Acknowledgements](#-acknowledgements)
- [License](#-license)

---

## 🌟 Core Features

| Feature | Description |
| --- | --- |
| **Universal Pipeline Router** | An abstract execution engine (`core/pipeline.py`) that decouples problem definition, search strategy, compute engine, and network coordination into interchangeable plugins. |
| **AlphaEvolve (LLM-Guided Search)** | A DeepMind-inspired evolutionary engine that uses a local LLM (Qwen3-Coder-30B via LM Studio) to evolve Python lambda programs for `a(n)` / `b(n)` GCF sequences — discovering novel mathematical structures beyond fixed-degree polynomials. |
| **Deep RL Search Optimization** | AlphaTensor MCTS heuristics intelligently prune coordinate spaces to focus GPU compute on high-probability regions. |
| **LLL/PSLQ Identity Resolver** | Automatic algebraic identity detection — transforms numerical matches into proven closed-form expressions using lattice basis reduction. |
| **Modular Problem System** | Scientific problems are self-contained modules. Expanding the framework to new domains requires no changes to core infrastructure. |
| **Distributed Orchestration** | Dynamically namespaced Firebase synchronization — multiple independent scientific problems run on a single global cluster simultaneously. |
| **Compute Telemetry** | Real-time tracking of GPU hours, combinations evaluated, and contributor attribution across the entire network. |
| **Resilient Edge Caching** | Local `sqlite3` buffering ensures verified discoveries and compute progress survive hardware or network disruptions. |
| **Plug-and-Play Deployment** | Automated bootstrapping handles environment isolation, dependencies, and cloud authentication for immediate volunteer participation. |
| **Pre-Trained AI Agents** | Optimized AlphaTensor MCTS weights (`em_mcts.pt`) included — achieving 400+ reward on Euler-Mascheroni convergence targets for immediate high-performance search out of the box. |

---

## 📋 Requirements

### Hardware

- **GPU (recommended):** NVIDIA GPU with CUDA support (tested on RTX 4000 Ada, 20GB VRAM)
- **CPU-only mode:** Supported via `ProcessPoolExecutor` fallback, but significantly slower
- **RAM:** 8 GB minimum, 16 GB recommended for large polynomial degree sweeps
- **Storage:** ~500 MB for dependencies + model weights
- **LM Studio (optional):** For AlphaEvolve LLM-guided search — any GGUF model ≥ 8B parameters

### Software

- **Python:** 3.13+
- **PyTorch:** 2.10+ with CUDA 13.0 (or CPU-only)
- **mpmath:** For arbitrary-precision verification (1000+ digit comparisons)
- **sympy:** Symbolic mathematics (constants dictionary, Möbius transforms)
- **gymnasium:** RL environments for MCTS agent training
- **scikit-learn:** Feature engineering for AI modules
- **Firebase Admin / Pyrebase:** For distributed coordination
- **TensorBoard:** For training visualization (optional, for `research_training/`)

> All dependencies are managed via `environment.yml` (Conda), `requirements.txt` / `requirements-cuda.txt` (pip), or auto-installed by `clients/setup/autoinstaller.py`.

---

## ⚡ Quickstart

### Option A: Conda (Recommended for researchers)

```bash
git clone https://github.com/meural-operator/Ramanujan-Home.git
cd Ramanujan-Home

# Creates 'curiosity' env with Python 3.13, PyTorch CUDA, and all deps
conda env create -f environment.yml
conda activate curiosity

# Run the AlphaEvolve evolutionary miner (uses LM Studio if available)
python scripts/evolve_miner.py --target pi --generations 100
```

### Option B: pip (CPU or GPU)

```bash
# CPU only
pip install -r requirements.txt

# NVIDIA GPU (CUDA 13.0)
pip install -r requirements-cuda.txt
```

### Option C: 1-Click Deployment (Windows volunteers)

```bash
.\run_node.bat
```

> The batch script automatically installs Python 3.13 via Micromamba, bootstraps all dependencies, generates Firebase credentials, seeds the LHS verification tables, and launches the GPU compute node.

### Option D: Smart Auto-Installer

```bash
python clients/setup/autoinstaller.py
```

> Auto-detects conda vs pip, NVIDIA GPU vs CPU, and installs the correct configuration.

For the full setup guide, see [`INSTALL.md`](INSTALL.md).

---

## 🏗️ Architecture & Hierarchy

The framework enforces a strict separation between **core infrastructure** and **scientific modules**. The `UniversalPipelineRouter` orchestrates plugin life-cycles without domain-specific knowledge.

![Universal Platform Architecture](assets/architecture.png)

### Abstract Interfaces (`core/interfaces/`)

| Interface | File | Purpose |
| --- | --- | --- |
| `TargetProblem` | `base_problem.py` | Defines the mathematical/scientific problem — constants, verification logic, LHS hash generation |
| `BoundingStrategy` | `base_strategy.py` | Search space optimization — AI pruning, heuristics, or brute-force passthrough |
| `ExecutionEngine` | `base_engine.py` | Hardware-accelerated compute — CUDA tensors, CPU multiprocessing, TPU, etc. |
| `NetworkCoordinator` | `base_coordinator.py` | Distributed coordination — work unit fetching, result submission, authentication |

### Adding a New Scientific Module

To add a new problem domain (e.g. `protein_folding`):

```python
# modules/protein_folding/target.py
from core.interfaces.base_problem import TargetProblem

class ProteinFoldingTarget(TargetProblem):
    @property
    def name(self): return "protein-folding"

    def verify_match(self, a_coef, b_coef):
        # Your domain-specific verification
        ...
```

No changes to `core/` are required. The pipeline automatically routes through your new plugin.

---

## 🗃️ Available Modules

| Module | Directory | Status | Description |
| --- | --- | --- | --- |
| **Continued Fractions** | `modules/continued_fractions/` | ✅ Active | GPU-accelerated discovery of novel GCF formulas for mathematical constants (γ, ζ(3), ζ(5), ζ(7), Catalan, Khinchin, etc.) |
| **AlphaEvolve Engine** | `modules/.../math_ai/agents/` | ✅ Active | LLM-guided evolutionary search for novel GCF programs using Qwen3-Coder-30B |
| **RL Training Suite** | `research_training/` | ✅ Active | Curriculum PPO training for the AlphaTensor MCTS neural bounds pruner |

### Supported Mathematical Constants

The continued fractions module ships with a built-in constants dictionary (`modules/continued_fractions/constants.py`) supporting:

| Constant | Symbol | Description |
| --- | --- | --- |
| Euler-Mascheroni | γ ≈ 0.5772 | Primary search target with dedicated RL environment |
| Riemann Zeta | ζ(3), ζ(5), ζ(7) | Apéry-style and multi-dimensional GCF domains |
| Catalan | G ≈ 0.9159 | Dedicated domain with large-scale test coverage |
| Pi | π, π² | Classical constant with Möbius transform lookups |
| Euler's Number | e | Exponential constant |
| Golden Ratio | φ ≈ 1.6180 | Algebraic constant |
| ln(2) | ln 2 | Natural logarithm of 2 |
| √2 | √2 | Square root of 2 |
| Khinchin | K ≈ 2.6854 | Geometric mean of CF partial quotients |
| Polygamma | ψ⁽ⁿ⁾ | Higher derivatives of the digamma function |

*Future modules can be added by implementing the 4 core interfaces — see [Architecture](#%EF%B8%8F-architecture--hierarchy) section above.*

---

## 🧬 AlphaEvolve — LLM-Guided Evolutionary Search

Inspired by DeepMind's AlphaEvolve, this module uses a local LLM to **evolve Python programs** that generate GCF sequences converging to mathematical constants. Instead of searching over fixed-degree polynomial coefficients, it searches over the space of _all computable functions_.

### How It Works

1. **Population:** Maintains a pool of candidate programs, each defined by two Python lambda expressions `a(n)` and `b(n)`
2. **Fitness:** Each program is evaluated by computing its GCF convergent over 200 terms and measuring how many digits match the target constant
3. **Selection:** Tournament selection picks high-fitness parents
4. **LLM Mutation:** The local LLM (Qwen3-Coder-30B) proposes mathematically-motivated mutations — modifying polynomial degrees, introducing alternating signs, factorials, or product forms
5. **LLM Crossover:** The LLM intelligently combines elements from two high-fitness parents
6. **Archive:** Programs exceeding 5+ digits of accuracy are archived to SQLite for analysis

### Architecture

| Component | File | Purpose |
| --- | --- | --- |
| **LM Studio Client** | `math_ai/llm/llm_client.py` | OpenAI-compatible API client for local LLM inference |
| **Program Sandbox** | `math_ai/agents/program_sandbox.py` | Safe eval environment with whitelisted ops, timeout, NaN/Inf rejection |
| **Evolution Engine** | `math_ai/agents/alpha_evolve_engine.py` | Population management, tournament selection, generation loop |
| **Pipeline Plugin** | `math_ai/strategies/alpha_evolve_strategy.py` | `BoundingStrategy` implementation for the `UniversalPipelineRouter` |
| **Standalone Miner** | `scripts/evolve_miner.py` | CLI runner for long-running evolutionary discovery |

### Running AlphaEvolve

```bash
# 1. Start LM Studio and load Qwen3-Coder-30B (or any model)
# 2. Run the evolutionary miner:
python scripts/evolve_miner.py --target catalan --generations 500 --population 30

# Available targets: pi, e, catalan, gamma, golden_ratio, ln2, sqrt2, zeta3
```

> **No LM Studio?** The miner falls back to random mutations automatically — LLM just makes the search dramatically smarter.

### Resource Management

- **GPU:** Reserved for LM Studio (LLM inference). Fitness evaluation runs on **CPU** via GCF recurrence.
- **VRAM:** ~16 GB for Qwen3-Coder-30B Q4 quantization.
- **Discoveries:** Archived to `evolve_<target>.db` SQLite databases.

---

## 🧠 RL Agent & Training

The framework includes a complete **Deep Reinforcement Learning** pipeline for intelligent search space pruning. Instead of brute-force exhaustion of polynomial coefficient spaces, the RL agent learns to propose tight coordinate boundaries that maximize the probability of discovering novel GCF representations.

### Architecture

- **Policy Network:** Actor-Critic with residual blocks, LayerNorm, and orthogonal initialization (`modules/continued_fractions/math_ai/models/actor_critic.py`)
- **Search Agent:** AlphaTensor-inspired MCTS with UCB-PUCT selection, Dirichlet noise injection, and global min-max Q normalization (`modules/continued_fractions/math_ai/agents/alpha_tensor_mcts.py`)
- **Training Algorithm:** Proximal Policy Optimization (PPO) with Generalized Advantage Estimation (GAE), cosine LR scheduling, and entropy annealing

### Training Configuration

Key hyperparameters from `research_training/config.yaml`:

| Parameter | Value | Description |
| --- | --- | --- |
| Target Episodes | 1,500,000 | Long-horizon curriculum training |
| MCTS Simulations | 200 per step | Tree traversals before each environment action |
| Network Hidden Dim | 256 | Actor-Critic hidden layer width |
| PPO Clip | 0.2 | Policy ratio clipping bound |
| Curriculum Start | 20 steps | Initial GCF sequence depth |
| Curriculum Limit | 150 steps | Maximum GCF sequence depth |
| Promotion Threshold | 35.0 reward | Required mean reward to advance curriculum level |

### Pre-Trained Weights

The repository ships with a trained checkpoint at `clients/checkpoints/em_mcts.pt` that achieved **400+ cumulative reward** on the Euler-Mascheroni convergence environment. Edge nodes automatically load this checkpoint for immediate high-performance search without requiring local training.

### Training From Scratch

```bash
cd research_training
python train.py --episodes 50000 --max-depth 200

# Monitor training metrics
tensorboard --logdir runs/
```

---

## 🔧 Full Setup Guide

See [`INSTALL.md`](INSTALL.md) for detailed instructions. Summary below.

### Conda (Recommended)

```bash
git clone https://github.com/meural-operator/Ramanujan-Home.git
cd Ramanujan-Home
conda env create -f environment.yml
conda activate curiosity
```

> The `environment.yml` creates a `curiosity` environment with Python 3.13, PyTorch CUDA 13.0, and all 20+ dependencies.
>
> For older GPUs (RTX 30 series), edit `environment.yml` and change `cu130` → `cu124`.

### pip (Alternative)

```bash
# CPU only
pip install -r requirements.txt

# NVIDIA GPU (CUDA 13.0)
pip install -r requirements-cuda.txt
```

### Smart Auto-Installer

```bash
python clients/setup/autoinstaller.py
```

> Detects your system (GPU/CPU, conda/pip) and installs the correct configuration automatically.

### AlphaEvolve Setup

To use LLM-guided evolution, install [LM Studio](https://lmstudio.ai), load a model (recommended: `Qwen3-Coder-30B`), and start the local server at `localhost:1234`. The miner auto-detects LM Studio availability.

### 1-Click Deployment (Windows Volunteers)

```bash
.\run_node.bat
```

> Handles Python isolation (Micromamba), dependency installation, Firebase credential generation, LHS table seeding, and GPU node launch — all automatically.

---

## 📁 Directory Structure

> ✅ = Currently implemented &nbsp;&nbsp; 🔮 = Planned / Future extension

```text
Ramanujan-Home/
│
├── core/                                        # ✅ Universal Framework (problem-agnostic)
│   ├── __init__.py
│   ├── pipeline.py                              #    UniversalPipelineRouter — Core orchestrator
│   ├── interfaces/                              #    Abstract Base Classes
│   │   ├── base_problem.py                      #    TargetProblem — defines what to solve
│   │   ├── base_strategy.py                     #    BoundingStrategy — search optimization
│   │   ├── base_engine.py                       #    ExecutionEngine — compute backend
│   │   └── base_coordinator.py                  #    NetworkCoordinator — distributed I/O
│   └── coordinators/                            #    Network implementations
│       └── firebase_coordinator.py              #    Firebase REST coordination
│
├── modules/                                     # ✅ Scientific Problem Modules
│   └── continued_fractions/                     # ✅ Generalized Continued Fraction Discovery
│       ├── constants.py                         #    Mathematical constants dictionary
│       ├── LHSHashTable.py                      #    Precomputed Möbius transform lookup
│       ├── CachedSeries.py                      #    Cached polynomial series evaluator
│       ├── multiprocess_enumeration.py          #    CPU multiprocess coordinator
│       │
│       ├── targets/                             #    Target constant plugins
│       │   └── euler_mascheroni.py              #    ✅ Euler-Mascheroni (γ = 0.5772...)
│       │
│       ├── engines/                             #    Compute backends
│       │   ├── AbstractGCFEnumerator.py
│       │   ├── EfficientGCFEnumerator.py
│       │   ├── GPUEfficientGCFEnumerator.py
│       │   ├── FREnumerator.py
│       │   ├── ParallelGCFEnumerator.py
│       │   ├── RelativeGCFEnumerator.py
│       │   └── cuda_gcf.py                      #    ✅ CUDAEnumerator adapter wrapper
│       │
│       ├── domains/                             #    Search space generators
│       │   ├── AbstractPolyDomains.py
│       │   ├── CartesianProductPolyDomain.py
│       │   ├── ExplicitCartesianProductPolyDomain.py
│       │   ├── MCTSPolyDomain.py
│       │   ├── NeuralMCTSPolyDomain.py
│       │   ├── ContinuousRelaxationDomain.py
│       │   ├── CatalanDomain.py
│       │   ├── Zeta3Domain1.py
│       │   ├── Zeta3Domain2.py
│       │   ├── Zeta3DomainWithRatC.py
│       │   ├── Zeta5Domain.py
│       │   ├── Zeta7Domain.py
│       │   └── ExamplePolyDomain.py
│       │
│       ├── math_ai/                             #    AI & Symbolic Heuristics
│       │   ├── symbolic_regression.py
│       │   ├── models/
│       │   │   └── actor_critic.py
│       │   ├── agents/
│       │   │   ├── alpha_tensor_mcts.py          #    ✅ MCTS search agent
│       │   │   ├── alpha_evolve_engine.py        #    ✅ LLM evolutionary engine
│       │   │   └── program_sandbox.py            #    ✅ Safe eval sandbox
│       │   ├── llm/                              #    ✅ LLM Integration
│       │   │   ├── __init__.py
│       │   │   └── llm_client.py                 #    LM Studio API client
│       │   ├── environments/
│       │   │   ├── AbstractRLEnvironment.py
│       │   │   ├── EulerMascheroniEnvironment.py
│       │   │   └── GCFRewardEnvironment.py
│       │   ├── training/
│       │   │   ├── ppo_trainer.py
│       │   │   ├── replay_buffer.py
│       │   │   └── checkpoint.py
│       │   └── strategies/
│       │       ├── mcts_strategy.py               #    ✅ Neural MCTS plugin
│       │       └── alpha_evolve_strategy.py       #    ✅ AlphaEvolve plugin
│       │
│       └── utils/                               #    Mathematical Utilities
│           ├── asymptotic_filter.py             #    ✅ Worpitzky convergence filter
│           ├── lll_identity_resolver.py         #    ✅ LLL/PSLQ identity resolver
│           ├── convergence_rate.py
│           ├── mobius.py
│           ├── latex.py
│           └── utils.py
│
├── clients/                                     # ✅ Distributed Edge Clients
│   ├── edge_node.py                             #    Client entrypoint
│   ├── run_node.bat                             #    1-click Windows deployer
│   ├── firebase_config.json
│   ├── checkpoints/                             #    Neural weight artifacts
│   │   └── em_mcts.pt                           #    ✅ Pre-trained MCTS weights (400+ reward)
│   └── setup/
│       ├── autoinstaller.py
│       ├── global_seeder.py
│       └── genesis_wipe.py
│
├── research_training/                           # ✅ Neural Training Pipeline
│   ├── train.py
│   ├── config.yaml                              #    Hyperparameter configuration
│   ├── env_curriculum.py
│   ├── eval_mcts.py
│   └── runs/                                    #    TensorBoard logs
│
├── scripts/                                     # ✅ Utility & Research Tools
│   ├── evolve_miner.py                          #    ✅ AlphaEvolve standalone runner
│   ├── publishable_discoveries_miner.py         #    ✅ Local publishable discovery miner
│   ├── seed_euler_mascheroni_db.py
│   ├── train_rl_em.py
│   ├── euler_mascheroni_ai_search.py
│   ├── euler_mascheroni_research_grade.py
│   ├── reset_v2_cursor.py
│   ├── seed_firebase_work.py
│   ├── multiprocessing_example.py
│   ├── zeta3_fr_results.py
│   ├── zeta3_infinite_family.py
│   ├── boinc/
│   │   ├── execute_from_json.py
│   │   └── split_execution.py
│   └── paper_results/
│
├── tests/                                       # ✅ Verification Suite (22/22 passing)
│   ├── test_interfaces.py
│   ├── test_universal_pipeline.py
│   ├── test_lll_resolver.py
│   ├── test_ai_modules.py
│   ├── test_asymptotic_filter.py
│   ├── test_gpu_enumerators.py
│   ├── test_fr_expansion.py
│   ├── test_poly_domains.py
│   ├── test_large_catalan.py
│   ├── test_alphaevolve_sandbox.py               #    ✅ Sandbox safety, fitness evaluation
│   ├── test_alphaevolve_llm.py                   #    ✅ LLM client mocks, response parsing
│   ├── conjectures_tests.py
│   └── boinc_scripts_tests.py
│
├── README.md
├── INSTALL.md                                    # ✅ Detailed installation guide
├── CHANGELOG.md
├── environment.yml                               # ✅ Conda environment specification
├── requirements.txt                              # ✅ pip deps (CPU PyTorch)
├── requirements-cuda.txt                         # ✅ pip deps (CUDA PyTorch)
└── setup.py
```

---

## 🗄️ Database Architecture

The Firebase Realtime Database is **problem-namespaced** — multiple scientific problems run on the same cluster simultaneously without schema changes.

```text
Ramanujan-Home/
│
├── nodes/                              ← ONE entry per volunteer (no duplication)
│   └── {node_id}/
│       ├── hostname: "DIAT-Lab-01"
│       ├── gpu_model: "RTX 4000 Ada"
│       ├── os: "Windows 11"
│       ├── python_version: "3.13.0"
│       ├── last_heartbeat: 1711234999000
│       ├── total_units_completed: 4217
│       └── total_gpu_seconds: 89432.5
│
├── problems/                           ← Auto-namespaced per problem type
│   └── {problem_name}/                 (e.g., "euler-mascheroni")
│       ├── config/
│       │   └── status: "active"        ("active" | "solved" | "paused")
│       │
│       ├── tasks/
│       │   └── cursor/                 ← Atomic work assignment state
│       │       ├── current_a_pos
│       │       ├── current_b_pos
│       │       └── degree
│       │
│       ├── results/                    ← Verified discoveries
│       │   └── {push_id}/
│       │       ├── hit_key
│       │       ├── params              (JSON blob — problem-agnostic)
│       │       ├── identity            (closed-form if LLL found one)
│       │       ├── identity_method     ("pslq_basis" | "mpmath_identify")
│       │       ├── identity_residual
│       │       ├── node_id             ← FK to /nodes/ (no duplication)
│       │       └── ts
│       │
│       └── stats/                      ← Aggregated compute telemetry
│           ├── total_combinations_evaluated
│           └── total_gpu_hours
```

### Design Principles

| Principle | Implementation |
| --- | --- |
| **Zero Redundancy** | Node metadata (GPU, hostname, OS) stored once in `/nodes/`. Results reference by `node_id` FK. |
| **Atomic Counters** | Compute telemetry uses read-modify-write increments, never per-result duplication. |
| **Problem Isolation** | Each problem type gets isolated `/tasks/`, `/results/`, `/stats/` — no cross-contamination. |
| **Discovery Attribution** | Every result links to the contributing node. Query "who solved it" is trivial. |
| **Lifecycle Control** | Set `/problems/{name}/config/status` to `"solved"` and all edge nodes gracefully stop. |

### Local SQLite Backup

The edge node maintains a local cache with a generic schema that works for any problem:

```sql
CREATE TABLE pending_hits (
    problem_type TEXT,    -- e.g., "euler-mascheroni"
    hit_key      TEXT,    -- constant-specific hash key
    params_json  TEXT,    -- JSON blob of all hit parameters
    node_id      TEXT,    -- this node's identifier
    ts           REAL     -- Unix timestamp
);
```

---

## 🧪 Testing

The project maintains a comprehensive test suite covering core abstractions, GPU parity, AI modules, and mathematical correctness:

```bash
conda run -n curiosity python -m unittest discover -s tests -v
```

| Test Module | Coverage Area |
| --- | --- |
| `test_interfaces.py` | Core ABC contract enforcement |
| `test_universal_pipeline.py` | Pipeline integration with generic schema |
| `test_lll_resolver.py` | LLL/PSLQ identity resolution (6 cases) |
| `test_ai_modules.py` | Actor-Critic forward pass, dimension checks |
| `test_asymptotic_filter.py` | Worpitzky convergence filtering |
| `test_gpu_enumerators.py` | GPU vs CPU numerical parity |
| `test_fr_expansion.py` | Multi-dimensional PSLQ expansion |
| `test_poly_domains.py` | Domain generator correctness |
| `test_large_catalan.py` | Large-degree Catalan constant search |
| `test_alphaevolve_sandbox.py` | Program sandbox safety, GCF fitness evaluation, timeout protection |
| `test_alphaevolve_llm.py` | LLM client mock tests, lambda response parsing, random mutation fallback |
| `conjectures_tests.py` | Known conjecture validation |
| `boinc_scripts_tests.py` | BOINC distributed integration |

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-new-module`
3. Implement your scientific module under `modules/your_module/`
4. Add tests under `tests/`
5. Submit a Pull Request

For new problem domains, implement the 4 interfaces in `core/interfaces/` and register your module. The framework handles everything else — database namespacing, telemetry, and edge caching are fully automatic.

---

## 📖 Citation

If you use this framework in your research, please cite:

```bibtex
@software{ramanujan_at_home,
  title   = {Ramanujan@Home: Universal Distributed Scientific Computing Framework},
  author  = {Ashish Musale},
  year    = {2026},
  url     = {https://github.com/meural-operator/Ramanujan-Home},
  note    = {GPU-accelerated distributed framework for mathematical constant
             discovery via Deep RL and Generalized Continued Fractions}
}
```

---

## 🙏 Acknowledgements

- **The Ramanujan Machine Project** ([Technion](https://www.ramanujanmachine.com/)) — foundational research on automated conjecture generation via continued fractions that inspired this framework's mathematical core.
- **DeepMind's AlphaTensor & AlphaEvolve** — architectural inspiration for the MCTS-guided neural search agent and the LLM-guided evolutionary program search.
- **LM Studio** — local LLM inference platform powering the AlphaEvolve evolutionary search module.
- **DIAT (Defence Institute of Advanced Technology)** — computational resources and research environment.

---

## 📄 License

This project is licensed under the MIT License.
