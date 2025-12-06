import sys
import json
from antlr4 import *
from PythonLexer import PythonLexer
from PythonParser import PythonParser
from PythonParserListener import PythonParserListener
from MyListener2 import AdvancedLinterListener # Pastikan nama class sesuai

def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("Config tidak ditemukan, menggunakan default.")
        return {
            "max_function_lines": 20,
            "max_nesting_depth": 3,
            "max_arguments": 3,
            "max_cyclomatic_complexity": 5
        }

def main():
    # 1. Load Konfigurasi
    config = load_config()
    print(f"🔍 Memulai PyCleanLint dengan konfigurasi: {config}\n")

    input_filename = "test_code.py"
    input_stream = FileStream(input_filename)

    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)
    
    tree = parser.file_input()

    # 2. Gunakan Listener Baru dengan Config
    listener = AdvancedLinterListener(config)
    walker = ParseTreeWalker()
    
    print("--- HASIL ANALISIS ---")
    walker.walk(listener, tree)
    print("----------------------")

if __name__ == '__main__':
    main()