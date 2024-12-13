from typing import Dict, Any, List
import ast
import os
from pathlib import Path

def analyze_code_structure(code: str) -> Dict[str, Any]:
    """Analyze code structure using AST.
    
    Args:
        code (str): Source code to analyze
        
    Returns:
        Dict[str, Any]: Analysis results
    """
    try:
        tree = ast.parse(code)
        return {
            'imports': _extract_imports(tree),
            'functions': _extract_functions(tree),
            'classes': _extract_classes(tree),
            'complexity': _calculate_complexity(tree)
        }
    except SyntaxError:
        return {}

def _extract_imports(tree: ast.AST) -> List[str]:
    """Extract import statements from AST."""
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for name in node.names:
                imports.append(name.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for name in node.names:
                imports.append(f'{module}.{name.name}')
    return imports

def _extract_functions(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract function definitions from AST."""
    functions = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append({
                'name': node.name,
                'args': [arg.arg for arg in node.args.args],
                'decorators': [ast.unparse(d) for d in node.decorator_list],
                'complexity': _calculate_complexity(node)
            })
    return functions

def _extract_classes(tree: ast.AST) -> List[Dict[str, Any]]:
    """Extract class definitions from AST."""
    classes = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            classes.append({
                'name': node.name,
                'bases': [ast.unparse(base) for base in node.bases],
                'methods': _extract_functions(node),
                'complexity': _calculate_complexity(node)
            })
    return classes

def _calculate_complexity(node: ast.AST) -> int:
    """Calculate cyclomatic complexity of AST node."""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler,
                            ast.With, ast.Assert, ast.Raise)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

def safe_write_file(path: str, content: str) -> bool:
    """Safely write content to file.
    
    Args:
        path (str): File path
        content (str): Content to write
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            f.write(content)
        return True
    except Exception:
        return False

def load_file_safely(path: str) -> str:
    """Safely load file content.
    
    Args:
        path (str): File path
        
    Returns:
        str: File content or empty string if error
    """
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception:
        return ""
