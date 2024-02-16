import os
import sys
import ctypes
import urllib.request
import zipfile
import requests
import shutil
import subprocess
from tqdm import tqdm
from colorama import Fore, Style, init

# Inisialisasi colorama untuk ANSI escape sequences (warna console)
init()

required_files = {
    "cublas64_11.dll",
    "cublasLt64_11.dll",
    "cudnn64_8.dll",
    "cudnn_adv_infer64_8.dll",
    "cudnn_adv_train64_8.dll",
    "cudnn_cnn_infer64_8.dll",
    "cudnn_cnn_train64_8.dll",
    "cudnn_ops_infer64_8.dll",
    "cudnn_ops_train64_8.dll",
    "cufft64_10.dll",
    "ffi.dll",
    "glib-2.0-0.dll",
    "gmodule-2.0-0.dll",
    "gobject-2.0-0.dll",
    "gstapp-1.0-0.dll",
    "gstaudio-1.0-0.dll",
    "gstbase-1.0-0.dll",
    "gstpbutils-1.0-0.dll",
    "gstreamer-1.0-0.dll",
    "gstriff-1.0-0.dll",
    "gsttag-1.0-0.dll",
    "gstvideo-1.0-0.dll",
    "hdf5.dll",
    "intl.dll",
    "nppc64_11.dll",
    "nppial64_11.dll",
    "nppicc64_11.dll",
    "nppidei64_11.dll",
    "nppif64_11.dll",
    "nppig64_11.dll",
    "nppim64_11.dll",
    "nppist64_11.dll",
    "nppitc64_11.dll",
    "pcre.dll",
    "zlib.dll",
    "zlibwapi.dll",
    "add_to_path.bat"
}

required_files2 = {
    "free.exe",
    "config.txt"
}

# Fungsi-fungsi yang sudah ada
def get_application_path():
    if getattr(sys, 'frozen', False):
        # Jika aplikasi dijalankan sebagai file tunggal (PyInstaller atau Nuitka),
        # bootloader PyInstaller atau Nuitka menambahkan flag frozen=True pada modul sys
        # dan menetapkan jalur aplikasi ke variabel _MEIPASS.
        return sys._MEIPASS
    else:
        # Jika tidak dijalankan sebagai file tunggal, gunakan jalur direktori skrip.
        return os.path.dirname(os.path.abspath(__file__))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def run_as_admin():
    if is_admin():
        return True

    print(Fore.RED + "Please run the program as an administrator." + Style.RESET_ALL)

    # Jika tidak ada hak administrator, jalankan ulang dengan hak administrator
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    
    # Tambahkan input untuk memberikan kesempatan membaca pesan sebelum menutup program
    input("Press Enter to exit...")
    sys.exit()

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def add_folder_to_local_path():
    try:
        # Get the folder path
        folder_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")

        # Execute the batch file to update the local PATH
        batch_file_path = os.path.join(folder_path, "add_to_path.bat")
        if os.path.isfile(batch_file_path):
            subprocess.run([batch_file_path], shell=True)
            print(f"Folder Added to path , executed successfully.")
        else:
            print(f"Error: Batch file not found in the specified folder.")
    except Exception as e:
        print(f"Error executing batch file: {e}")


def remove_file(file_path):
    try:
        os.remove(file_path)
        print(Fore.YELLOW + f"Removed existing file: {file_path}" + Style.RESET_ALL)
    except Exception as e:
        print(Fore.RED + f"Error removing file {file_path}: {e}" + Style.RESET_ALL)

