#!/usr/bin/env python3
"""Test the updated semantic visitor on test_code.py."""
import sys
from pathlib import Path

app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path / 'generated'))
sys.path.insert(0, str(app_path / 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

print("=" * 70)
print("Semantic Analysis: test_code.py (Original Test File)")
print("=" * 70 + "\n")

try:
    with open('test_code.py', 'r', encoding='utf-8') as f:
        code = f.read()
    
    input_stream = InputStream(code)
    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    tree = parser.file_input()
    
    print("Analysis Results:")
    print("=" * 70 + "\n")
    visitor = MySemanticVisitor()
    visitor.visit(tree)
    
    print("\n" + "=" * 70)
    print("Expected Errors:")
    print("  - faktor_kali (in proses_data)")
    print("  - z (in main)")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
