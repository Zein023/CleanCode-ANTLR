# 

# test_code.py

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

# Panggil main
main()