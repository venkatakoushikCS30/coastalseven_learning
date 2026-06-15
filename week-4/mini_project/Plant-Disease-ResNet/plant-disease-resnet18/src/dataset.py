"""
Dataset loading, analysis, and train/val/test splitting for PlantVillage.

Dynamically discovers class names and image counts from the directory
structure — nothing is hardcoded.
"""

from __future__ import annotations

import json
import os
import random
from collections import Counter
from pathlib import Path
from typing import Any

import yaml
from PIL import Image
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms

# Supported image extensions
_IMG_EXTS: set[str] = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tif", ".tiff"}

# ── Default dataset root (relative to project) ──────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_DEFAULT_DATA_ROOT = _PROJECT_ROOT.parent / "PlantVillage"


def discover_classes(data_root: Path | str) -> list[str]:
    """Return sorted list of class-folder names, skipping nested duplicates."""
    data_root = Path(data_root)
    classes = sorted(
        d.name
        for d in data_root.iterdir()
        if d.is_dir() and d.name != "PlantVillage"
    )
    return classes


def count_images_per_class(data_root: Path | str) -> dict[str, int]:
    """Return {class_name: image_count} by scanning image extensions."""
    data_root = Path(data_root)
    classes = discover_classes(data_root)
    counts: dict[str, int] = {}
    for cls in classes:
        cls_dir = data_root / cls
        n = sum(
            1
            for f in cls_dir.iterdir()
            if f.is_file() and f.suffix.lower() in _IMG_EXTS
        )
        counts[cls] = n
    return counts


def build_file_list(data_root: Path | str) -> list[tuple[str, int]]:
    """Return list of (image_path, label_index) tuples."""
    data_root = Path(data_root)
    classes = discover_classes(data_root)
    class_to_idx = {c: i for i, c in enumerate(classes)}
    samples: list[tuple[str, int]] = []
    for cls in classes:
        cls_dir = data_root / cls
        for f in sorted(cls_dir.iterdir()):
            if f.is_file() and f.suffix.lower() in _IMG_EXTS:
                samples.append((str(f), class_to_idx[cls]))
    return samples


# ── Dataset class ────────────────────────────────────────────────────────────

class PlantVillageDataset(Dataset):
    """PyTorch Dataset for PlantVillage images."""

    def __init__(
        self,
        samples: list[tuple[str, int]],
        transform: transforms.Compose | None = None,
    ) -> None:
        self.samples = samples
        self.transform = transform

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> tuple:
        path, label = self.samples[idx]
        img = Image.open(path).convert("RGB")
        if self.transform:
            img = self.transform(img)
        return img, label


# ── Splitting utilities ─────────────────────────────────────────────────────

def stratified_split(
    samples: list[tuple[str, int]],
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
) -> tuple[list[tuple[str, int]], list[tuple[str, int]], list[tuple[str, int]]]:
    """Stratified split into train / val / test lists."""
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

    rng = random.Random(seed)
    by_class: dict[int, list[tuple[str, int]]] = {}
    for s in samples:
        by_class.setdefault(s[1], []).append(s)

    train, val, test = [], [], []
    for label in sorted(by_class):
        items = by_class[label]
        rng.shuffle(items)
        n = len(items)
        n_train = int(n * train_ratio)
        n_val = int(n * val_ratio)
        train.extend(items[:n_train])
        val.extend(items[n_train : n_train + n_val])
        test.extend(items[n_train + n_val :])

    return train, val, test


# ── Analysis & reporting ────────────────────────────────────────────────────

def analyse_dataset(data_root: Path | str | None = None) -> dict[str, Any]:
    """Run full dataset analysis and return a stats dictionary."""
    if data_root is None:
        data_root = _DEFAULT_DATA_ROOT
    data_root = Path(data_root)

    classes = discover_classes(data_root)
    counts = count_images_per_class(data_root)
    total = sum(counts.values())

    samples = build_file_list(data_root)
    train, val, test = stratified_split(samples)

    stats: dict[str, Any] = {
        "data_root": str(data_root),
        "num_classes": len(classes),
        "class_names": classes,
        "total_images": total,
        "per_class_counts": counts,
        "split_sizes": {
            "train": len(train),
            "val": len(val),
            "test": len(test),
        },
        "most_common": max(counts, key=counts.get),  # type: ignore[arg-type]
        "least_common": min(counts, key=counts.get),  # type: ignore[arg-type]
    }
    return stats


def print_analysis(stats: dict[str, Any]) -> None:
    """Pretty-print dataset analysis to stdout."""
    print("=" * 60)
    print("  PLANTVILLAGE DATASET ANALYSIS")
    print("=" * 60)
    print(f"\n  Data root    : {stats['data_root']}")
    print(f"  Num classes  : {stats['num_classes']}")
    print(f"  Total images : {stats['total_images']}")
    print(f"\n  {'Class Name':<55s} {'Count':>6s}")
    print("  " + "-" * 62)
    for cls, cnt in sorted(stats["per_class_counts"].items()):
        print(f"  {cls:<55s} {cnt:>6d}")
    print("  " + "-" * 62)
    print(f"  {'TOTAL':<55s} {stats['total_images']:>6d}")

    print(f"\n  Most  common : {stats['most_common']} "
          f"({stats['per_class_counts'][stats['most_common']]})")
    print(f"  Least common : {stats['least_common']} "
          f"({stats['per_class_counts'][stats['least_common']]})")

    sp = stats["split_sizes"]
    print(f"\n  Split (70/15/15) : "
          f"Train={sp['train']}, Val={sp['val']}, Test={sp['test']}")
    print("\n" + "=" * 60)


def main() -> None:
    stats = analyse_dataset()
    print_analysis(stats)

    # Save class names for downstream use
    out_dir = _PROJECT_ROOT / "configs"
    out_dir.mkdir(parents=True, exist_ok=True)
    class_names_path = out_dir / "class_names.json"
    with open(class_names_path, "w", encoding="utf-8") as f:
        json.dump(stats["class_names"], f, indent=2)
    print(f"\n[OK] Class names saved to {class_names_path}")


if __name__ == "__main__":
    main()
