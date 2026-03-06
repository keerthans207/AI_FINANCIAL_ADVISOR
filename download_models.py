#!/usr/bin/env python3
"""
Download Phi-2 GGUF model for local RAG system
Optimized for 4GB RAM, CPU-only
"""

import os
import sys
from pathlib import Path
import urllib.request
from tqdm import tqdm

# Model configuration
MODEL_URL = "https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
MODEL_NAME = "phi-2.Q4_K_M.gguf"
MODELS_DIR = Path("models")
MODEL_PATH = MODELS_DIR / MODEL_NAME

# Model size: ~1.6GB
EXPECTED_SIZE_MB = 1600


class DownloadProgressBar(tqdm):
    """Progress bar for downloads"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_model():
    """Download Phi-2 Q4_K_M GGUF model"""
    
    print("="*60)
    print("  Phi-2 GGUF Model Downloader")
    print("  Optimized for 4GB RAM, CPU-only")
    print("="*60)
    print()
    
    # Create models directory
    MODELS_DIR.mkdir(exist_ok=True)
    print(f"✓ Models directory: {MODELS_DIR}")
    
    # Check if model already exists
    if MODEL_PATH.exists():
        size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
        print(f"✓ Model already exists: {MODEL_PATH}")
        print(f"  Size: {size_mb:.1f} MB")
        
        response = input("\nRe-download? (y/N): ")
        if response.lower() != 'y':
            print("Skipping download.")
            return
        
        print("Removing existing model...")
        MODEL_PATH.unlink()
    
    print()
    print(f"Downloading: {MODEL_NAME}")
    print(f"From: {MODEL_URL}")
    print(f"Expected size: ~{EXPECTED_SIZE_MB} MB")
    print()
    print("This may take 10-30 minutes depending on your connection...")
    print()
    
    try:
        with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=MODEL_NAME) as t:
            urllib.request.urlretrieve(
                MODEL_URL,
                MODEL_PATH,
                reporthook=t.update_to
            )
        
        # Verify download
        size_mb = MODEL_PATH.stat().st_size / (1024 * 1024)
        print()
        print("="*60)
        print("✓ Download complete!")
        print(f"  Location: {MODEL_PATH}")
        print(f"  Size: {size_mb:.1f} MB")
        print("="*60)
        print()
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements-llm.txt")
        print("2. Start server: python -m uvicorn app.main:app --host 127.0.0.1 --port 8010")
        print("3. Test RAG: curl http://localhost:8010/rag/status")
        print()
        
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
            print("Partial download removed.")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n✗ Download failed: {e}")
        if MODEL_PATH.exists():
            MODEL_PATH.unlink()
        sys.exit(1)


def check_system_requirements():
    """Check if system meets requirements"""
    
    print("Checking system requirements...")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return False
    print(f"✓ Python {sys.version_info.major}.{sys.version_info.minor}")
    
    # Check available disk space
    import shutil
    stat = shutil.disk_usage(MODELS_DIR.parent)
    free_gb = stat.free / (1024**3)
    
    if free_gb < 2:
        print(f"✗ Insufficient disk space: {free_gb:.1f} GB free (need 2GB)")
        return False
    print(f"✓ Disk space: {free_gb:.1f} GB free")
    
    # Check RAM (approximate)
    try:
        import psutil
        ram_gb = psutil.virtual_memory().total / (1024**3)
        print(f"✓ RAM: {ram_gb:.1f} GB")
        
        if ram_gb < 4:
            print("⚠ Warning: Less than 4GB RAM detected. System may be slow.")
    except ImportError:
        print("⚠ Cannot check RAM (psutil not installed)")
    
    print()
    return True


if __name__ == "__main__":
    print()
    
    if not check_system_requirements():
        print("\nSystem requirements not met.")
        sys.exit(1)
    
    try:
        download_model()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
