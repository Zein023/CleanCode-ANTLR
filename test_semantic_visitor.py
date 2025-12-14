#!/usr/bin/env python3
"""
Quick test of the fixed semantic visitor against test_code.py
"""
import sys
from pathlib import Path

# Add app paths
app_path = Path(__file__).parent / 'app'
sys.path.insert(0, str(app_path / 'generated'))
sys.path.insert(0, str(app_path / 'linter'))

from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

def test_semantic_visitor():
    """Test the semantic visitor on a simple test case."""
    
    # Simple test code
    test_code = """
def main():
    a = 10
    b = 20
    print(a)
    print(b)
    print(z)
"""
    
    print("=" * 60)
    print("Testing Semantic Visitor (Fixed)")
    print("=" * 60)
    print("\nTest Code:")
    print(test_code)
    print("\n" + "=" * 60)
    print("Analysis:")
    print("=" * 60)
    
    try:
        # Parse
        input_stream = InputStream(test_code)
        lexer = PythonLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = PythonParser(stream)
        tree = parser.file_input()
        
        # Analyze
        visitor = MySemanticVisitor()
        visitor.visit(tree)
        
        print("\n" + "=" * 60)
        print("Expected Errors:")
        print("  - z should be flagged as undefined (it is not defined anywhere)")
        print("\nExpected NO Errors for:")
        print("  - a (defined as a = 10)")
        print("  - b (defined as b = 20)")
        print("=" * 60)
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_semantic_visitor()