# Modifikasi fungsi download_file
def download_file(url, destination_folder):
    try:
        file_name = url.split("/")[-1]
        file_path = os.path.abspath(os.path.join(destination_folder, file_name))

        # Mendownload file yang belum ada
        print(Fore.CYAN + f"Downloading {file_name}..." + Style.RESET_ALL)
        with urllib.request.urlopen(url) as response, open(file_path, 'wb') as out_file:
            total_size = int(response.headers['Content-Length'])
            pbar = tqdm(total=total_size, unit='B', unit_scale=True, bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} {postfix}')
            while True:
                data = response.read(8192)
                if not data:
                    break
                out_file.write(data)
                pbar.update(len(data))
            pbar.close()

        print(Fore.GREEN + f"Download complete: {file_name}" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(Fore.RED + f"Error downloading {url}: {e}" + Style.RESET_ALL)
        return False

def download_missing_files(files, destination_folder):
    base_url = "https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release/"
    for file_name in files:
        file_url = f"{base_url}{file_name}"
        download_file(file_url, destination_folder)

def check_and_setup_environment():
    # Bersihkan layar console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Cek dan buat folder cuda_cudnn jika belum ada
    cuda_cudnn_folder = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")
    create_folder_if_not_exists(cuda_cudnn_folder)

    # Cek apakah required files ada di dalam c:/cuda_cudnn
    print(Fore.YELLOW + "Checking Files..." + Style.RESET_ALL)

    existing_files = {file for file in required_files if os.path.isfile(os.path.join(cuda_cudnn_folder, file))}

    if existing_files != required_files:
        print(Fore.RED + "Some required files are missing. Downloading..." + Style.RESET_ALL)

        # Jika required files kurang dari 10, download satu per satu
        if len(required_files - existing_files) >= 10:
            print(Fore.CYAN + "Downloading and extracting the entire package..." + Style.RESET_ALL)

            # URL file ZIP yang akan diunduh
            zip_url = "https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release/cuda_cudnn.zip"

            # Hapus cuda_cudnn.zip jika sudah ada
            zip_path = os.path.join(cuda_cudnn_folder, "cuda_cudnn.zip")
            # Panggil fungsi untuk mendownload dan mengekstrak
            if download_file(zip_url, cuda_cudnn_folder):  
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(cuda_cudnn_folder)
                
                if os.path.isfile(zip_path):
                    remove_file(zip_path)
        else:
            print(Fore.CYAN + "Downloading and extracting missing files one by one..." + Style.RESET_ALL)
            missing_files = {file for file in required_files if file not in existing_files}
            download_missing_files(missing_files, cuda_cudnn_folder)

    else:
        print(Fore.GREEN + "All required files are present." + Style.RESET_ALL)

    # Tambahkan folder ke dalam PATH
    add_folder_to_local_path()

def check_and_setup_environment2():
    # Dapatkan jalur aplikasi dengan benar menggunakan sys.argv[0]
    app_path = os.path.abspath(os.path.dirname(sys.argv[0]))

    # Cek apakah free.exe ada di dalam folder aplikasi
    free_exe_path = os.path.join(app_path, "free.exe")

    if os.path.exists(free_exe_path):
        print(Fore.GREEN + "moji-aim is present. Not downloading moji.zip." + Style.RESET_ALL)
    else:
        print(Fore.RED + "moji-aim is missing. Downloading moji.zip and extracting all contents..." + Style.RESET_ALL)

        # Download moji.zip
        moji_zip_url = "https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release-Fre/moji.zip"
        moji_zip_path = os.path.join(app_path, "moji.zip")

        if download_file(moji_zip_url, app_path):
            print(Fore.GREEN + "Download of moji.zip complete." + Style.RESET_ALL)
        else:
            print(Fore.RED + "Failed to download moji.zip. Exiting." + Style.RESET_ALL)
            sys.exit()

        # Extract all contents of moji.zip
        with zipfile.ZipFile(moji_zip_path, 'r') as zip_ref:
            zip_ref.extractall(app_path)

        # Remove moji.zip after extraction
        os.remove(moji_zip_path)

        print(Fore.GREEN + "Extraction complete." + Style.RESET_ALL)

def download_opencv_dll():
    print("Choose your Graphic Card Series For Download DLL:")
    print("1. RTX 3090 , RTX 3080 , RTX 3070 , RTX 3060 , RTX 3050")
    print("2. RTX 2080 , RTX 2070 , RTX 2060 , GTX 1660 , GTX 1650")
    print("3. GTX 1080 , GTX 1070 , GTX 1060, GTX 1050 , GT 1030, GT 1010")
    print(" ")

    choice = input("Enter your choice (1-3): ")

    print(" ")
    options = {
        "1": "RTX 3090 Ti, RTX 3090, RTX 3080 Ti, RTX 3080 12GB, RTX 3080, RTX 3070 Ti, RTX 3070, RTX 3060 Ti, RTX 3060, RTX 3050",
        "2": "RTX 2080 Ti, RTX 2080 Super, RTX 2080, RTX 2070 Super, RTX 2070, RTX 2060 Super, RTX 2060 12GB, RTX 2060, GTX 1660 Ti, GTX 1660 Super, GTX 1660, GTX 1650 Super, GTX 1650",
        "3": "GTX 1080 Ti, GTX 1080, GTX 1070 Ti, GTX 1070, GTX 1060, GTX 1050 Ti, GTX 1050, GT 1030, GT 1010"
    }

    if choice not in options:
        print("Invalid choice. Exiting.")
        sys.exit()

    print(f"You have selected Nvidia Series: {options[choice]}")

    zip_names = {
        "1": "opencv_world452_86.zip",
        "2": "opencv_world452_75.zip",
        "3": "opencv_world452_61.zip"
    }

    zip_name = zip_names[choice]

    # Download and extract opencv_world452.dll
    dll_url = f"https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release/{zip_name}"

    # Download opencv_world452.dll
    opencv_zip_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), zip_name))

    if download_file(dll_url, os.path.abspath(os.path.join(os.path.dirname(sys.argv[0])))):
        print(Fore.GREEN + f"Download of {dll_url} complete." + Style.RESET_ALL)
        
        # Extract opencv_world452.dll
        with zipfile.ZipFile(opencv_zip_path, 'r') as zip_ref:
            zip_ref.extractall(os.path.dirname(sys.argv[0]))

        # Remove opencv_world452.zip after extraction
        os.remove(opencv_zip_path)

        print(Fore.GREEN + "Extraction complete." + Style.RESET_ALL)
    else:
        print(Fore.RED + f"Failed to download {dll_url}. Exiting." + Style.RESET_ALL)
        sys.exit()

def main():
    print(Fore.YELLOW + "This program requires administrative privileges." + Style.RESET_ALL)

    # Meminta hak administrator
    run_as_admin()

    # Lanjutkan dengan operasi yang memerlukan hak administrator
    print(Fore.GREEN + "Running with administrative privileges." + Style.RESET_ALL)

    # Cek dan setup lingkungan
    check_and_setup_environment()

    # Lanjutkan dengan tugas utama Anda setelah setup
    print(Fore.GREEN + "Environment setup complete. Proceed with the next steps." + Style.RESET_ALL)
    # ...

    check_and_setup_environment2()

    opencv_dll_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "opencv_world452.dll"))

    free_exe_path = os.path.abspath(os.path.join(os.path.dirname(sys.argv[0]), "free.exe"))   

    if os.path.exists(opencv_dll_path):
        print(Fore.GREEN + "opencv_world452.dll is present." + Style.RESET_ALL)
    else:
        download_opencv_dll()

    # Lanjutkan dengan menjalankan free.exe
    free_exe_path = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "free.exe")

    if os.path.exists(free_exe_path):
        print(Fore.GREEN + "Running moji-aim..." + Style.RESET_ALL)
        subprocess.run([free_exe_path])
    else:
        print(Fore.RED + "Error: free.exe not found." + Style.RESET_ALL)

if __name__ == "__main__":
    main()
