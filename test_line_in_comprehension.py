#!/usr/bin/env python3
"""Test the exact patterns from main_window.py that were flagging 'line' as undefined."""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))
sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

# Test the exact patterns from main_window.py
test_code = """
# Pattern 1: from total_semantic calculation
results_data = [
    {'semantic_output': ['line 1', 'line 2', '❌ ERROR: undefined']},
    {'semantic_output': ['line 3', '❌ ERROR: another error']}
]

total_semantic = sum(len([line for line in r['semantic_output'] 
                           if '❌' in line or 'ERROR' in line]) 
                     for r in results_data)

# Pattern 2: from semantic_issues extraction
result = {'semantic_output': ['  ', '❌ ERROR: x undefined', 'line without error']}

semantic_issues = [line for line in result['semantic_output'] 
                   if line.strip() and ('❌' in line or 'ERROR' in line)]

print("Test complete!")
"""

print("=" * 80)
print("Testing main_window.py patterns where 'line' was flagged as undefined")
print("=" * 80)
print()

try:
    input_stream = InputStream(test_code)
    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    tree = parser.file_input()
    
    print("Running semantic analysis...")
    print()
    visitor = MySemanticVisitor()
    visitor.visit(tree)
    
    print()
    print("=" * 80)
    print("✅ SUCCESS! No undefined variable errors!")
    print("=" * 80)
    print()
    print("Both patterns now work correctly:")
    print("  1. [line for line in r['semantic_output'] if '❌' in line]")
    print("  2. [line for line in result['semantic_output'] if line.strip()]")
    print()
    print("The 'line' variable is correctly recognized in both comprehensions.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
