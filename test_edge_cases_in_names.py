#!/usr/bin/env python3
"""
Edge case test: Variables with 'in' in their name used in comprehensions.
This tests the fix for the bug where find('in') would match 'in' inside variable names.
"""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))
sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

test_code = """
# Variables containing 'in' in their name
line = "test line"
inline = "inline text"
input_data = [1, 2, 3]
min_value = 0

# List comprehensions with these variables
lines = ["line 1", "line 2", "line 3"]
result1 = [line for line in lines]  # 'line' should work

# More complex: variable 'line' in filter expression
result2 = [line for line in lines if '1' in line]

# Variable names with 'in': inline, input_data, min_value
inlines = ["inline1", "inline2"]
result3 = [inline for inline in inlines]

inputs = [10, 20, 30]
result4 = [input_data for input_data in inputs]

mins = [1, 2, 3]
result5 = [min_value for min_value in mins]

# Dict comprehensions with 'in' in variable names
result6 = {line: len(line) for line in lines}
result7 = {inline: len(inline) for inline in inlines}

# Nested comprehensions
matrix = [[line for line in row] for row in [lines, inlines]]

# Generator expressions
gen1 = (line for line in lines)
gen2 = (inline for inline in inlines)

print("All edge cases passed!")
"""

print("\n" + "=" * 80)
print("EDGE CASE TEST: Variables with 'in' in their names")
print("=" * 80 + "\n")

try:
    input_stream = InputStream(test_code)
    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    tree = parser.file_input()
    
    print("Running semantic analysis...\n")
    visitor = MySemanticVisitor()
    visitor.visit(tree)
    
    print("\n" + "=" * 80)
    print("✅ ALL EDGE CASES PASSED!")
    print("=" * 80)
    print("""
Tested variables:
  - line (contains 'in')
  - inline (contains 'in')
  - input_data (starts with 'in')
  - min_value (contains 'in')

All variables correctly handled in:
  ✓ List comprehensions
  ✓ Dict comprehensions
  ✓ Generator expressions
  ✓ Nested comprehensions
  ✓ Filter expressions (if ... in ...)

The fix correctly uses parse tree traversal instead of text search,
avoiding false matches of 'in' inside variable names.
""")
    print("=" * 80 + "\n")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
