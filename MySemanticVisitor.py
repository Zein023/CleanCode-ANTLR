from PythonParserVisitor import PythonParserVisitor
from PythonParser import PythonParser
import re

class Scope:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.symbols = set()

    def define(self, name):
        self.symbols.add(name)

    def resolve(self, name):
        if name in self.symbols: return True
        if self.parent: return self.parent.resolve(name)
        return False

class MySemanticVisitor(PythonParserVisitor):
    def __init__(self):
        self.current_scope = Scope("Global")
        self.builtins = {'list', 'dict', 'str', 'int', 'len', 'print', 'range', 'input', 'set', 'id', 'type'}
        self.current_scope.symbols.update(self.builtins)

    # =========================================================================
    # 1. HELPER: DEFINER (PENCARI NAMA REKURSIF)
    # Fungsi ini bertugas mencari semua variabel dalam sebuah node
    # dan MENDIFINISIKANNYA ke dalam scope (tanpa cek error).
    # =========================================================================
    def define_variables_in_node(self, ctx):
        # Jika node ini adalah 'name' (identifier), masukkan ke scope
        # Di grammar Anda, rule untuk nama variabel adalah 'name'
        if isinstance(ctx, PythonParser.NameContext):
            var_name = ctx.getText()
            
            # Cek Shadowing
            if var_name in self.builtins:
                print(f"  ⚠️ [CLEAN CODE] Shadowing: Variabel '{var_name}' menimpa fungsi bawaan!")
            
            self.current_scope.define(var_name)
            # print(f"  [ACTION] Definisi Variabel: {var_name}")
            return

        # Jika bukan 'name', cari terus ke anak-anaknya (Recursive)
        if hasattr(ctx, 'getChildCount'):
            for i in range(ctx.getChildCount()):
                self.define_variables_in_node(ctx.getChild(i))

    # =========================================================================
    # 2. CORE LOGIC: HANDLER ASSIGNMENT (PENCEGATAN)
    # Ini menangani rule: "assignment" di grammar Anda
    # =========================================================================
    def visitAssignment(self, ctx):
        children = list(ctx.getChildren())
        
        # Cek apakah ini assignment standar dengan '='
        # (Grammar Anda juga support '+=', ':', dll, kita fokus ke '=' dulu)
        has_assign = False
        last_eq_index = -1
        
        for i, child in enumerate(children):
            if child.getText() == '=':
                has_assign = True
                last_eq_index = i
        
        # JIKA INI ADALAH ASSIGNMENT (a = 10 atau a = b = 10)
        if has_assign:
            # 1. PROSES SISI KIRI (LHS) -> DEFINISI
            # Semua node SEBELUM tanda '=' terakhir adalah target definisi
            for i in range(last_eq_index):
                child = children[i]
                if child.getText() == '=': continue
                
                # Panggil helper untuk mendefinisikan variabel di node ini
                # Kita TIDAK memanggil self.visit(child) agar visitName tidak dijalankan (bebas error)
                self.define_variables_in_node(child)
            
            # 2. PROSES SISI KANAN (RHS) -> PENGGUNAAN
            # Node SETELAH tanda '=' terakhir adalah value/ekspresi
            # Kita panggil self.visit() biasa agar pengecekan usage berjalan
            for i in range(last_eq_index + 1, len(children)):
                self.visit(children[i])
                
            return None # Stop default recursion (karena kita sudah handle manual)
            
        # Jika bukan assignment '=' (misal type hint a:int), biarkan default
        return self.visitChildren(ctx)

    # =========================================================================
    # 3. HANDLER PENGGUNAAN VARIABEL (NAME)
    # Di grammar Anda, rule spesifik untuk identifier adalah 'visitName'
    # =========================================================================
    def visitName(self, ctx):
        var_name = ctx.getText()
        ignored = list(self.builtins) + ['None', 'True', 'False', 'self', '...', 'pass', '_']
        
        if var_name not in ignored:
            # Cek apakah variabel sudah ada di scope
            if not self.current_scope.resolve(var_name):
                print(f"  ❌ [ERROR] Semantic Error: Variabel '{var_name}' digunakan tapi belum didefinisikan!")
                print(f"     (Posisi Scope: {self.current_scope.name})")
        
        return self.visitChildren(ctx)

    # =========================================================================
    # 4. HANDLER FUNGSI (SUDAH BENAR)
    # =========================================================================
    def visitFunction_def(self, ctx):
        # UNWRAPPER untuk Grammar Anda (function_def -> function_def_raw)
        actual_ctx = ctx
        if ctx.getChildCount() == 1: # function_def hanya membungkus function_def_raw
            actual_ctx = ctx.getChild(0)

        func_name = "Unknown"
        # Di grammar Anda: 'def' name ...
        # Kita cari child bertipe NameContext
        for i in range(actual_ctx.getChildCount()):
            child = actual_ctx.getChild(i)
            if isinstance(child, PythonParser.NameContext):
                func_name = child.getText()
                break
        
        print(f"\n[INFO] Fungsi: '{func_name}'")

        if func_name != "Unknown" and not re.match(r'^[a-z_][a-z0-9_]*$', func_name):
             print(f"  ⚠️ [CLEAN CODE] Bad Naming: Fungsi '{func_name}' harusnya snake_case!")

        self.current_scope.define(func_name)
        parent_scope = self.current_scope
        self.current_scope = Scope(func_name, parent=parent_scope)

        # PARAMETER HANDLING
        # Grammar: parameters -> slash_no_default ...
        # Kita ambil teks parameter secara brute force untuk kemudahan
        full_text = actual_ctx.getText()
        start_idx = full_text.find('(')
        end_idx = full_text.find(')')
        if start_idx != -1 and end_idx != -1:
            params_str = full_text[start_idx+1 : end_idx]
            if params_str.strip():
                # Split koma, abaikan struktur kompleks
                for p in params_str.split(','):
                    # Bersihkan: "a:int=10" -> ambil "a"
                    p_clean = p.split('=')[0].split(':')[0].strip()
                    # Bersihkan *args dan **kwargs
                    p_clean = p_clean.replace('*', '')
                    
                    if p_clean and p_clean != 'self':
                        if p_clean in self.builtins:
                            print(f"  ⚠️ [CLEAN CODE] Shadowing: Parameter '{p_clean}' menimpa fungsi bawaan!")
                        self.current_scope.define(p_clean)
        
        # BODY VISIT
        # Kunjungi anak-anak (kecuali nama fungsi agar tidak dianggap pemakaian)
        child_count = actual_ctx.getChildCount()
        for i in range(child_count):
            child = actual_ctx.getChild(i)
            # Jangan visit nama fungsi itu sendiri
            if child.getText() != func_name:
                 self.visit(child)

        self.current_scope = parent_scope
        return None