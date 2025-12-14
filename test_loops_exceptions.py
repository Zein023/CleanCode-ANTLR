#!/usr/bin/env python3
"""Test semantic visitor with for loops, except clauses, and line numbers."""
import sys
import os
from pathlib import Path

# Add app paths directly
sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))
sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

test_code = """
import sys

def process_data(items):
    # For loop - x should be defined
    for x in items:
        print(x)
        print(y)  # ERROR: y is undefined
    
    # Try-except - e should be defined
    try:
        result = 1 / 0
    except ZeroDivisionError as e:
        print(e)  # OK: e is defined
        print(undefined_error)  # ERROR: undefined_error is undefined
    
    # Tuple unpacking in for loop
    for a, b in [(1, 2), (3, 4)]:
        print(a, b)  # OK: a and b are defined
        print(c)  # ERROR: c is undefined
"""

print("=" * 70)
print("Semantic Analysis: For Loops, Exception Handling, and Line Numbers")
print("=" * 70 + "\n")

try:
    input_stream = InputStream(test_code)
    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    tree = parser.file_input()
    
    print("Test Code with Line Numbers:")
    print("-" * 70)
    for i, line in enumerate(test_code.split('\n'), 1):
        print(f"{i:3d} | {line}")
    print("-" * 70 + "\n")
    
    print("Analysis Results:")
    print("=" * 70 + "\n")
    
    visitor = MySemanticVisitor()
    visitor.visit(tree)
    
    print("\n" + "=" * 70)
    print("Expected Errors:")
    print("  - y (line 8) - used but never defined")
    print("  - undefined_error (line 14) - used but never defined")
    print("  - c (line 19) - used but never defined")
    print("\nExpected NO errors for:")
    print("  - x (line 7) - defined in for loop")
    print("  - e (line 12) - defined in except clause")
    print("  - a, b (line 16) - defined in for loop with tuple unpacking")
    print("=" * 70)
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
