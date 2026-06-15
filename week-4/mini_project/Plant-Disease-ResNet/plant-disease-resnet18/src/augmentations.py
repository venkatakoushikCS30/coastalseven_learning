"""
Image augmentation pipelines for PlantVillage training and evaluation.

Training uses aggressive augmentations to improve generalisation on a
relatively small dataset.  Val/Test use deterministic resize + center-crop
so that metrics are reproducible.

ImageNet statistics are used for normalisation because the ResNet18 backbone
was pre-trained on ImageNet.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from torchvision import transforms

# ── ImageNet channel statistics (used by pre-trained ResNet) ────────────────
IMAGENET_MEAN: list[float] = [0.485, 0.456, 0.406]
IMAGENET_STD: list[float] = [0.229, 0.224, 0.225]

# ── Config loader ───────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _load_image_size() -> int:
    """Read image_size from hw_config.yaml; fall back to 128."""
    cfg_path = _PROJECT_ROOT / "configs" / "hw_config.yaml"
    if cfg_path.exists():
        with open(cfg_path, "r", encoding="utf-8") as f:
            cfg: dict[str, Any] = yaml.safe_load(f)
        return int(cfg.get("hyperparameters", {}).get("image_size", 128))
    return 128


# ── Transform factories ─────────────────────────────────────────────────────

def get_train_transforms(image_size: int | None = None) -> transforms.Compose:
    """Return the training augmentation pipeline.

    Parameters
    ----------
    image_size : int, optional
        Target spatial size.  Loaded from config if not supplied.
    """
    if image_size is None:
        image_size = _load_image_size()

    return transforms.Compose([
        # Randomly crop and resize to target size, simulating scale variation
        transforms.RandomResizedCrop(image_size, scale=(0.8, 1.0)),
        # Mirror horizontally to double effective dataset size
        transforms.RandomHorizontalFlip(p=0.5),
        # Mirror vertically — leaves can appear in any orientation
        transforms.RandomVerticalFlip(p=0.5),
        # Rotate up to 15 degrees to handle camera-angle differences
        transforms.RandomRotation(degrees=15),
        # Perturb brightness, contrast, saturation, and hue to reduce colour bias
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        # Convert PIL image to [C, H, W] float tensor in [0, 1]
        transforms.ToTensor(),
        # Normalise channels to ImageNet statistics for pre-trained backbone
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


def get_val_transforms(image_size: int | None = None) -> transforms.Compose:
    """Return the validation / test transform pipeline (deterministic).

    Parameters
    ----------
    image_size : int, optional
        Target spatial size.  Loaded from config if not supplied.
    """
    if image_size is None:
        image_size = _load_image_size()

    # Resize slightly larger then center-crop to keep consistent framing
    resize_target = int(image_size * 1.14)  # e.g. 128 -> 146

    return transforms.Compose([
        # Resize to slightly larger than target for a clean centre crop
        transforms.Resize(resize_target),
        # Deterministic centre crop to exact target size
        transforms.CenterCrop(image_size),
        # Convert PIL image to [C, H, W] float tensor in [0, 1]
        transforms.ToTensor(),
        # Normalise channels to ImageNet statistics for pre-trained backbone
        transforms.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD),
    ])


# Alias — test uses the same deterministic pipeline as validation
get_test_transforms = get_val_transforms


# ── Inverse normalisation (for visualisation) ───────────────────────────────

def get_inverse_normalize() -> transforms.Normalize:
    """Return a Normalize transform that undoes ImageNet normalisation.

    Useful when visualising model predictions or misclassified images.
    """
    inv_mean = [-m / s for m, s in zip(IMAGENET_MEAN, IMAGENET_STD)]
    inv_std = [1.0 / s for s in IMAGENET_STD]
    return transforms.Normalize(mean=inv_mean, std=inv_std)


# ── Quick sanity check ──────────────────────────────────────────────────────

def main() -> None:
    """Print the transform pipelines for verification."""
    image_size = _load_image_size()
    print(f"Image size from config: {image_size}\n")

    print("=== TRAIN transforms ===")
    train_t = get_train_transforms(image_size)
    for i, t in enumerate(train_t.transforms):
        print(f"  [{i}] {t}")

    print("\n=== VAL / TEST transforms ===")
    val_t = get_val_transforms(image_size)
    for i, t in enumerate(val_t.transforms):
        print(f"  [{i}] {t}")

    # Verify on a dummy tensor
    from PIL import Image
    import torch
    dummy = Image.new("RGB", (256, 256), color=(128, 200, 100))
    out_train = train_t(dummy)
    out_val = val_t(dummy)
    print(f"\nTrain output shape : {out_train.shape}")
    print(f"Val   output shape : {out_val.shape}")
    print(f"Train pixel range  : [{out_train.min():.3f}, {out_train.max():.3f}]")
    print(f"Val   pixel range  : [{out_val.min():.3f}, {out_val.max():.3f}]")
    print("\n[OK] Augmentation pipelines verified.")


if __name__ == "__main__":
    main()
