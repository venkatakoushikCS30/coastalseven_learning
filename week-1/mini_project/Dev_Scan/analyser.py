# analyser.py
import ast
import re
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import deque
from models import FileResult, FileStat, ProjectSummary

logger = logging.getLogger(__name__)

# Base thresholds mapping for health indicators
THRESHOLDS = {
    'todos': {'yellow': 3, 'red': 6},
    'complexity': {'yellow': 6, 'red': 10},
    'dead_functions': {'yellow': 1, 'red': 3},
    'duplicate_functions': {'yellow': 1, 'red': 2}
}

def walk_non_function(node: ast.AST):
    """Helper to walk AST without descending into nested functions."""
    todo = deque([node])
    while todo:
        curr = todo.popleft()
        if curr is not node and isinstance(curr, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for child in ast.iter_child_nodes(curr):
            yield child
            todo.append(child)

class CodeVisitor(ast.NodeVisitor):
    """Visits AST nodes to extract functions, calls, and compute complexity."""
    def __init__(self):
        self.functions: Dict[str, int] = {}  # func_name -> complexity
        self.calls: Set[str] = set()

    def visit_FunctionDef(self, node: ast.FunctionDef):
        # Base complexity is 1. Add +1 for every If, For, While, ExceptHandler, and Match node found.
        complexity = 1
        for child in walk_non_function(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.ExceptHandler, ast.Match, ast.AsyncFor)):
                complexity += 1
        self.functions[node.name] = complexity
        self.generic_visit(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        self.visit_FunctionDef(node)

    def visit_Call(self, node: ast.Call):
        if isinstance(node.func, ast.Name):
            self.calls.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.calls.add(node.func.attr)
        self.generic_visit(node)

class Analyser:
    def __init__(self):
        # Match both Python (#) and JS (//, /*, *) comments containing TODO, FIXME, or HACK
        self.todo_pattern = re.compile(r'(?:#|\/\/|\/\*|\*).*?\b(TODO|FIXME|HACK)\b', re.IGNORECASE)

    def _count_todos(self, lines: List[str]) -> int:
        """Counts TODO, FIXME, and HACK comments."""
        return sum(1 for line in lines if self.todo_pattern.search(line))

    def _analyse_js(self, source_code: str) -> Tuple[Dict[str, int], Set[str]]:
        """Custom static analysis for JavaScript files using regex and brace tracking."""
        funcs: Dict[str, int] = {}
        calls: Set[str] = set()
        
        # 1. Strip comments to avoid matching functions/calls inside comments
        def strip_js_comments(code: str) -> str:
            def repl(match):
                s = match.group(0)
                if s.startswith('/') or s.startswith('*'):
                    return ' ' * len(s)
                return s
            # Match string literals and comments to avoid stripping // inside strings
            pattern = re.compile(r'("(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|`(?:\\.|[^`\\])*`|/\*.*?\*/|//[^\r\n]*)', re.DOTALL)
            return pattern.sub(repl, code)

        clean_code = strip_js_comments(source_code)
        
        # Match common JS function declarations:
        # Group 1: function name(...)
        # Group 2: const/let/var name = (...) =>
        # Group 3: const/let/var name = function(...)
        # Group 4: method_name(...) { (at start of line or in classes/objects)
        func_pattern = re.compile(
            r'\bfunction\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\b|'
            r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[a-zA-Z_$][a-zA-Z0-9_$]*)\s*=>|'
            r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*=\s*(?:async\s*)?function\b|'
            r'^\s*([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\([^)]*\)\s*\{',
            re.MULTILINE
        )
        
        js_keywords = {'if', 'for', 'while', 'catch', 'switch', 'case', 'function', 'const', 'let', 'var', 'return', 'default', 'import', 'export', 'class', 'extends', 'super', 'this'}
        
        # Find function starts and names
        func_starts: List[Tuple[str, int]] = []
        for match in func_pattern.finditer(clean_code):
            name = match.group(1) or match.group(2) or match.group(3) or match.group(4)
            if name and name not in js_keywords:
                func_starts.append((name, match.end()))

        # Compute complexity and extract calls by scanning function bodies
        for name, start_pos in func_starts:
            brace_idx = clean_code.find('{', start_pos)
            if brace_idx == -1:
                funcs[name] = 1
                continue
            
            brace_count = 1
            curr_idx = brace_idx + 1
            code_len = len(clean_code)
            while curr_idx < code_len and brace_count > 0:
                char = clean_code[curr_idx]
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                curr_idx += 1
                
            body = clean_code[brace_idx:curr_idx]
            
            # Base complexity is 1. Add +1 for every if, for, while, catch, case
            complexity = 1
            branch_matches = re.findall(r'\b(if|for|while|catch|case)\b', body)
            complexity += len(branch_matches)
            funcs[name] = complexity

        # Find all function calls (e.g. name(...) where name is not a keyword)
        call_pattern = re.compile(r'\b([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(')
        for match in call_pattern.finditer(clean_code):
            cname = match.group(1)
            if cname not in js_keywords:
                calls.add(cname)
                
        return funcs, calls

    def _calculate_health(self, stat: FileStat, duplicates: int) -> str:
        """Determines the file health color based on thresholds."""
        # Check against red thresholds first
        if (stat['todos'] >= THRESHOLDS['todos']['red'] or
            stat['max_complexity'] >= THRESHOLDS['complexity']['red'] or
            len(stat['dead_functions']) >= THRESHOLDS['dead_functions']['red'] or
            duplicates >= THRESHOLDS['duplicate_functions']['red']):
            return 'Red'
            
        # Check against yellow thresholds
        if (stat['todos'] >= THRESHOLDS['todos']['yellow'] or
            stat['max_complexity'] >= THRESHOLDS['complexity']['yellow'] or
            len(stat['dead_functions']) >= THRESHOLDS['dead_functions']['yellow'] or
            duplicates >= THRESHOLDS['duplicate_functions']['yellow']):
            return 'Yellow'
            
        return 'Green'

    def analyse(self, file_results: List[FileResult]) -> Tuple[Dict[str, FileStat], ProjectSummary]:
        """Performs static analysis on the collection of files."""
        file_stats: Dict[str, FileStat] = {}
        all_defined_functions: Dict[str, List[str]] = {}  # name -> list of file paths
        all_called_functions: Set[str] = set()
        
        total_todos = 0
        total_functions_count = 0
        worst_file = ""
        highest_global_complexity = -1

        # Pass 1: Per-file analysis
        for result in file_results:
            source_code = "".join(result.lines)
            todos = self._count_todos(result.lines)
            total_todos += todos
            
            funcs: Dict[str, int] = {}
            
            if result.path.endswith('.py'):
                try:
                    tree = ast.parse(source_code, filename=result.path)
                    visitor = CodeVisitor()
                    visitor.visit(tree)
                    funcs = visitor.functions
                    all_called_functions.update(visitor.calls)
                except SyntaxError as e:
                    logger.warning(f"Syntax error in {result.rel_path}: {e}. Skipping AST analysis.")
                except Exception as e:
                    logger.warning(f"Failed to parse {result.rel_path}: {e}")
            elif result.path.endswith('.js'):
                try:
                    funcs, calls = self._analyse_js(source_code)
                    all_called_functions.update(calls)
                except Exception as e:
                    logger.warning(f"Failed to parse JavaScript {result.rel_path}: {e}")

            # Calculate complexity metrics
            max_c = max(funcs.values()) if funcs else 0
            avg_c = sum(funcs.values()) / len(funcs) if funcs else 0.0
            
            total_functions_count += len(funcs)
            if max_c > highest_global_complexity:
                highest_global_complexity = max_c
                worst_file = result.rel_path

            for func_name in funcs.keys():
                all_defined_functions.setdefault(func_name, []).append(result.rel_path)

            file_stats[result.rel_path] = {
                'file_name': Path(result.path).name,
                'functions': list(funcs.keys()),
                'todos': todos,
                'max_complexity': max_c,
                'avg_complexity': avg_c,
                'dead_functions': [],  # To be filled in Pass 2
                'health': 'Green'      # To be filled in Pass 2
            }

        # Pass 2: Cross-file metrics
        duplicate_functions = {name: paths for name, paths in all_defined_functions.items() if len(paths) > 1 and not name.startswith('__')}
        dead_functions = [name for name in all_defined_functions.keys() if name not in all_called_functions and not name.startswith('__')]

        # Update per-file stats with cross-file context
        for rel_path, stat in file_stats.items():
            stat['dead_functions'] = [f for f in stat['functions'] if f in dead_functions]
            file_dupes_count = sum(1 for f in stat['functions'] if f in duplicate_functions)
            stat['health'] = self._calculate_health(stat, file_dupes_count)

        summary: ProjectSummary = {
            'total_files': len(file_results),
            'total_functions': total_functions_count,
            'total_todos': total_todos,
            'duplicate_functions': duplicate_functions,
            'dead_functions': dead_functions,
            'worst_file': worst_file,
            'scan_timestamp': ""  # Set during reporting
        }

        return file_stats, summary