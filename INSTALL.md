# Installation Guide

## Quick Start (Recommended — Conda)

```bash
# 1. Clone the repository
git clone https://github.com/meural-operator/Ramanujan-Home.git
cd Ramanujan-Home

# 2. Create the environment (auto-installs Python 3.13, PyTorch CUDA, and all deps)
conda env create -f environment.yml

# 3. Activate
conda activate curiosity

# 4. Run a discovery miner
python scripts/evolve_miner.py --target pi --generations 100
```

> **GPU Note:** The `environment.yml` defaults to **PyTorch with CUDA 13.0** (RTX 40/50/Ada series).
> For older GPUs (e.g., RTX 30 series), edit `environment.yml` and change `cu130` → `cu124`.
> For CPU-only, see the pip instructions below.

---

## Alternative: pip + venv

### CPU Only
```bash
pip install -r requirements.txt
```

### NVIDIA GPU (CUDA)
```bash
pip install -r requirements-cuda.txt
```

---

## Automatic Installer

The smart auto-installer detects your system (GPU/CPU, conda/pip) and installs accordingly:

```bash
python clients/setup/autoinstaller.py
```

This will:
- Detect whether you have an NVIDIA GPU via `nvidia-smi`
- Prefer conda if available, otherwise fall back to pip + venv
- Install the correct PyTorch build (CUDA or CPU)
- Install all mathematical, ML, and networking dependencies

---

## Dependencies Overview

| Category | Packages |
|---|---|
| **Core Math** | `mpmath`, `numpy`, `scipy`, `sympy` |
| **ML / RL** | `torch`, `torchvision`, `scikit-learn`, `gymnasium`, `tensorboard` |
| **Symbolic Regression** | `pysr` |
| **Distributed** | `requests`, `pyrebase4`, `firebase-admin`, `google-cloud-firestore` |
| **Optimization** | `ortools`, `pybloom_live` |
| **Utilities** | `tqdm`, `pyyaml`, `semver` |

---

## AlphaEvolve (LLM-Guided Search)

To use the LLM-guided evolutionary search, you also need:

1. **LM Studio** — Download from [lmstudio.ai](https://lmstudio.ai)
2. Load a model (recommended: `Qwen3-Coder-30B`)
3. Start the local server (default: `http://localhost:1234`)
4. Run the evolutionary miner:
   ```bash
   python scripts/evolve_miner.py --target catalan --generations 500
   ```

> The miner works **without** LM Studio too — it falls back to random mutations.
> LM Studio just makes the search dramatically smarter.
