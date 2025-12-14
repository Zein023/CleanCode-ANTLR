#!/usr/bin/env python3
"""Debug with statement parsing."""
import sys
import os

sys.path.insert(0, os.path.join(os.getcwd(), 'app', 'generated'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from PythonParserVisitor import PythonParserVisitor

class DebugVisitor(PythonParserVisitor):
    def visitWith_stmt(self, ctx):
        print(f"Found with_stmt: {ctx.getText()[:80]}")
        print(f"Number of children: {len(ctx.children)}")
        for i, child in enumerate(ctx.children):
            child_text = child.getText() if hasattr(child, 'getText') else str(child)
            child_type = child.__class__.__name__
            print(f"  Child {i}: {child_type} = {child_text[:50]}")
            
            # If this is a With_itemContext, show its children
            if child_type == 'With_itemContext':
                print(f"    With_item children:")
                for j, subchild in enumerate(child.children):
                    subchild_text = subchild.getText() if hasattr(subchild, 'getText') else str(subchild)
                    subchild_type = subchild.__class__.__name__
                    print(f"      [{j}] {subchild_type} = {subchild_text[:30]}")
        return self.visitChildren(ctx)

code = """import io
with io.StringIO() as buffer:
    buffer.write('test')
"""

input_stream = InputStream(code)
lexer = PythonLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = PythonParser(stream)
tree = parser.file_input()

print("Searching for with_stmt...")
visitor = DebugVisitor()
visitor.visit(tree)
