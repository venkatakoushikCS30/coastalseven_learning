# scanner.py
import os
import logging
from pathlib import Path
from typing import List, Set
from models import FileResult

logger = logging.getLogger(__name__)

class Scanner:
    def __init__(self, lang: str):
        """Initializes the scanner with the target language."""
        self.lang = lang
        self.max_size_bytes = 1024 * 1024  # 1 MB threshold

    def _is_valid_extension(self, filename: str) -> bool:
        """Helper to check if a file matches the requested language."""
        ext = Path(filename).suffix.lower()
        if self.lang in ("python", "all") and ext == ".py":
            return True
        if self.lang in ("js", "all") and ext == ".js":
            return True
        return False

    def scan(self, target_dir: Path) -> List[FileResult]:
        """Traverses the directory and returns a list of FileResults."""
        logger.info(f"Scanning directory: {target_dir}")
        
        seen_paths: Set[str] = set()
        results: List[FileResult] = []
        resolved_target_dir = target_dir.resolve()

        for root, dirs, files in os.walk(target_dir):
            # Modify 'dirs' in-place to skip hidden directories and __pycache__
            dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']

            for file in files:
                if not self._is_valid_extension(file):
                    continue

                abs_path = Path(root) / file
                resolved_path = abs_path.resolve()
                
                # Prevent double-processing
                if str(resolved_path) in seen_paths:
                    continue
                seen_paths.add(str(resolved_path))

                # Skip files exceeding 1 MB
                try:
                    size_bytes = resolved_path.stat().st_size
                    if size_bytes > self.max_size_bytes:
                        logger.warning(f"Skipping {abs_path}: File exceeds 1MB limit.")
                        continue
                except OSError as e:
                    logger.warning(f"Skipping {abs_path}: Could not read file stats. ({e})")
                    continue

                # Safely attempt to read the file
                try:
                    with open(resolved_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        
                    rel_path = resolved_path.relative_to(resolved_target_dir)
                    
                    results.append(FileResult(
                        path=str(resolved_path),
                        rel_path=str(rel_path),
                        lines=lines,
                        size_bytes=size_bytes
                    ))
                except (UnicodeDecodeError, PermissionError):
                    # Catch and ignore UnicodeDecodeError and PermissionError
                    pass
                except Exception as e:
                    logger.warning(f"Skipping {abs_path}: Unexpected error ({e}).")

        logger.info(f"Scan complete. Found {len(results)} valid files.")
        return results