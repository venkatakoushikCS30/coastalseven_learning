"""
Hardware detection and configuration generator for Plant Disease Detection.

Detects CPU, RAM, GPU/VRAM, and storage; writes optimal training
hyperparameters to configs/hw_config.yaml.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import psutil
import yaml


def get_cpu_info() -> dict[str, Any]:
    """Return CPU model, architecture, and logical/physical core counts."""
    info: dict[str, Any] = {
        "model": platform.processor() or "Unknown",
        "architecture": platform.machine(),
        "logical_cores": psutil.cpu_count(logical=True),
        "physical_cores": psutil.cpu_count(logical=False),
    }
    # Try to get a friendlier CPU name on Windows
    if platform.system() == "Windows":
        try:
            out = subprocess.check_output(
                ["wmic", "cpu", "get", "Name"],
                text=True,
                stderr=subprocess.DEVNULL,
            )
            lines = [l.strip() for l in out.strip().splitlines() if l.strip()]
            if len(lines) >= 2:
                info["model"] = lines[1]
        except Exception:
            pass
    return info


def get_ram_info() -> dict[str, Any]:
    """Return total and available RAM in GB."""
    mem = psutil.virtual_memory()
    return {
        "total_gb": round(mem.total / (1024**3), 2),
        "available_gb": round(mem.available / (1024**3), 2),
    }


def get_gpu_info() -> dict[str, Any]:
    """Detect NVIDIA GPU via PyTorch CUDA or fall back to CPU-only."""
    gpu: dict[str, Any] = {
        "available": False,
        "name": None,
        "vram_gb": None,
        "cuda_version": None,
        "cudnn_version": None,
    }
    try:
        import torch

        if torch.cuda.is_available():
            gpu["available"] = True
            gpu["name"] = torch.cuda.get_device_name(0)
            gpu["vram_gb"] = round(
                torch.cuda.get_device_properties(0).total_mem / (1024**3), 2
            )
            gpu["cuda_version"] = torch.version.cuda
            gpu["cudnn_version"] = str(torch.backends.cudnn.version())
    except ImportError:
        pass
    return gpu


def get_storage_info(path: str = ".") -> dict[str, Any]:
    """Return total and free disk space for the partition containing *path*."""
    usage = shutil.disk_usage(path)
    return {
        "total_gb": round(usage.total / (1024**3), 2),
        "free_gb": round(usage.free / (1024**3), 2),
    }


def get_python_env() -> dict[str, str]:
    """Capture Python and key library versions."""
    env: dict[str, str] = {
        "python_version": platform.python_version(),
        "os": f"{platform.system()} {platform.release()}",
    }
    try:
        import torch
        env["pytorch_version"] = str(torch.__version__)
    except ImportError:
        env["pytorch_version"] = "NOT INSTALLED"
    return env


# ── Hyperparameter heuristics ───────────────────────────────────────────────

def compute_hyperparams(
    ram_gb: float,
    gpu_available: bool,
    vram_gb: float | None,
    physical_cores: int,
) -> dict[str, Any]:
    """Derive safe training hyperparameters from detected hardware."""
    # Image size
    if gpu_available and vram_gb and vram_gb >= 6:
        image_size = 224
    elif gpu_available and vram_gb and vram_gb >= 3:
        image_size = 192
    else:
        image_size = 128

    # Batch size
    if gpu_available and vram_gb:
        if vram_gb >= 8:
            batch_size = 64
        elif vram_gb >= 4:
            batch_size = 32
        elif vram_gb >= 2:
            batch_size = 16
        else:
            batch_size = 8
    else:
        batch_size = 16 if ram_gb >= 8 else 8

    # Epochs
    epochs_feature_extract = 10
    epochs_finetune = 10

    # DataLoader workers
    num_workers = min(physical_cores or 2, 4)

    # Learning rates
    lr_feature_extract = 1e-3
    lr_finetune = 1e-4

    # Mixed precision
    use_amp = gpu_available

    return {
        "image_size": image_size,
        "batch_size": batch_size,
        "epochs_feature_extract": epochs_feature_extract,
        "epochs_finetune": epochs_finetune,
        "num_workers": num_workers,
        "lr_feature_extract": lr_feature_extract,
        "lr_finetune": lr_finetune,
        "use_amp": use_amp,
        "device": "cuda" if gpu_available else "cpu",
    }


# ── Main ────────────────────────────────────────────────────────────────────

def run_hardware_check(project_root: Path | None = None) -> dict[str, Any]:
    """Run full hardware inspection and return the consolidated report."""
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent

    cpu = get_cpu_info()
    ram = get_ram_info()
    gpu = get_gpu_info()
    storage = get_storage_info(str(project_root))
    env = get_python_env()
    hyperparams = compute_hyperparams(
        ram_gb=ram["total_gb"],
        gpu_available=gpu["available"],
        vram_gb=gpu["vram_gb"],
        physical_cores=cpu["physical_cores"],
    )

    report: dict[str, Any] = {
        "cpu": cpu,
        "ram": ram,
        "gpu": gpu,
        "storage": storage,
        "environment": env,
        "hyperparameters": hyperparams,
    }
    return report


def save_config(report: dict[str, Any], project_root: Path) -> Path:
    """Persist hardware config as YAML."""
    config_dir = project_root / "configs"
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / "hw_config.yaml"
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(report, f, default_flow_style=False, sort_keys=False)
    return config_path


def print_report(report: dict[str, Any]) -> None:
    """Pretty-print the hardware report to stdout."""
    print("=" * 60)
    print("  HARDWARE & ENVIRONMENT REPORT")
    print("=" * 60)

    cpu = report["cpu"]
    print(f"\n[CPU]")
    print(f"  Model          : {cpu['model']}")
    print(f"  Architecture   : {cpu['architecture']}")
    print(f"  Physical cores : {cpu['physical_cores']}")
    print(f"  Logical cores  : {cpu['logical_cores']}")

    ram = report["ram"]
    print(f"\n[RAM]")
    print(f"  Total          : {ram['total_gb']} GB")
    print(f"  Available      : {ram['available_gb']} GB")

    gpu = report["gpu"]
    print(f"\n[GPU]")
    if gpu["available"]:
        print(f"  Name           : {gpu['name']}")
        print(f"  VRAM           : {gpu['vram_gb']} GB")
        print(f"  CUDA           : {gpu['cuda_version']}")
        print(f"  cuDNN          : {gpu['cudnn_version']}")
    else:
        print("  No CUDA GPU detected — will train on CPU.")

    storage = report["storage"]
    print(f"\n[Storage]")
    print(f"  Total          : {storage['total_gb']} GB")
    print(f"  Free           : {storage['free_gb']} GB")

    env = report["environment"]
    print(f"\n[Environment]")
    for k, v in env.items():
        print(f"  {k:16s}: {v}")

    hp = report["hyperparameters"]
    print(f"\n[Derived Hyperparameters]")
    for k, v in hp.items():
        print(f"  {k:24s}: {v}")

    print("\n" + "=" * 60)


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    report = run_hardware_check(project_root)
    print_report(report)
    config_path = save_config(report, project_root)
    print(f"\n[OK] Config saved to {config_path}")


if __name__ == "__main__":
    main()
