"""
ResNet18 transfer-learning model for PlantVillage classification.

The backbone is loaded with ImageNet pre-trained weights and frozen.
Only the new classification head is trainable during feature-extraction
training (Phase 4).  Phase 5 unfreezes layer4 for fine-tuning.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
import torch.nn as nn
from torchvision import models
from torchvision.models import ResNet18_Weights


_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_num_classes() -> int:
    """Read num_classes from configs/class_names.json."""
    path = _PROJECT_ROOT / "configs" / "class_names.json"
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return len(json.load(f))
    raise FileNotFoundError(
        f"class_names.json not found at {path}. Run dataset.py first."
    )


# ── Model builder ───────────────────────────────────────────────────────────

def build_model(
    num_classes: int | None = None,
    freeze_backbone: bool = True,
    pretrained: bool = True,
) -> nn.Module:
    """Build a ResNet18 with a replaced classification head.

    Parameters
    ----------
    num_classes : int, optional
        Number of output classes.  Auto-detected from config if omitted.
    freeze_backbone : bool
        If True, all backbone parameters are frozen (requires_grad=False).
    pretrained : bool
        If True, load ImageNet pre-trained weights.

    Returns
    -------
    nn.Module
        The modified ResNet18 model.
    """
    if num_classes is None:
        num_classes = _load_num_classes()

    weights = ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
    model = models.resnet18(weights=weights)

    # Freeze the entire backbone
    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace the final fully-connected layer with a new head
    in_features: int = model.fc.in_features
    model.fc = nn.Sequential(
        nn.Dropout(p=0.3),
        nn.Linear(in_features, num_classes),
    )

    return model


# ── Freeze / unfreeze helpers ───────────────────────────────────────────────

def unfreeze_layer4(model: nn.Module) -> None:
    """Unfreeze ResNet18 layer4 for fine-tuning (Phase 5)."""
    for param in model.layer4.parameters():
        param.requires_grad = True


def freeze_backbone(model: nn.Module) -> None:
    """Re-freeze everything except the classification head."""
    for name, param in model.named_parameters():
        if not name.startswith("fc"):
            param.requires_grad = False


# ── Param counting ──────────────────────────────────────────────────────────

def count_parameters(model: nn.Module) -> dict[str, int]:
    """Return counts of total, trainable, and frozen parameters."""
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    frozen = total - trainable
    return {"total": total, "trainable": trainable, "frozen": frozen}


def print_param_summary(model: nn.Module, title: str = "Model") -> None:
    """Print a formatted summary of trainable vs frozen parameters."""
    counts = count_parameters(model)
    pct = (counts["trainable"] / counts["total"] * 100) if counts["total"] else 0

    print(f"\n{'=' * 55}")
    print(f"  {title} — Parameter Summary")
    print(f"{'=' * 55}")
    print(f"  Total params      : {counts['total']:>12,d}")
    print(f"  Trainable params  : {counts['trainable']:>12,d}  ({pct:.1f}%)")
    print(f"  Frozen params     : {counts['frozen']:>12,d}  ({100 - pct:.1f}%)")
    print(f"{'=' * 55}")


def print_layer_status(model: nn.Module) -> None:
    """Print per-layer freeze/trainable status."""
    print(f"\n  {'Layer':<40s} {'Params':>10s}  {'Status':<10s}")
    print("  " + "-" * 64)
    for name, param in model.named_parameters():
        status = "TRAIN" if param.requires_grad else "FROZEN"
        print(f"  {name:<40s} {param.numel():>10,d}  {status}")


# ── Quick test ──────────────────────────────────────────────────────────────

def main() -> None:
    """Build model, print summary, and run a dummy forward pass."""
    num_classes = _load_num_classes()
    print(f"Detected num_classes = {num_classes}")

    # Build with frozen backbone (Phase 4 mode)
    model = build_model(num_classes=num_classes, freeze_backbone=True)
    print_param_summary(model, title="ResNet18 — Feature Extraction (Phase 4)")
    print_layer_status(model)

    # Dummy forward pass
    dummy = torch.randn(2, 3, 128, 128)
    model.eval()
    with torch.no_grad():
        out = model(dummy)
    print(f"\n  Dummy input  : {list(dummy.shape)}")
    print(f"  Dummy output : {list(out.shape)}")
    assert out.shape == (2, num_classes), f"Expected (2, {num_classes}), got {out.shape}"
    print("  Forward pass OK")

    # Preview fine-tune mode (Phase 5)
    unfreeze_layer4(model)
    print_param_summary(model, title="ResNet18 — Fine-Tune layer4 (Phase 5)")

    print("\n[OK] Model initialisation verified.")


if __name__ == "__main__":
    main()
