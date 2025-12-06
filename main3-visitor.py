import sys
from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from MySemanticVisitor import MySemanticVisitor

def main():
    input_filename = "test_code.py" # Nama file yang ingin dites
    
    print(f"--- Membaca file: {input_filename} ---")

    try:
        # GANTI InputStream MENJADI FileStream
        # encoding='utf-8' penting agar bisa baca karakter khusus
        input_stream = FileStream(input_filename, encoding='utf-8')
        
        # 1. Lexer
        lexer = PythonLexer(input_stream)
        stream = CommonTokenStream(lexer)
        
        # 2. Parser
        parser = PythonParser(stream)
        tree = parser.file_input()
        
        # 3. Semantic Visitor
        print("--- HASIL PENGECEKAN SEMANTIK ---")
        visitor = MySemanticVisitor()
        visitor.visit(tree)
        
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' tidak ditemukan!")

if __name__ == '__main__':
    main()