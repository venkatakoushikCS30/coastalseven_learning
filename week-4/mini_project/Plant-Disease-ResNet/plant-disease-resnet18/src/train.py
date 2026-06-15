"""
Training pipeline for PlantVillage ResNet18.

Supports two modes:
  1. Feature extraction (Phase 4) — frozen backbone, train head only
  2. Fine-tuning (Phase 5)        — unfreeze layer4 + head

Includes early stopping, best-model checkpointing, LR scheduling,
and tqdm progress bars.
"""

from __future__ import annotations

import json
import os
import random
import time
from pathlib import Path
from typing import Any

import numpy as np
import torch
import torch.nn as nn
import yaml
from torch.utils.data import DataLoader
from tqdm import tqdm

from augmentations import get_train_transforms, get_val_transforms
from dataset import PlantVillageDataset, build_file_list, stratified_split, _DEFAULT_DATA_ROOT
from model import build_model, unfreeze_layer4, count_parameters

# ── Reproducibility ─────────────────────────────────────────────────────────

SEED = 42


def seed_everything(seed: int = SEED) -> None:
    """Set seeds for Python, NumPy, and PyTorch for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


# ── Config loader ───────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_config() -> dict[str, Any]:
    """Load hyperparameters from hw_config.yaml."""
    cfg_path = _PROJECT_ROOT / "configs" / "hw_config.yaml"
    with open(cfg_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ── Early stopping ──────────────────────────────────────────────────────────

class EarlyStopping:
    """Stop training when validation loss stops improving."""

    def __init__(self, patience: int = 5, min_delta: float = 1e-4) -> None:
        self.patience = patience
        self.min_delta = min_delta
        self.counter: int = 0
        self.best_loss: float = float("inf")
        self.should_stop: bool = False

    def step(self, val_loss: float) -> bool:
        if val_loss < self.best_loss - self.min_delta:
            self.best_loss = val_loss
            self.counter = 0
        else:
            self.counter += 1
            if self.counter >= self.patience:
                self.should_stop = True
        return self.should_stop


# ── Training / validation loops ─────────────────────────────────────────────

def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    epoch: int,
    total_epochs: int,
) -> tuple[float, float]:
    """Train for one epoch. Returns (avg_loss, accuracy)."""
    model.train()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(loader, desc=f"  Train {epoch}/{total_epochs}", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)

        pbar.set_postfix(loss=f"{loss.item():.4f}", acc=f"{correct/total:.3f}")

    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


@torch.no_grad()
def validate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: torch.device,
    epoch: int,
    total_epochs: int,
) -> tuple[float, float]:
    """Validate the model. Returns (avg_loss, accuracy)."""
    model.eval()
    running_loss = 0.0
    correct = 0
    total = 0

    pbar = tqdm(loader, desc=f"  Val   {epoch}/{total_epochs}", leave=False)
    for images, labels in pbar:
        images, labels = images.to(device), labels.to(device)

        outputs = model(images)
        loss = criterion(outputs, labels)

        running_loss += loss.item() * images.size(0)
        _, preds = outputs.max(1)
        correct += preds.eq(labels).sum().item()
        total += labels.size(0)

        pbar.set_postfix(loss=f"{loss.item():.4f}", acc=f"{correct/total:.3f}")

    avg_loss = running_loss / total
    accuracy = correct / total
    return avg_loss, accuracy


# ── Main training driver ────────────────────────────────────────────────────

def run_training(
    mode: str = "feature_extract",
    checkpoint_path: str | Path | None = None,
) -> dict[str, Any]:
    """Execute a full training run.

    Parameters
    ----------
    mode : str
        ``"feature_extract"`` (Phase 4) or ``"finetune"`` (Phase 5).
    checkpoint_path : str | Path, optional
        Path to a checkpoint to resume from (used in fine-tuning).

    Returns
    -------
    dict
        Training results including best metrics and paths.
    """
    seed_everything(SEED)
    cfg = load_config()
    hp = cfg["hyperparameters"]

    device = torch.device(hp["device"])
    image_size: int = hp["image_size"]
    batch_size: int = hp["batch_size"]
    num_workers: int = hp["num_workers"]

    if mode == "feature_extract":
        epochs: int = hp["epochs_feature_extract"]
        lr: float = hp["lr_feature_extract"]
        freeze = True
    elif mode == "finetune":
        epochs = hp["epochs_finetune"]
        lr = hp["lr_finetune"]
        freeze = True  # build frozen first, then unfreeze layer4
    else:
        raise ValueError(f"Unknown mode: {mode}")

    print("=" * 60)
    print(f"  TRAINING — {mode.upper()}")
    print("=" * 60)
    print(f"  Device       : {device}")
    print(f"  Image size   : {image_size}")
    print(f"  Batch size   : {batch_size}")
    print(f"  Epochs       : {epochs}")
    print(f"  LR           : {lr}")
    print(f"  Workers      : {num_workers}")
    print("=" * 60)

    # ── Data ────────────────────────────────────────────────────────────
    samples = build_file_list(_DEFAULT_DATA_ROOT)
    train_samples, val_samples, _ = stratified_split(samples, seed=SEED)

    train_ds = PlantVillageDataset(train_samples, transform=get_train_transforms(image_size))
    val_ds = PlantVillageDataset(val_samples, transform=get_val_transforms(image_size))

    train_loader = DataLoader(
        train_ds, batch_size=batch_size, shuffle=True,
        num_workers=num_workers, pin_memory=False,
    )
    val_loader = DataLoader(
        val_ds, batch_size=batch_size, shuffle=False,
        num_workers=num_workers, pin_memory=False,
    )

    print(f"\n  Train samples : {len(train_ds)}")
    print(f"  Val   samples : {len(val_ds)}")

    # ── Model ───────────────────────────────────────────────────────────
    model = build_model(freeze_backbone=freeze)

    if mode == "finetune":
        # Load Phase 4 best checkpoint, then unfreeze layer4
        ckpt_path = checkpoint_path or (_PROJECT_ROOT / "models" / "best_feature_extract.pth")
        print(f"\n  Loading checkpoint: {ckpt_path}")
        state = torch.load(ckpt_path, map_location=device, weights_only=True)
        model.load_state_dict(state["model_state_dict"])
        unfreeze_layer4(model)
        print("  Unfroze layer4 for fine-tuning.")

    model = model.to(device)
    params = count_parameters(model)
    print(f"  Trainable params : {params['trainable']:,}")

    # ── Optimiser, scheduler, criterion ─────────────────────────────────
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.Adam(trainable_params, lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode="min", factor=0.5, patience=2,
    )
    criterion = nn.CrossEntropyLoss()
    early_stop = EarlyStopping(patience=5)

    # ── Training loop ───────────────────────────────────────────────────
    models_dir = _PROJECT_ROOT / "models"
    models_dir.mkdir(parents=True, exist_ok=True)
    best_tag = f"best_{mode}"
    best_path = models_dir / f"{best_tag}.pth"

    history: dict[str, list[float]] = {
        "train_loss": [], "train_acc": [],
        "val_loss": [], "val_acc": [],
        "lr": [],
    }
    best_val_acc = 0.0
    best_epoch = 0
    start_time = time.time()

    for epoch in range(1, epochs + 1):
        current_lr = optimizer.param_groups[0]["lr"]
        print(f"\n  Epoch {epoch}/{epochs}  (lr={current_lr:.6f})")

        train_loss, train_acc = train_one_epoch(
            model, train_loader, criterion, optimizer, device, epoch, epochs,
        )
        val_loss, val_acc = validate(
            model, val_loader, criterion, device, epoch, epochs,
        )
        scheduler.step(val_loss)

        history["train_loss"].append(round(train_loss, 4))
        history["train_acc"].append(round(train_acc, 4))
        history["val_loss"].append(round(val_loss, 4))
        history["val_acc"].append(round(val_acc, 4))
        history["lr"].append(current_lr)

        improved = ""
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_epoch = epoch
            torch.save(
                {
                    "epoch": epoch,
                    "model_state_dict": model.state_dict(),
                    "optimizer_state_dict": optimizer.state_dict(),
                    "val_acc": val_acc,
                    "val_loss": val_loss,
                },
                best_path,
            )
            improved = "  ** saved best **"

        print(f"    Train loss={train_loss:.4f}  acc={train_acc:.4f}")
        print(f"    Val   loss={val_loss:.4f}  acc={val_acc:.4f}{improved}")

        if early_stop.step(val_loss):
            print(f"\n  Early stopping triggered at epoch {epoch}.")
            break

    elapsed = time.time() - start_time

    # ── Summary ─────────────────────────────────────────────────────────
    results: dict[str, Any] = {
        "mode": mode,
        "best_epoch": best_epoch,
        "best_val_acc": round(best_val_acc, 4),
        "best_val_loss": round(history["val_loss"][best_epoch - 1], 4),
        "final_train_acc": history["train_acc"][-1],
        "final_train_loss": history["train_loss"][-1],
        "epochs_run": len(history["train_loss"]),
        "elapsed_sec": round(elapsed, 1),
        "best_checkpoint": str(best_path),
        "history": history,
    }

    print(f"\n{'=' * 60}")
    print(f"  {mode.upper()} COMPLETE")
    print(f"{'=' * 60}")
    print(f"  Best epoch     : {results['best_epoch']}")
    print(f"  Best val acc   : {results['best_val_acc']:.4f}")
    print(f"  Best val loss  : {results['best_val_loss']:.4f}")
    print(f"  Epochs run     : {results['epochs_run']}")
    print(f"  Time elapsed   : {results['elapsed_sec']:.1f}s")
    print(f"  Checkpoint     : {results['best_checkpoint']}")
    print(f"{'=' * 60}")

    # Save history
    hist_path = _PROJECT_ROOT / "models" / f"history_{mode}.json"
    with open(hist_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"\n  History saved to {hist_path}")

    return results


# ── CLI entry point ─────────────────────────────────────────────────────────

def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Train PlantVillage ResNet18")
    parser.add_argument(
        "--mode", type=str, default="feature_extract",
        choices=["feature_extract", "finetune"],
        help="Training mode (default: feature_extract)",
    )
    parser.add_argument(
        "--checkpoint", type=str, default=None,
        help="Path to checkpoint for fine-tuning",
    )
    args = parser.parse_args()
    run_training(mode=args.mode, checkpoint_path=args.checkpoint)


if __name__ == "__main__":
    main()
