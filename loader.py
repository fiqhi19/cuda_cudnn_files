import os
import urllib.request
import zipfile
import shutil

def download_and_extract_zip(url, zip_filename, extract_folder, add_to_path=True):
    try:
        # Mendownload file ZIP
        urllib.request.urlretrieve(url, zip_filename)

        # Mengekstrak file ZIP
        with zipfile.ZipFile(zip_filename, 'r') as zip_ref:
            zip_ref.extractall(extract_folder)

        print(f"File ZIP berhasil diunduh dan diekstrak: {zip_filename}")

        # Menambahkan folder ke dalam path environment variables jika diizinkan
        if add_to_path:
            extracted_path = os.path.join(os.getcwd(), extract_folder)
            os.environ["PATH"] += os.pathsep + extracted_path
            print(f"Folder {extracted_path} ditambahkan ke dalam PATH.")
    except Exception as e:
        print(f"Terjadi kesalahan: {e}")

def main():
    # URL file ZIP yang akan diunduh
    zip_url = "URL_FILE_ZIP"

    # Nama file ZIP setelah diunduh
    zip_filename = "example.zip"

    # Nama folder tempat file ZIP diekstrak
    extract_folder = "example_folder"

    # Panggil fungsi untuk mendownload, mengekstrak, dan menambahkan folder ke dalam PATH
    download_and_extract_zip(zip_url, zip_filename, extract_folder)

    # Setelah proses selesai, jalankan program utama Anda atau tugas lainnya
    # ...

if __name__ == "__main__":
    main()