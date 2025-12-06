from antlr4 import *
# PENTING: Kita kembali mewarisi listener bawaan hasil generate
try:
    from PythonParserListener import PythonParserListener
except ImportError:
    # Fallback jika nama filenya berbeda (sesuaikan jika perlu)
    from PythonParser import Python3ParserListener as PythonParserListener

from PythonParser import PythonParser
import re

class AdvancedCleanCodeListener(PythonParserListener):

    def __init__(self, config):
        self.config = config
        self.violations = [] 
        self.scopes = [set()]
        self.func_stack = []
        self.current_depth = 0
        
        # Keyword yang diabaikan saat mencari nama variabel/fungsi
        self.keywords = {'def', 'class', 'return', 'if', 'elif', 'else', 'while', 'for', 'in', 'pass', 'break', 'continue', 'lambda', 'await', 'async'}

    # -------------------------------
    # HELPER: FLATTEN TREE TO TOKENS
    # (Logika "Senjata Pamungkas" agar data selalu ketemu)
    # -------------------------------
    def get_tokens(self, ctx):
        """
        Mengambil semua teks dari node dan anak-anaknya menjadi list flat.
        """
        tokens = []
        if not ctx.children: return tokens
        for child in ctx.children:
            if hasattr(child, 'getSymbol'): 
                tokens.append(child.getText())
            elif hasattr(child, 'children'):
                tokens.extend(self.get_tokens(child))
        return tokens

    def log(self, line, msg):
        # HANYA simpan ke list, JANGAN print di sini agar tidak double output
        self.violations.append(f"⚠️ [Baris {line}] {msg}")

    # -------------------------------
    # 1. FUNCTION DEFINITION
    # -------------------------------
    # Nama method ini HARUS sama persis dengan yang ada di PythonParserListener.py
    # Berdasarkan tracer Anda: rule 'function_def' -> enterFunction_def
    def enterFunction_def(self, ctx):
        tokens = self.get_tokens(ctx)
        func_name = "unknown"
        
        # Cari kata setelah 'def'
        if 'def' in tokens:
            idx = tokens.index('def')
            if idx + 1 < len(tokens):
                func_name = tokens[idx + 1]

        line = ctx.start.line
        self.scopes.append(set())

        # Cek Snake Case
        if func_name != "unknown" and func_name not in self.keywords:
            if self.config['naming_convention']['function'] == 'snake_case':
                if not re.match(r"^[a-z_][a-z0-9_]*$", func_name):
                    self.log(line, f"Naming: Fungsi '{func_name}' harus snake_case.")

        # Simpan metrik
        self.func_stack.append({
            "name": func_name,
            "start_line": line,
            "complexity": 1
        })

    def exitFunction_def(self, ctx):
        if not self.func_stack: return
        func = self.func_stack.pop()
        self.scopes.pop()

        # Cek Panjang
        length = ctx.stop.line - func["start_line"] + 1
        if length > self.config.get('max_function_lines', 20):
             self.log(func['start_line'], f"Panjang: Fungsi '{func['name']}' ({length} baris) melebihi batas.")

        # Cek Kompleksitas
        if func["complexity"] > self.config.get('max_cyclomatic_complexity', 5):
             self.log(func['start_line'], f"Kompleksitas: Fungsi '{func['name']}' terlalu rumit (Score: {func['complexity']}).")

    # -------------------------------
    # 2. VARIABLE ASSIGNMENT
    # -------------------------------
    def enterAssignment(self, ctx):
        tokens = self.get_tokens(ctx)
        if not tokens: return
        
        # Asumsi token pertama adalah target variabel
        var_name = tokens[0]
        line = ctx.start.line

        # Filter: identifier valid & bukan keyword (seperti self)
        if re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", var_name) and var_name != 'self':
            
            # Cek Shadowing Built-in
            builtins = {'print', 'list', 'str', 'int', 'dict', 'set', 'len', 'range', 'type', 'id'}
            if var_name in builtins:
                self.log(line, f"Shadowing Built-in: Variable '{var_name}' merusak fungsi bawaan Python.")
            
            # Cek Naming (Snake Case)
            elif self.config['naming_convention']['variable'] == 'snake_case':
                 # Izinkan huruf besar semua (CONSTANT)
                 if not re.match(r"^[a-z_][a-z0-9_]*$", var_name) and not var_name.isupper():
                     self.log(line, f"Naming: Variable '{var_name}' harus snake_case.")

    # -------------------------------
    # 3. PARAMETERS
    # -------------------------------
    def enterParameters(self, ctx):
        # Ambil text mentah "(a,b,c)"
        raw = ctx.getText().replace("(", "").replace(")", "")
        if not raw.strip(): count = 0
        else: count = len(raw.split(','))

        if count > self.config.get('max_arguments', 3):
             self.log(ctx.start.line, f"Argumen: Terlalu banyak parameter ({count}).")

    # -------------------------------
    # 4. NESTING & COMPLEXITY
    # -------------------------------
    def increment_complexity(self):
        if self.func_stack: self.func_stack[-1]["complexity"] += 1

    # Override metode standar
    def enterIf_stmt(self, ctx): self.increment_complexity()
    def enterWhile_stmt(self, ctx): self.increment_complexity()
    def enterFor_stmt(self, ctx): self.increment_complexity()
    
    # Block handling (Nesting)
    # Nama method 'enterBlock' ini standar jika rule di grammar namanya 'block'
    def enterBlock(self, ctx):
        self.current_depth += 1
        if self.current_depth > self.config.get('max_nesting_depth', 3):
            self.log(ctx.start.line, f"Nesting: Terlalu dalam ({self.current_depth}).")

    def exitBlock(self, ctx):
        self.current_depth -= 1