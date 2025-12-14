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
    
    def __str__(self):
        return f"Scope<{self.name}> Symbols: {list(self.symbols)}"

class MySemanticVisitor(PythonParserVisitor):
    def __init__(self):
        self.current_scope = Scope("Global")
        # Tambahkan built-in agar tidak dianggap error
        self.current_scope.symbols.update(['print', 'range', 'len', 'int', 'str', 'list', 'input'])

    # -------------------------------------------------------------------------
    # PERBAIKAN: HANDLER UNTUK DEFINISI FUNGSI
    # -------------------------------------------------------------------------
   # -------------------------------------------------------------------------
    # PERBAIKAN FINAL: HANDLER FUNGSI (UNWRAPPER LOGIC)
    # -------------------------------------------------------------------------
    def visitFunction_def(self, ctx):
        # 1. UNWRAPPER: Cek apakah node ini hanya pembungkus?
        # Jika anak pertamanya adalah 'Function_def_raw', kita pakai itu sebagai konteks utama
        actual_ctx = ctx
        if ctx.getChildCount() == 1:
            first_child = ctx.getChild(0)
            # Cek nama tipe class child tersebut
            if 'Function_def_raw' in type(first_child).__name__:
                actual_ctx = first_child

        # 2. AMBIL NAMA FUNGSI DARI CONTEXT ASLI
        func_name = "UnknownFunction"
        
        # Coba ambil token NAME/name dari actual_ctx
        if hasattr(actual_ctx, 'NAME') and actual_ctx.NAME():
            func_name = actual_ctx.NAME().getText()
        elif hasattr(actual_ctx, 'name') and actual_ctx.name():
            func_name = actual_ctx.name().getText()
        else:
            # Fallback: Biasanya token ke-2 adalah nama (index 1), setelah 'def' (index 0)
            # Kita pastikan jumlah anak cukup
            if actual_ctx.getChildCount() > 1:
                candidate = actual_ctx.getChild(1).getText()
                if candidate != '(': 
                    func_name = candidate

        print(f"\n[INFO] Menemukan Definisi Fungsi: '{func_name}'")
        
        # 3. SETUP SCOPE
        self.current_scope.define(func_name)
        parent_scope = self.current_scope
        self.current_scope = Scope(func_name, parent=parent_scope)

        # 4. AMBIL PARAMETER (Logic Text - Terbukti Berhasil)
        full_text = actual_ctx.getText()
        start_idx = full_text.find('(')
        end_idx = full_text.find(')')
        
        if start_idx != -1 and end_idx != -1:
            params_str = full_text[start_idx+1 : end_idx]
            if params_str.strip():
                # Split koma, tapi hati-hati dengan struktur kompleks
                # Untuk semantic check sederhana, split text cukup aman
                for p in params_str.split(','):
                    # Bersihkan: "a:int=10" -> ambil "a"
                    p_name = p.split('=')[0].split(':')[0].strip()
                    if p_name and p_name != 'self':
                        self.current_scope.define(p_name)
                        # print(f"  [ACTION] Parameter: {p_name}")

        # 5. KUNJUNGI ISI FUNGSI (BODY)
        # Kita harus mengunjungi anak-anak dari actual_ctx (si raw context)
        child_count = actual_ctx.getChildCount()
        for i in range(child_count):
            child = actual_ctx.getChild(i)
            txt = child.getText()
            # Skip token nama fungsi, def, tanda baca, agar tidak dianggap variabel
            if txt not in [func_name, 'def', ':', '(', ')', '->']:
                self.visit(child)

        self.current_scope = parent_scope
        return None

    # -------------------------------------------------------------------------
    # HANDLER UNTUK ASSIGNMENT (Variabel)
    # -------------------------------------------------------------------------
    def visitExpr_stmt(self, ctx):
        # Di Python3.g4, assignment seringkali masuk ke rule 'expr_stmt' atau 'assignment'
        # Struktur: testlist_star_expr ('=' testlist_star_expr)*
        
        # Cek apakah ini operasi assignment (ada tanda '=')
        # Tapi bukan '==' (comparison)
        children = list(ctx.getChildren())
        if len(children) > 1 and children[1].getText() == '=':
            # Ini Assignment: LHS = RHS
            lhs_node = children[0]
            rhs_node = children[2] # Simpelnya, ambil setelah '='
            
            # 1. Analisis Sisi Kiri (Definisi)
            # Ambil teks mentah untuk mendapatkan nama variabel
            var_name = lhs_node.getText()
            
            # Validasi sederhana (hindari a[0] atau a.b dianggap variabel baru)
            if '[' not in var_name and '.' not in var_name and '(' not in var_name:
                self.current_scope.define(var_name)
                # print(f"  [ACTION] Mendefinisikan Variabel: {var_name}")
            
            # 2. Analisis Sisi Kanan (Penggunaan)
            # Kita HARUS visit sisi kanan untuk mengecek apakah variabel yg dipakai sudah ada
            self.visit(rhs_node)
            
            # KITA TIDAK MEMANGGIL self.visit(lhs_node) 
            # Agar 'visitName' tidak protes bahwa variabel kiri belum ada.
            return None
            
        return self.visitChildren(ctx)

    # -------------------------------------------------------------------------
    # HANDLER UNTUK PENGGUNAAN VARIABEL (NAME)
    # -------------------------------------------------------------------------
   # -------------------------------------------------------------------------
    # PERBAIKAN: HANDLER UNTUK PENGGUNAAN VARIABEL (NAME)
    # -------------------------------------------------------------------------
    def visitAtom(self, ctx):
        # Ambil teks mentah dari node atom ini
        # Bisa berisi: nama variabel ("x"), angka ("10"), string ("'hello'"), atau keyword ("None")
        token_text = ctx.getText()

        # Kita perlu memfilter: Hanya proses jika ini terlihat seperti NAMA VARIABEL.
        # Kriteria Nama Variabel:
        # 1. Valid identifier (huruf/underscore, tidak diawali angka)
        # 2. Bukan angka, bukan string dengan kutip
        # 3. Bukan keyword bawaan Python (True, False, None)
        
        ignored_keywords = ['None', 'True', 'False', 'self', 'print', 'range', 'int', 'str', 'len']
        
        # Cek apakah ini identifier yang valid dan bukan keyword
        if token_text.isidentifier() and token_text not in ignored_keywords:
            
            # Cek apakah variabel sudah ada di scope?
            if not self.current_scope.resolve(token_text):
                print(f"  ❌ [ERROR] Semantic Error: Variabel '{token_text}' digunakan tapi belum didefinisikan!")
                print(f"     (Posisi Scope: {self.current_scope.name})")

        return self.visitChildren(ctx)