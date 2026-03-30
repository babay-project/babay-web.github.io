import zlib
import os
import sys
import subprocess
import platform
import json

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_bin_files():
    """Mencari semua file .bin di folder saat ini"""
    files = [f for f in os.listdir('.') if f.endswith('.bin') and not f.startswith('(BACKUP)') and not f.startswith('NEW_')]
    return files

def buka_editor(path_file):
    """Membuka text editor default sistem"""
    if platform.system() == 'Windows':
        os.startfile(path_file)
    elif platform.system() == 'Darwin':
        subprocess.call(('open', path_file))
    else:
        subprocess.call(('xdg-open', path_file))

def main():
    while True:
        clear_screen()
        print("==============================================")
        print("   ULTIMATE ZLIB EDITOR (AUTO SCAN & BACKUP)  ")
        print("==============================================")
        
        # 1. SCAN FILE
        bin_files = get_bin_files()
        
        if not bin_files:
            print("\n[!] Tidak ditemukan file .bin di folder ini.")
            print("Pastikan script ini satu folder dengan file game.")
            input("\nTekan Enter untuk keluar...")
            sys.exit()

        print("\nDaftar File yang Ditemukan:")
        for i, filename in enumerate(bin_files):
            print(f" [{i+1}] {filename}")
        print(" [0] Keluar")

        # 2. PILIH FILE
        try:
            pilihan = int(input("\nPilih nomor file yang mau diedit: "))
            if pilihan == 0:
                print("Dadah!")
                sys.exit()
            
            if 1 <= pilihan <= len(bin_files):
                target_file = bin_files[pilihan - 1]
                proses_file(target_file)
            else:
                print("[!] Pilihan tidak valid.")
                input("Tekan Enter untuk ulang...")
        except ValueError:
            print("[!] Masukkan angka saja.")
            input("Tekan Enter untuk ulang...")

def proses_file(filename):
    print(f"\n>> Memproses: {filename}...")
    
    # Variabel penting
    header_data = b""
    mode_alternatif = False
    temp_txt = filename + ".txt"
    backup_name = "(BACKUP) " + filename

    # --- TAHAP 1: BONGKAR ---
    try:
        with open(filename, "rb") as f:
            data_mentah = f.read()

        # Deteksi metode kompresi
        try:
            # Coba Zlib biasa
            data_bytes = zlib.decompress(data_mentah)
        except:
            # Coba skip 4 byte
            try:
                header_data = data_mentah[:4]
                data_bytes = zlib.decompress(data_mentah[4:])
                mode_alternatif = True
                print("   (Info: File menggunakan header 4-byte)")
            except:
                print("[!] Gagal membongkar. File mungkin terenkripsi khusus.")
                input("Tekan Enter kembali ke menu...")
                return

        # Format JSON (Pretty Print)
        try:
            json_str = data_bytes.decode('utf-8')
            json_obj = json.loads(json_str)
            content_final = json.dumps(json_obj, indent=4) # Rapi ke bawah
        except:
            print("[!] Peringatan: Isi file bukan JSON valid. Mode raw text.")
            content_final = data_bytes.decode('utf-8', errors='ignore')

        # Tulis ke TXT sementara
        with open(temp_txt, "w", encoding='utf-8') as f:
            f.write(content_final)

    except Exception as e:
        print(f"[!] Error saat membaca: {e}")
        input("Tekan Enter...")
        return

    # --- TAHAP 2: EDIT ---
    print(f">> Membuka editor untuk {temp_txt}...")
    buka_editor(temp_txt)
    
    print("\n" + "="*50)
    print(" SEDANG MODE EDITING...")
    print(f" 1. Silakan edit file di Notepad.")
    print(f" 2. SAVE file tersebut (Ctrl+S).")
    print(f" 3. Kembali ke sini tekan Enter untuk memproses.")
    print("="*50)
    
    # Loop validasi JSON agar tidak error saat dipacking
    data_siap_kompres = None
    while True:
        input(" >> Tekan Enter jika SUDAH SELESAI edit & save...")
        
        try:
            with open(temp_txt, "r", encoding='utf-8') as f:
                text_edit = f.read()
            
            # Coba Minify (cek error syntax)
            try:
                json_obj = json.loads(text_edit)
                # Minify (hilangkan spasi agar ukuran kecil)
                data_siap_kompres = json.dumps(json_obj, separators=(',', ':')).encode('utf-8')
                break # Jika sukses, keluar loop
            except json.JSONDecodeError as e:
                print(f"\n[!] ERROR JSON SYNTAX di baris {e.lineno}, kolom {e.colno}:")
                print(f"    {e.msg}")
                print(" >> Cek lagi editanmu! Mungkin kurang koma (,) atau kurung { }.")
                pilihan = input("    Ketik 'r' untuk reload ulang Notepad, atau 'x' batalkan: ").lower()
                if pilihan == 'x': return
                buka_editor(temp_txt)

        except Exception as e:
            # Jika bukan JSON, langsung pack raw
            data_siap_kompres = text_edit.encode('utf-8')
            break

    # --- TAHAP 3: BUNGKUS & REPLACE ---
    print("\n>> Sedang membungkus ulang...")
    try:
        # Kompresi
        data_kompres = zlib.compress(data_siap_kompres, level=9)
        
        # 1. Buat Backup File Asli
        if os.path.exists(backup_name):
            os.remove(backup_name) # Hapus backup lama jika ada
        os.rename(filename, backup_name)
        print(f"   [OK] File asli diamankan ke: {backup_name}")

        # 2. Tulis File Baru dengan Nama Asli
        with open(filename, "wb") as f_out:
            if mode_alternatif:
                f_out.write(header_data) # Balikin header
            f_out.write(data_kompres)
        
        print(f"   [SUKSES] File {filename} telah diperbarui!")
        
        # Bersihkan file sampah
        os.remove(temp_txt)
        
    except Exception as e:
        print(f"[!] Gagal menulis file: {e}")
        # Jika gagal, coba kembalikan backup
        if os.path.exists(backup_name) and not os.path.exists(filename):
            os.rename(backup_name, filename)

    input("\nSelesai. Tekan Enter untuk kembali ke menu...")

if __name__ == "__main__":
    main()