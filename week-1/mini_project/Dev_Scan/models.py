# models.py
from dataclasses import dataclass
from typing import TypedDict, Dict, List

@dataclass
class FileResult:
    """Represents the raw data extracted from a single file"""
    path: str
    rel_path: str
    lines: List[str]
    size_bytes: int

class FileStat(TypedDict):
    """Represents the computed health statistics for a single file"""
    file_name: str
    functions: List[str]
    todos: int
    max_complexity: int
    avg_complexity: float
    dead_functions: List[str]
    health: str  # 'Green', 'Yellow', 'Red'

class ProjectSummary(TypedDict):
    """Represents the aggregated metrics for the entire codebase"""
    total_files: int
    total_functions: int
    total_todos: int
    dead_functions: List[str]
    duplicate_functions: Dict[str, List[str]]
    worst_file: str
    scan_timestamp: str