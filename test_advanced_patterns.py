#!/usr/bin/env python3
"""Test comprehensions, with statements, and other advanced patterns."""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))
sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

test_code = """
# List comprehension
a = [i for i in range(5)]
print(a)
print(i)  # ERROR: i is undefined (comprehension scope)

# Dict comprehension
d = {k: v for k, v in [(1, 'a'), (2, 'b')]}
print(d)
print(k)  # ERROR: k is undefined (comprehension scope)
print(v)  # ERROR: v is undefined (comprehension scope)

# Set comprehension
s = {x for x in range(10)}
print(s)
print(x)  # ERROR: x is undefined (comprehension scope)

# Generator expression
gen = (num for num in range(100))
print(gen)
print(num)  # ERROR: num is undefined (generator scope)

# With statement
import io
with io.StringIO() as buffer:
    buffer.write('test')
    print(buffer)  # OK: buffer is defined

print(buffer)  # OK: buffer is still defined (Python 3 semantics)

# With statement with multiple contexts
with open('test.txt') as f1, open('other.txt') as f2:
    content = f1.read()
    other = f2.read()
    print(f1, f2)  # OK: both defined

print(f1)  # OK: f1 is still defined
print(f2)  # OK: f2 is still defined

# For loop (should work)
result = []
for line in result:
    print(line)  # OK: line is defined in loop scope

# Nested comprehensions
matrix = [[j for j in range(3)] for i in range(3)]
print(matrix)
print(i)  # ERROR: i is undefined
print(j)  # ERROR: j is undefined
"""

print("\n" + "=" * 80)
print("COMPREHENSIVE TEST: Comprehensions, With Statements, and More")
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
    print("SUMMARY")
    print("=" * 80)
    print("""
[OK] Patterns tested:
  1. List comprehensions: [i for i in range(5)]
  2. Dict comprehensions: {k: v for k, v in items}
  3. Set comprehensions: {x for x in range(10)}
  4. Generator expressions: (num for num in range(100))
  5. With statements: with open('file') as f:
  6. Multiple context managers: with a as x, b as y:
  7. Nested comprehensions: [[j for j in range(3)] for i in range(3)]

Key points:
  - Variables defined in comprehensions/generators are LOCAL to that scope
  - They should NOT be accessible outside the comprehension/generator
  - Variables defined in 'with' statements ARE accessible after the block (in Python semantics)
  - For loops define variables in their containing scope
""")
    print("=" * 80 + "\n")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
