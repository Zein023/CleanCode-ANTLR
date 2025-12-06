# MyListener.py

from PythonParserListener import PythonParserListener
from PythonParser import PythonParser

# Tetapkan batas kedalaman maksimum yang kita inginkan
MAX_NESTING_DEPTH = 5

class FunctionListener(PythonParserListener):

    # --- BARU: Kita tambahkan __init__ untuk melacak kedalaman ---
    def __init__(self):
        self.current_depth = 0
        super().__init__()

    # --- BARU: Dipanggil saat MASUK ke blok (melihat INDENT) ---
    def enterBlock(self, ctx: PythonParser.BlockContext):
        self.current_depth += 1
        
        # Dapatkan baris tempat blok ini dimulai
        start_line = ctx.start.line
        
        # Cek apakah kedalaman ini melebihi batas "clean code" kita
        if self.current_depth > MAX_NESTING_DEPTH:
            print(f"🔥 PERINGATAN (Clean Code): Nesting terlalu dalam!")
            print(f"  > Kedalaman: {self.current_depth} (melebihi {MAX_NESTING_DEPTH})")
            print(f"  > Dimulai di baris: {start_line}")

    # --- BARU: Dipanggil saat KELUAR dari blok (melihat DEDENT) ---
    def exitBlock(self, ctx: PythonParser.BlockContext):
        self.current_depth -= 1


    # --- Metode lama (Fungsi) ---
    def exitFunction_def(self, ctx: PythonParser.Function_defContext):
        try:
            func_name = ctx.function_def_raw().name().getText()
            start_line = ctx.start.line
            stop_line = ctx.stop.line
            total_lines = stop_line - start_line + 1
            print(f"✅ Ditemukan fungsi: {func_name} (Baris {start_line}-{stop_line}, total {total_lines} baris)")
        except AttributeError:
            print("Melewatkan node function_def...")
            
    # --- Metode lama (Import) ---
    def enterImport_stmt(self, ctx: PythonParser.Import_stmtContext):
        input_stream = ctx.start.getInputStream()
        start_index = ctx.start.start
        stop_index = ctx.stop.stop
        import_line = input_stream.getText(start_index, stop_index)
        print(f"📦 Ditemukan import: {import_line}")
        
    # --- Metode lama (Assignment) ---
    def enterAssignment(self, ctx: PythonParser.AssignmentContext):
        try:
            var_name_list_ctx = ctx.star_targets() 
            var_name_texts = [target.getText() for target in var_name_list_ctx]
            var_name = ' = '.join(var_name_texts)
            
            value_ctx = ctx.star_expressions()
            if value_ctx is None:
                value_ctx = ctx.yield_expr()
            
            if value_ctx is None:
                raise AttributeError("Tidak dapat menemukan sisi kanan penetapan")
            
            var_value = value_ctx.getText()
            var_value_clean = ' '.join(var_value.split())
            print(f"📝 Ditemukan variabel: {var_name} = {var_value_clean}")
        except AttributeError:
            print("Melewatkan penetapan (mungkin sintaks kompleks)...")