from PythonParserVisitor import PythonParserVisitor
from PythonParser import PythonParser

# Class Scope sederhana untuk menyimpan variabel
class Scope:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.symbols = set()
    
    def define(self, var_name):
        self.symbols.add(var_name)
        
    def resolve(self, var_name):
        if var_name in self.symbols: return True
        if self.parent: return self.parent.resolve(var_name)
        return False

class MySemanticChecker(PythonParserVisitor):
    
    def __init__(self):
        self.current_scope = Scope("Global")

    # --- BAGIAN YANG DIPERBAIKI ---
    # Gunakan nama "visitFunction_def" sesuai generated file baris 169
    # Hapus type hint ctx:... agar tidak error import
    def visitFunction_def(self, ctx):
        # Ambil nama fungsi
        # Di grammar Python standar, biasanya ada rule 'name' atau token NAME
        # Kita coba ambil text dari child ke-1 (setelah 'def')
        func_name = ctx.name().getText()
        
        print(f"--- [INFO] Masuk Fungsi: {func_name} ---")
        self.current_scope.define(func_name) # Daftarkan fungsi ke scope luar
        
        # Masuk Scope Baru
        parent_scope = self.current_scope
        self.current_scope = Scope(func_name, parent=parent_scope)
        
        # Proses anak-anaknya (parameter & body)
        self.visitChildren(ctx)
        
        # Keluar Scope
        print(f"--- [INFO] Keluar Fungsi {func_name}. Vars: {self.current_scope.symbols}")
        self.current_scope = parent_scope

    # Handle Assignment (Variable Declaration)
    # Sesuai generated file baris 59: visitAssignment
    def visitAssignment(self, ctx):
        # Logika sederhana: ambil teks sisi kiri '='
        # Struktur assignment kompleks, ini penyederhanaan
        text = ctx.getText() 
        if '=' in text:
            var_name = text.split('=')[0].strip()
            # Filter nama aneh
            if '.' not in var_name and '[' not in var_name:
                self.current_scope.define(var_name)
                print(f"  -> Definisi Variabel: {var_name}")
        
        return self.visitChildren(ctx)

    # Handle Penggunaan Variabel
    # Sesuai generated file baris 720: visitName
    def visitName(self, ctx):
        var_name = ctx.getText()
        # Cek apakah variabel sudah didefinisikan?
        # Skip keyword/builtin sederhana
        if var_name not in ['print', 'range', 'self']:
            if not self.current_scope.resolve(var_name):
                print(f"  [WARNING] Variabel '{var_name}' dipakai tapi belum didefinisikan!")
        
        return self.visitChildren(ctx)