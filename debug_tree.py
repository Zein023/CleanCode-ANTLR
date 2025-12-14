#!/usr/bin/env python3
"""
Debug the parse tree structure for function definitions.
"""
import sys
from pathlib import Path

app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path / 'generated'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser

def print_tree(ctx, indent=0):
    """Recursively print parse tree."""
    prefix = "  " * indent
    if hasattr(ctx, 'getText'):
        text = ctx.getText()[:50]  # Limit text length
    else:
        text = str(ctx)[:50]
    
    class_name = type(ctx).__name__
    print(f"{prefix}{class_name}: {text}")
    
    if hasattr(ctx, 'children') and ctx.children:
        for child in ctx.children:
            if hasattr(child, 'getText'):
                print_tree(child, indent + 1)

test_code = """
def main():
    a = 10
"""

input_stream = InputStream(test_code)
lexer = PythonLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = PythonParser(stream)
tree = parser.file_input()

print("Parse Tree Structure:")
print_tree(tree)
