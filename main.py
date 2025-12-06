import sys
from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser

# 1. Impor ParseTreeWalker dan Listener kustom kita
from antlr4.tree.Tree import ParseTreeWalker
from MyListener import FunctionListener 

def main():
    input_filename = "test_code.py"
    print(f"Mencoba mem-parsing file: {input_filename}...")
    
    try:
        input_stream = FileStream(input_filename)
    except FileNotFoundError:
        print(f"Error: File '{input_filename}' tidak ditemukan.")
        return

    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    
    # 'file_input' masih menjadi aturan awal kita
    tree = parser.file_input()
    
    # --- Bagian yang Diubah ---
    
    # 2. Buat instance Listener kita
    listener = FunctionListener()
    
    # 3. Buat ParseTreeWalker standar
    walker = ParseTreeWalker()
    
    # 4. Perintahkan walker untuk "berjalan" di atas pohon
    #    dan memicu event di 'listener' kita
    walker.walk(listener, tree)
    
    # 5. Hapus atau beri komentar pada print(tree.toStringTree...)
    # print("\n--- Parse Tree (LISP Style) ---")
    # print(tree.toStringTree(recog=parser))
    
    print("\n--- Selesai ---")

if __name__ == '__main__':
    main()