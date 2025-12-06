import sys
from antlr4 import *

# --- IMPORT FILE GENERATE ANTLR ---
# Pastikan nama file ini sesuai dengan yang ada di folder Anda
from PythonLexer import PythonLexer
from PythonParser import PythonParser

# --- IMPORT LISTENER KITA ---
# Asumsi nama file listener Anda adalah MyListener2.py
# dan nama class di dalamnya adalah AdvancedCleanCodeListener
try:
    from MyListener2 import AdvancedCleanCodeListener
except ImportError:
    print("❌ ERROR: File 'MyListener2.py' tidak ditemukan atau nama class salah.")
    print("Pastikan file listener Anda bernama MyListener2.py")
    sys.exit(1)

def main():
    # 1. Tentukan file yang akan dites
    input_file = "test_code.py"
    
    print(f"🔍 Membaca file: {input_file}")

    # 2. Setup Input Stream
    try:
        input_stream = FileStream(input_file, encoding='utf-8')
    except FileNotFoundError:
        print(f"❌ ERROR: File '{input_file}' tidak ditemukan.")
        return

    # 3. Setup Lexer & Parser
    lexer = PythonLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = PythonParser(stream)

    # (Opsional) Hapus error listener bawaan agar output console bersih
    # parser.removeErrorListeners() 

    # 4. Mulai Parsing (Membuat Pohon Sintaksis)
    # 'file_input' adalah rule awal (root) standar untuk Python
    # Jika grammar Anda menggunakan nama lain (misal 'root' atau 'program'), ubah di sini.
    try:
        tree = parser.file_input()
    except Exception as e:
        print(f"❌ ERROR saat Parsing: {e}")
        return

    # 5. Konfigurasi Rules Linter
    config = {
        'max_function_lines': 20,          # Batas panjang fungsi
        'max_nesting_depth': 3,            # Batas kedalaman if/for
        'max_arguments': 3,                # Batas jumlah parameter
        'max_cyclomatic_complexity': 5,    # Batas kerumitan logika
        'naming_convention': {
            'function': 'snake_case',      # calculate_value
            'class': 'PascalCase',         # MyClass
            'variable': 'snake_case'       # my_var
        }
    }

    # 6. Inisialisasi Listener dengan Config
    try:
        listener = AdvancedCleanCodeListener(config)
    except Exception as e:
        print(f"❌ ERROR Inisialisasi Listener: {e}")
        print("Pastikan __init__ di class AdvancedCleanCodeListener menerima parameter 'config'.")
        return

    # 7. Jalanlan Walker
    walker = ParseTreeWalker()
    print("🚀 Sedang menganalisis kode...")
    walker.walk(listener, tree)

    # 8. Tampilkan Hasil
    print("\n" + "="*30)
    print("   HASIL ANALISIS CODE   ")
    print("="*30)

    # Cek list 'violations' dari listener
    if hasattr(listener, 'violations'):
        if not listener.violations:
            print("✅ CLEAN CODE! Tidak ditemukan pelanggaran.")
        else:
            print(f"⚠️ Ditemukan {len(listener.violations)} pelanggaran:\n")
            for msg in listener.violations:
                print(msg)
    else:
        print("❌ ERROR: Listener tidak memiliki atribut 'violations'.")
        print("Pastikan Anda sudah menambahkan 'self.violations = []' di __init__ Listener.")

if __name__ == '__main__':
    main()