"""
Linter Runner Module
Handles running both listener and semantic visitor linters on Python files
"""
import sys
import os
from pathlib import Path
from antlr4 import *

# Add parent directory to path to import generated modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'generated'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'linter'))

from generated.PythonLexer import PythonLexer
from generated.PythonParser import PythonParser
from antlr4.tree.Tree import ParseTreeWalker
from linter.MyListener import AdvancedCleanCodeListener
from linter.MySemanticVisitor import MySemanticVisitor

# Custom Error Listener to capture lexer/parser errors
from linter.error_listener import CollectingErrorListener

class LinterRunner:
    """Runs linter checks on Python files"""
    
    def __init__(self, config):
        """
        Initialize linter runner
        
        Args:
            config: Configuration dictionary for linter rules
        """
        self.config = config
    
    def find_python_files(self, path, exclude_patterns):
        """
        Recursively find all Python files in a directory
        
        Args:
            path: Path to file or directory
            exclude_patterns: List of patterns to exclude
            
        Returns:
            List of Path objects for Python files
        """
        path = Path(path)
        python_files = []
        
        if path.is_file():
            if path.suffix == '.py':
                # Check if file should be excluded
                if not self._should_exclude(path, exclude_patterns):
                    python_files.append(path)
        elif path.is_dir():
            # Recursively find all .py files
            for item in path.rglob('*.py'):
                if not self._should_exclude(item, exclude_patterns):
                    python_files.append(item)
        
        return python_files
    
    def _should_exclude(self, file_path, exclude_patterns):
        """
        Check if file should be excluded based on patterns
        
        Args:
            file_path: Path object to check
            exclude_patterns: List of patterns to exclude
            
        Returns:
            True if file should be excluded, False otherwise
        """
        # Convert to string for pattern matching
        path_str = str(file_path)
        
        # Check against each exclude pattern
        for pattern in exclude_patterns:
            # Simple pattern matching - check if pattern is in path
            if pattern in path_str:
                return True
        
        return False
    
    def lint_file(self, file_path, use_listener=True, use_semantic=True):
        """
        Run linter on a single file
        
        Args:
            file_path: Path to Python file to lint
            use_listener: Whether to use listener-based linter
            use_semantic: Whether to use semantic visitor linter
            
        Returns:
            Dictionary with results from both linters
        """
        results = {
            'file': str(file_path),
            'listener_violations': [],
            'semantic_output': [],
            'errors': []
        }
        
        try:
            # Parse the file
            input_stream = FileStream(str(file_path), encoding='utf-8')
            lexer = PythonLexer(input_stream)
            # Conditionally attach custom error listener to lexer
            lex_error_listener = None
            if self.config.get('parser_errors_enabled', True):
                lexer.removeErrorListeners()
                lex_error_listener = CollectingErrorListener()
                lexer.addErrorListener(lex_error_listener)
            stream = CommonTokenStream(lexer)
            parser = PythonParser(stream)
            
            # Conditionally attach custom error listener to parser
            parse_error_listener = None
            if self.config.get('parser_errors_enabled', True):
                parser.removeErrorListeners()
                parse_error_listener = CollectingErrorListener()
                parser.addErrorListener(parse_error_listener)
            
            # Parse the file
            tree = parser.file_input()
            
            # Run listener-based linter
            if use_listener:
                try:
                    listener = AdvancedCleanCodeListener(self.config)
                    walker = ParseTreeWalker()
                    walker.walk(listener, tree)
                    results['listener_violations'] = listener.violations
                except Exception as e:
                    results['errors'].append(f"Listener error: {str(e)}")
            
            # Run semantic visitor linter
            if use_semantic:
                try:
                    # Capture print output from semantic visitor
                    import io
                    from contextlib import redirect_stdout
                    
                    f = io.StringIO()
                    with redirect_stdout(f):
                        visitor = MySemanticVisitor()
                        visitor.visit(tree)
                    
                    semantic_output = f.getvalue()
                    if semantic_output:
                        results['semantic_output'] = semantic_output.strip().split('\n')
                except Exception as e:
                    results['errors'].append(f"Semantic visitor error: {str(e)}")
        
            # Merge any lexer/parser syntax errors collected
            if lex_error_listener and lex_error_listener.errors:
                results['errors'].extend([f"Lexer: {msg}" for msg in lex_error_listener.errors])
            if parse_error_listener and parse_error_listener.errors:
                results['errors'].extend([f"Parser: {msg}" for msg in parse_error_listener.errors])

        except Exception as e:
            results['errors'].append(f"Parse error: {str(e)}")
        
        return results
    
    def lint_files(self, file_paths, use_listener=True, use_semantic=True, progress_callback=None):
        """
        Run linter on multiple files
        
        Args:
            file_paths: List of file paths to lint
            use_listener: Whether to use listener-based linter
            use_semantic: Whether to use semantic visitor linter
            progress_callback: Optional callback function(current, total, filename)
            
        Returns:
            List of results dictionaries
        """
        all_results = []
        total = len(file_paths)
        
        for idx, file_path in enumerate(file_paths, 1):
            if progress_callback:
                progress_callback(idx, total, str(file_path))
            
            result = self.lint_file(file_path, use_listener, use_semantic)
            all_results.append(result)
        
        return all_results
    
    def format_results(self, results):
        """
        Format linter results as a readable string
        
        Args:
            results: List of results dictionaries
            
        Returns:
            Formatted string with all violations
        """
        output = []
        
        for result in results:
            file_path = result['file']
            has_issues = False
            
            # Check if there are any violations or errors
            if result['listener_violations'] or result['semantic_output'] or result['errors']:
                has_issues = True
                output.append(f"\n{'='*80}")
                output.append(f"File: {file_path}")
                output.append(f"{'='*80}\n")
            
            # Show listener violations
            if result['listener_violations']:
                output.append("--- Clean Code Violations (Listener) ---")
                for violation in result['listener_violations']:
                    output.append(violation)
                output.append("")
            
            # Show semantic analysis output
            if result['semantic_output']:
                output.append("--- Semantic Analysis (Visitor) ---")
                for line in result['semantic_output']:
                    if line.strip():  # Only show non-empty lines
                        output.append(line)
                output.append("")
            
            # Show errors
            if result['errors']:
                output.append("--- Errors ---")
                for error in result['errors']:
                    output.append(f"❌ {error}")
                output.append("")
        
        if not output:
            return "✅ No issues found! All files passed the linter checks."
        
        return '\n'.join(output)
