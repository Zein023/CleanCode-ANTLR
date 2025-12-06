import json
from antlr4 import *
from PythonParserListener import PythonParserListener
from PythonParser import PythonParser

class AdvancedLinterListener(PythonParserListener):
    
    def __init__(self, config):
        self.config = config
        
        # --- STATE MANAGEMENT ---
        self.python_builtins = {'list', 'str', 'int', 'dict', 'set', 'len', 'print', 'id', 'type'}
        self.scopes = [set(self.python_builtins)] 
        
        # Stack untuk metrik fungsi: {'name': 'foo', 'complexity': 1, 'start_line': 10}
        self.func_stack = []
        
        # Nesting Depth Counter
        self.current_depth = 0

    # --- HELPER METHODS ---
    
    def current_scope(self):
        return self.scopes[-1]
    
    def check_shadowing(self, name, line):
        # Cek apakah nama ada di scope mana pun SELAIN scope saat ini
        for i in range(len(self.scopes) - 1):
            if name in self.scopes[i]:
                print(f"⚠️ [Baris {line}] Variable Shadowing: '{name}' menimpa variabel di outer scope/built-in.")
                return
        self.current_scope().add(name)

    def check_snake_case(self, name, line, type_):
        if not name.islower() or "__" in name:
            if name.startswith("__") and name.endswith("__"): return
            print(f"⚠️ [Baris {line}] Naming: {type_} '{name}' harus snake_case.")

    # --- 1. SCOPE & FUNCTION MANAGEMENT ---
    
    # PERBAIKAN: Menggunakan 'enterFunction_def' (bukan enterFuncdef)
    def enterFunction_def(self, ctx: PythonParser.Function_defContext):
        self.scopes.append(set())
        
        # PERBAIKAN: Mengakses nama melalui 'function_def_raw' sesuai parse tree Anda
        try:
            func_name = ctx.function_def_raw().name().getText()
        except AttributeError:
            func_name = "unknown_function"

        line = ctx.start.line
        
        # Validasi Naming
        self.check_snake_case(func_name, line, "Fungsi")
        
        # Inisialisasi Metrik
        self.func_stack.append({
            'name': func_name,
            'complexity': 1, 
            'start_line': line
        })
        
        self.check_shadowing(func_name, line)

    # PERBAIKAN: Menggunakan 'exitFunction_def'
    def exitFunction_def(self, ctx: PythonParser.Function_defContext):
        if not self.func_stack: return

        func_data = self.func_stack.pop()
        
        # Validasi Panjang Fungsi
        stop_line = ctx.stop.line
        length = stop_line - func_data['start_line'] + 1
        
        if length > self.config.get('max_function_lines', 20):
            print(f"⚠️ [Baris {func_data['start_line']}] Panjang Fungsi: '{func_data['name']}' terlalu panjang ({length} baris). Max: {self.config.get('max_function_lines')}")

        # Validasi Kompleksitas
        if func_data['complexity'] > self.config.get('max_cyclomatic_complexity', 5):
             print(f"⚠️ [Baris {func_data['start_line']}] Kompleksitas: '{func_data['name']}' terlalu rumit (Score: {func_data['complexity']}). Max: {self.config.get('max_cyclomatic_complexity')}")

        self.scopes.pop()

    # --- 2. CYCLOMATIC COMPLEXITY RULES ---
    
    def increment_complexity(self):
        if self.func_stack:
            self.func_stack[-1]['complexity'] += 1

    # Rule nama di sini menebak standar umum Python3. 
    # Jika error, berarti nama rule di grammar Anda berbeda (misal: if_stmt vs if_statement)
    def enterIf_stmt(self, ctx): self.increment_complexity()
    def enterWhile_stmt(self, ctx): self.increment_complexity()
    def enterFor_stmt(self, ctx): self.increment_complexity()
    
    # PERBAIKAN: Grammar Anda mungkin menggunakan 'try_stmt' yang berisi 'except_block'
    # Kita coba tangkap clause except secara umum jika ada
    # Jika method ini error, bisa dihapus atau disesuaikan
    def enterExcept_block(self, ctx): self.increment_complexity() 

    # --- 3. NESTING DEPTH ---
    
    # PERBAIKAN: Menggunakan 'enterBlock' (bukan enterSuite)
    def enterBlock(self, ctx: PythonParser.BlockContext):
        self.current_depth += 1
        
        if self.current_depth > self.config.get('max_nesting_depth', 3):
            print(f"⚠️ [Baris {ctx.start.line}] Nesting Depth: Terlalu dalam ({self.current_depth}). Max: {self.config.get('max_nesting_depth')}")

    def exitBlock(self, ctx: PythonParser.BlockContext):
        self.current_depth -= 1

    # --- 4. ARGUMENT & PARAMETER ---
    
    # PERBAIKAN: Grammar Anda menggunakan 'parameters' -> 'param'
    def enterParameters(self, ctx: PythonParser.ParametersContext):
        # Menghitung jumlah parameter secara manual dengan iterasi anak
        # Ini lebih aman daripada menebak nama rule anak (tfpdef/param)
        param_count = 0
        
        # Kita iterasi semua children, jika child itu adalah param, kita hitung
        if ctx.children:
            for child in ctx.children:
                # Cek apakah text child tersebut terlihat seperti parameter (bukan koma/kurung)
                txt = child.getText()
                if txt not in [',', '(', ')', '*', '**'] and len(txt) > 0:
                     param_count += 1
                     self.check_shadowing(txt, ctx.start.line)

        # Karena logic diatas agak kasar (bisa menghitung tipe data), 
        # opsi paling aman adalah mengecek jumlah koma + 1 (jika tidak kosong)
        # Tapi untuk sekarang kita coba tangkap logic sederhananya.
        
        if param_count > self.config.get('max_arguments', 3):
             print(f"⚠️ [Baris {ctx.start.line}] Argumen: Terlalu banyak parameter (deteksi kasar: {param_count}). Max: {self.config.get('max_arguments')}")

    # --- 5. ASSIGNMENT CHECK ---
    
    def enterAssignment(self, ctx: PythonParser.AssignmentContext):
        # Menggunakan logika assignment yang sudah berhasil sebelumnya
        try:
            var_name_list_ctx = ctx.star_targets() 
            # Ambil target pertama saja untuk cek shadowing
            if var_name_list_ctx:
                first_target = var_name_list_ctx[0]
                var_name = first_target.getText()
                
                # Filter sederhana
                if var_name.isidentifier():
                    self.check_shadowing(var_name, ctx.start.line)
                    self.check_snake_case(var_name, ctx.start.line, "Variabel")
        except:
            pass