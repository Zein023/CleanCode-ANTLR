#!/usr/bin/env python3
"""Debug for loop parsing."""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))
sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

code = """result = []
for line in result:
    print(line)
"""

input_stream = InputStream(code)
lexer = PythonLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = PythonParser(stream)
tree = parser.file_input()

print("Testing for loop parsing...")
print(code)
print("="*50)

visitor = MySemanticVisitor()
visitor.visit(tree)

print("\n[OK] Test complete")
