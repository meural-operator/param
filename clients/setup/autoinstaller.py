import os
import sys
import subprocess
import shutil

def is_windows():
    return sys.platform == "win32"

def has_nvidia_gpu():
    """Detect NVIDIA GPU via nvidia-smi."""
    try:
        result = subprocess.run(
            ["nvidia-smi"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def has_conda():
    """Check if conda is available in the system PATH."""
    try:
        result = subprocess.run(
            ["conda", "--version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False

def setup_conda_env(repo_root, env_name="curiosity"):
    """Create or update the conda environment from environment.yml."""
    env_file = os.path.join(repo_root, "environment.yml")
    
    if not os.path.exists(env_file):
        print("[!] environment.yml not found. Falling back to pip-based setup.")
        return False
    
    # Check if environment already exists
    result = subprocess.run(
        ["conda", "env", "list"], capture_output=True, text=True
    )
    env_exists = env_name in result.stdout
    
    if env_exists:
        print(f"[*] Updating existing conda environment '{env_name}'...")
        subprocess.run(
            ["conda", "env", "update", "-n", env_name, "-f", env_file, "--prune"],
            check=True
        )
    else:
        print(f"[*] Creating new conda environment '{env_name}'...")
        subprocess.run(
            ["conda", "env", "create", "-f", env_file],
            check=True
        )
    
    print(f"[+] Conda environment '{env_name}' ready.")
    return True

def setup_pip_env(repo_root, has_gpu):
    """Fallback: create a venv and install deps via pip."""
    import venv
    
    env_dir = os.path.abspath(os.path.join(os.path.expanduser("~"), ".param_env"))
    
    if not os.path.exists(env_dir):
        print(f"[*] Creating Python virtual environment at {env_dir}...")
        builder = venv.EnvBuilder(with_pip=True)
        builder.create(env_dir)
    else:
        print(f"[*] Using existing virtual environment at {env_dir}")
    
    pip_exe = os.path.join(env_dir, "Scripts" if is_windows() else "bin", "pip")
    
    # Select the right requirements file
    if has_gpu:
        req_file = os.path.join(repo_root, "requirements-cuda.txt")
        print("[+] NVIDIA GPU detected — installing CUDA-accelerated PyTorch.")
    else:
        req_file = os.path.join(repo_root, "requirements.txt")
        print("[-] No NVIDIA GPU detected — installing CPU-only PyTorch.")
    
    print(f"[*] Installing dependencies from {os.path.basename(req_file)}...")
    subprocess.run([pip_exe, "install", "-r", req_file], check=True)
    
    # Install the project itself in editable mode
    print("[*] Installing Ramanujan@Home engine (editable)...")
    subprocess.run([pip_exe, "install", "-e", repo_root], check=True)
    
    python_exe = os.path.join(env_dir, "Scripts" if is_windows() else "bin", "python")
    return python_exe

def main():
    print("=" * 60)
    print("      Ramanujan@Home — Smart Environment Installer")
    print("=" * 60)
    
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    gpu_available = has_nvidia_gpu()
    conda_available = has_conda()
    
    print(f"\n  System: {'Windows' if is_windows() else 'Linux/macOS'}")
    print(f"  GPU:    {'NVIDIA detected ✓' if gpu_available else 'Not detected (CPU mode)'}")
    print(f"  Conda:  {'Available ✓' if conda_available else 'Not found (using pip/venv)'}")
    print()
    
    if conda_available:
        # Preferred path: use conda
        success = setup_conda_env(repo_root)
        if success:
            print("\n" + "=" * 60)
            print("  Setup Complete!")
            print("  Activate with:  conda activate curiosity")
            print("  Then run:       python scripts/evolve_miner.py --target pi")
            print("=" * 60)
            return
    
    # Fallback: pip + venv
    python_exe = setup_pip_env(repo_root, gpu_available)
    
    print("\n" + "=" * 60)
    print("  Setup Complete!")
    print(f"  Run with:  {python_exe} scripts/evolve_miner.py --target pi")
    print("=" * 60)

if __name__ == "__main__":
    main()
