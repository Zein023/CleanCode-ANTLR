#!/usr/bin/env python3
"""Debug for loop parsing."""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from PythonParserVisitor import PythonParserVisitor

class DebugVisitor(PythonParserVisitor):
    def visitFor_stmt(self, ctx):
        print(f"Found for_stmt: {ctx.getText()}")
        return self.visitChildren(ctx)

code = """result = []
for line in result:
    print(line)
"""

input_stream = InputStream(code)
lexer = PythonLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = PythonParser(stream)
tree = parser.file_input()

print("Searching for for_stmt...")
visitor = DebugVisitor()
visitor.visit(tree)
