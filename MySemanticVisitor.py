from PythonParserVisitor import PythonParserVisitor
from PythonParser import PythonParser

class Scope:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.symbols = set()

    def define(self, name):
        self.symbols.add(name)

    def resolve(self, name):
        if name in self.symbols:
            return True
        if self.parent:
            return self.parent.resolve(name)
        return False

class MySemanticVisitor(PythonParserVisitor):
    def __init__(self):
        self.current_scope = Scope("Global")
        # Tambahkan fungsi built-in python biar tidak dianggap error
        self.current_scope.symbols.update(['print', 'range', 'len', 'int', 'str'])

    # --- PERBAIKAN DI SINI ---
    def visitFunction_def(self, ctx):
        # GANTI ctx.name().getText() MENJADI ctx.NAME().getText()
        func_name = ctx.NAME().getText()
        
        print(f"\n[INFO] Menemukan Definisi Fungsi: '{func_name}'")
        
        self.current_scope.define(func_name)
        
        parent_scope = self.current_scope
        self.current_scope = Scope(func_name, parent=parent_scope)
        
        self.visitChildren(ctx)
        
        print(f"[DEBUG] Keluar Scope '{func_name}'. Vars: {self.current_scope.symbols}")
        self.current_scope = parent_scope
        return None

    def visitAssignment(self, ctx):
        full_text = ctx.getText() 
        if '=' in full_text:
            # Ambil sisi kiri "="
            # Hati-hati: ctx.children[0] bisa jadi list/tuple, kita ambil text-nya saja
            lhs_raw = ctx.children[0].getText()
            var_name = lhs_raw.strip()
            
            if '.' not in var_name and '[' not in var_name and '(' not in var_name:
                self.current_scope.define(var_name)
                # print(f"  [ACTION] Mendefinisikan: {var_name}")
        
        return self.visitChildren(ctx)

    def visitName(self, ctx):
        var_name = ctx.getText()
        
        # Saring keyword atau atribut
        if var_name not in ['print', 'range', 'self', 'None', 'True', 'False']:
            # Cek apakah variabel ada di scope?
            if not self.current_scope.resolve(var_name):
                # Kita perlu cek apakah ini node assignment (definisi) atau node usage (pemakaian)
                # Cara sederhana (tapi tidak sempurna): 
                # Jika dia tidak ada di scope, kita anggap error dulu,
                # KECUALI dia baru saja didefinisikan di visitAssignment (tapi visitName dipanggil recursive)
                
                # Untuk kode tes Anda, error 't' muncul di sini.
                print(f"  ❌ [ERROR] Semantic Error: Variabel '{var_name}' digunakan tapi belum didefinisikan!")
                print(f"     (Posisi Scope: {self.current_scope.name})")
        
        return self.visitChildren(ctx)
    
    def visitFunction_def(self, ctx):
        # Kemungkinan 1: Nama ada di dalam function_def_raw()
        if hasattr(ctx, 'function_def_raw'):
            raw_ctx = ctx.function_def_raw()
            # Cek apakah raw punya name() atau NAME()
            if hasattr(raw_ctx, 'name'):
                func_name = raw_ctx.name().getText()
            elif hasattr(raw_ctx, 'NAME'):
                func_name = raw_ctx.NAME().getText()
            else:
                # Fallback: ambil token ke-2 dari raw (setelah 'def')
                func_name = raw_ctx.children[1].getText()
        else:
            # Kemungkinan 2: Tidak ada raw, ambil langsung dari children
            # Biasanya urutannya: "def" "nama_fungsi" ...
            func_name = ctx.children[1].getText()

        print(f"\n[INFO] Menemukan Definisi Fungsi: '{func_name}'")
        
        # ... (kode scope sisanya sama) ...
        self.current_scope.define(func_name)
        parent_scope = self.current_scope
        self.current_scope = Scope(func_name, parent=parent_scope)
        self.visitChildren(ctx)
        self.current_scope = parent_scope
        return None