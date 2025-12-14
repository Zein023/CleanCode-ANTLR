# test_code.py
from antlr4 import risky_operation, ErrorNode

# 1. Shadowing Built-in
list = [1, 2, 3] 

def fungsibersih(param1, param2, param3, param4): # 2. PascalCase & Too Many Args
    
    # 3. Shadowing Outer Scope
    list = "shadowing" 
    
    # 4. Deep Nesting
    if param1:
        if param2:
            if param3:
                if param4:
                    if param1:
                        if param2:
                            print("Too deep!")

def complex_logic(x):
    # 5. High Complexity (Score awal 1 + 5 if = 6)
    if x == 1: pass
    if x == 2: pass
    if x == 3: pass
    if x == 4: pass
    if x == 5: pass

# --- KASUS 1: Clean Code Warning (Shadowing Built-in Variable) ---
# Visitor harus mendeteksi bahwa 'list' dan 'str' adalah tipe data bawaan Python
list = [1, 2, 3]
str = "Jangan lakukan ini"

# --- KASUS 2: Clean Code Warning (Bad Naming Convention) ---
# Nama fungsi menggunakan PascalCase, seharusnya snake_case (hitung_gaji_karyawan)
# Visitor harus mendeteksi ini.
def HitungGajiKaryawan(nama, gaji_pokok, tunjangan, lembur, bonus):
    
    # --- KASUS 3: Clean Code Warning (Complexity / Too Many Params) ---
    # Fungsi di atas memiliki 5 parameter. Batas di visitor kita adalah 3.
    
    # --- KASUS 4: Clean Code Warning (Shadowing Built-in Parameter) ---
    # Bayangkan ada sub-fungsi di sini
    pass

def proses_data(id, type, input):
    # 'id', 'type', dan 'input' adalah fungsi bawaan Python.
    # Visitor harus memberi peringatan shadowing pada parameter ini.
    
    hasil = 100
    
    # --- KASUS 5: SEMANTIC ERROR (Undefined Variable) ---
    # Variabel 'faktor_kali' tidak pernah didefinisikan sebelumnya.
    # Ini adalah error fatal.
    total = hasil * faktor_kali
    
    return total

def main():
    a = 10
    b = 20
    
    # --- KASUS 6: SEMANTIC ERROR (Undefined Variable) ---
    # Variabel 'z' belum didefinisikan.
    print(a)
    print(b)
    print(z) 

def error_node():
    pass

def complexUndefinedVariables():
    res = [i + j for i in range(5)]
    res = [k for i in range(j for j in range(2))]

    lines = ["This is a test", "Another line here"]
    for line in lines:
        for word in line.split():
            print(word + unknown_var)
    
    try:
        value = int("not_a_number")
    except ValueError as e:
        print(e + extra_info)
    
    with open("non_existent_file.txt", "r") as f:
        content = f.read()
        print(content + file_suffix)

    try:
        error_node()
        risky_operation()
        ErrorNode()
    except NonExistentError as nee:
        print(nee + more_info)

# Panggil main
main()