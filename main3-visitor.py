import sys
from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
# Pastikan file visitor perbaikan sebelumnya disimpan dengan nama MySemanticVisitor.py
from MySemanticVisitor import MySemanticVisitor 

def main():
    # Nama file yang akan dianalisis
    input_filename = "test_code.py"
    
    print(f"{'='*40}")
    print(f"SEMANTIC ANALYZER: {input_filename}")
    print(f"{'='*40}")

    try:
        # 1. Membaca File (Cara Aman untuk ANTLR v4.13+)
        # Kita baca manual pakai open(), lalu masukkan ke InputStream
        with open(input_filename, "r", encoding='utf-8') as f:
            file_content = f.read()
            input_stream = InputStream(file_content)

        # 2. Lexer Analysis
        lexer = PythonLexer(input_stream)
        stream = CommonTokenStream(lexer)

        # 3. Parser Analysis
        parser = PythonParser(stream)
        
        # 'file_input' adalah start rule standar untuk grammar Python3
        # Jika error "AttributeError", cek nama rule paling atas di file .g4 Anda
        tree = parser.file_input()

        # 4. Semantic Visitor Execution
        print("\n[STEP 1] Memulai Penelusuran Pohon (Tree Walk)...\n")
        visitor = MySemanticVisitor()
        visitor.visit(tree)

        print("\n" + "="*40)
        print("ANALISIS SELESAI")
        print("Jika tidak ada pesan [ERROR], berarti kode aman secara semantik dasar.")
        print("="*40)

    except FileNotFoundError:
        print(f"FATAL ERROR: File '{input_filename}' tidak ditemukan.")
    except Exception as e:
        print(f"TERJADI ERROR SISTEM: {e}")

if __name__ == '__main__':
    main()