#!/usr/bin/env python3
"""Debug comprehension structure."""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from PythonParserVisitor import PythonParserVisitor

class DebugVisitor(PythonParserVisitor):
    def __init__(self):
        self.indent_level = 0
    
    def _print(self, msg):
        print("  " * self.indent_level + msg)
    
    def visitAtom(self, ctx):
        text = ctx.getText()
        if text and text[0] in '[{(':
            self._print(f"Found atom starting with '{text[0]}': {text[:30]}...")
            self.indent_level += 1
            print_children = True
            # Print children types
            for i, child in enumerate(ctx.children):
                child_type = child.__class__.__name__
                child_text = child.getText() if hasattr(child, 'getText') else str(child)
                self._print(f"Child {i}: {child_type} = {child_text[:50]}")
            self.indent_level -= 1
        
        return self.visitChildren(ctx)

code = "[i for i in range(5)]"

input_stream = InputStream(code)
lexer = PythonLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = PythonParser(stream)
tree = parser.file_input()

print(f"Code: {code}\n")
print("Parse tree:")
print(tree.toStringTree(recog=parser))

print("\n\nVisitor walk:")
visitor = DebugVisitor()
visitor.visit(tree)
