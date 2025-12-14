#!/usr/bin/env python3
"""Test semantic visitor with imports and external references."""
import sys
from pathlib import Path

app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path / 'generated'))
sys.path.insert(0, str(app_path / 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

test_code = """
import sys
import os as operating_system
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow

# These should NOT be flagged as undefined
print(sys.version)
print(operating_system.getcwd())
my_path = Path('.')

# This should NOT be flagged (external class)
window = QMainWindow()

# This SHOULD be flagged (truly undefined)
print(undefined_var)

def example():
    # Import inside function
    import json
    data = json.loads('{}')
    
    # This should be flagged
    print(not_defined)
"""

print("=" * 70)
print("Semantic Analysis: Imports and External References")
print("=" * 70 + "\n")

try:
    input_stream = InputStream(test_code)
    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    tree = parser.file_input()
    
    print("Test Code:")
    print(test_code)
    print("\n" + "=" * 70)
    print("Analysis Results:")
    print("=" * 70 + "\n")
    
    visitor = MySemanticVisitor()
    visitor.visit(tree)
    
    print("\n" + "=" * 70)
    print("Expected Errors:")
    print("  - undefined_var (global scope)")
    print("  - not_defined (example scope)")
    print("\nExpected NO errors for:")
    print("  - sys, operating_system, Path, QMainWindow (imported)")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
