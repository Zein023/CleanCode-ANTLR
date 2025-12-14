#!/usr/bin/env python3
"""Debug what visitor methods are being called."""
import sys
from pathlib import Path

app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path / 'generated'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser

test_code = "import os as operating_system\nprint(operating_system)"

input_stream = InputStream(test_code)
lexer = PythonLexer(input_stream)
stream = CommonTokenStream(lexer)
parser = PythonParser(stream)
tree = parser.file_input()

def print_tree(ctx, indent=0):
    prefix = "  " * indent
    class_name = type(ctx).__name__
    text = ctx.getText()[:40] if hasattr(ctx, 'getText') else str(ctx)[:40]
    print(f"{prefix}{class_name}: {text}")
    
    if hasattr(ctx, 'children') and ctx.children:
        for child in ctx.children:
            if hasattr(child, 'getText'):
                print_tree(child, indent + 1)

print("Parse tree for: import os as operating_system")
print_tree(tree)
