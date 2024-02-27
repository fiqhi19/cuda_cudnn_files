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
import datetime
import keyboard
import win32api
import win32con
import random
import psutil
import _thread
from ctypes import windll, Structure, byref

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
    "premium.exe",
    "config.txt"
}

def disable_console_mouse_input():
    kernel32 = ctypes.windll.kernel32
    kernel32.SetConsoleMode(kernel32.GetStdHandle(-10), 128)

def get_timestamp():
    now = datetime.datetime.now()
    return f"[ {now.strftime('%d/%m/%Y %H:%M')} ]"

def build_title(length) -> str:
    """Return a randomly generated window title to prevent detections."""
    chars = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
        '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '!', '@', '#',
        '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '/', '?'
    ]
    return ''.join(random.choice(chars) for character in range(length))

def set_window_title(title):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def restart():
    print('Please restart the loader.')
    input('Press Enter to exit...')
    sys.exit()

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
    restart()

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

def add_folder_to_local_path():
    timestamp = get_timestamp()
    try:
        # Get the folder path
        folder_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")

        # Execute the batch file to update the local PATH
        batch_file_path = os.path.join(folder_path, "add_to_path.bat")
        if os.path.isfile(batch_file_path):
            subprocess.run([batch_file_path], shell=True)
            print(timestamp + Fore.CYAN + "Folder Added to path , executed successfully." + Style.RESET_ALL)

            restart()
        else:
            print(timestamp + Fore.RED + "Error: Batch file not found in the specified folder." + Style.RESET_ALL)
    except Exception as e:
        print(timestamp + Fore.RED + "Error executing batch file:." + Style.RESET_ALL)

def remove_file(file_path):
    timestamp = get_timestamp()
    try:
        os.remove(file_path)
    except Exception as e:
        print(timestamp + Fore.RED + f"Error removing file {file_path}: {e}" + Style.RESET_ALL)

# Modifikasi fungsi download_file
def download_file(url, destination_folder):
    timestamp = get_timestamp()
    try:
        file_name = url.split("/")[-1]
        file_path = os.path.abspath(os.path.join(destination_folder, file_name))

        # Mendownload file yang belum ada
        print(timestamp + Fore.CYAN + f"Downloading {file_name}..." + Style.RESET_ALL)
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

        print(timestamp + Fore.GREEN + f"Download complete: {file_name}" + Style.RESET_ALL)
        return True
    except Exception as e:
        print(timestamp + Fore.RED + f"Error downloading {file_name}: {e}" + Style.RESET_ALL)
        return False

def download_missing_files(files, destination_folder):
    base_url = "https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release/"
    for file_name in files:
        file_url = f"{base_url}{file_name}"
        download_file(file_url, destination_folder)

def check_and_setup_environment():
    timestamp = get_timestamp()
    # Bersihkan layar console
    os.system('cls' if os.name == 'nt' else 'clear')

    # Cek dan buat folder cuda_cudnn jika belum ada
    cuda_cudnn_folder = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")
    create_folder_if_not_exists(cuda_cudnn_folder)

    # Cek apakah required files ada di dalam c:/cuda_cudnn
    print(timestamp + Fore.YELLOW + "Checking Files..." + Style.RESET_ALL)

    existing_files = {file for file in required_files if os.path.isfile(os.path.join(cuda_cudnn_folder, file))}

    if existing_files != required_files:
        print(timestamp + Fore.RED + "Some required files are missing. Downloading..." + Style.RESET_ALL)

        # Jika required files kurang dari 10, download satu per satu
        if len(required_files - existing_files) >= 10:
            print(timestamp + Fore.CYAN + "Downloading and extracting the entire package..." + Style.RESET_ALL)
            print(timestamp + Fore.RED + "Do not disturb download progress !!!" + Style.RESET_ALL)

            # URL file ZIP yang akan diunduh
            zip_url = "https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release/cuda_cudnn.zip"

            # Hapus cuda_cudnn.zip jika sudah ada
            zip_path = os.path.join(cuda_cudnn_folder, "cuda_cudnn.zip")
            # Panggil fungsi untuk mendownload dan mengekstrak
            if download_file(zip_url, cuda_cudnn_folder):  
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    print(timestamp + Fore.YELLOW + "extracting Files.." + Style.RESET_ALL)
                    zip_ref.extractall(cuda_cudnn_folder)

                if os.path.isfile(zip_path):
                    remove_file(zip_path)
                    add_folder_to_local_path()
        else:
            print(timestamp + Fore.CYAN + "Downloading and extracting missing files one by one..." + Style.RESET_ALL)
            missing_files = {file for file in required_files if file not in existing_files}
            download_missing_files(missing_files, cuda_cudnn_folder)
            add_folder_to_local_path()
    else:
        print(timestamp + Fore.GREEN + "All required files are present." + Style.RESET_ALL)


def check_and_setup_environment2():
    os.system('cls' if os.name == 'nt' else 'clear')
    timestamp = get_timestamp()
    # Dapatkan jalur aplikasi dengan benar menggunakan sys.argv[0]
    app_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")

    # Cek apakah premium.exe ada di dalam folder aplikasi
    premium_exe_path = os.path.join(app_path, "premium.exe")

    if os.path.exists(premium_exe_path):
        print(timestamp + Fore.GREEN + "moji-aim is present. Not downloading moji.zip." + Style.RESET_ALL)
    else:
        print(timestamp + Fore.RED + "moji-aim is missing. Downloading moji.zip and extracting all contents..." + Style.RESET_ALL)

        # Download moji.zip
        moji_zip_url = "https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release-Pre/moji.zip"
        moji_zip_path = os.path.join(app_path, "moji.zip")

        if download_file(moji_zip_url, app_path):
            print(timestamp + Fore.GREEN + "Download of moji.zip complete." + Style.RESET_ALL)
        else:
            print(timestamp + Fore.RED + "Failed to download moji.zip. Exiting." + Style.RESET_ALL)
            sys.exit()

        # Extract all contents of moji.zip
        with zipfile.ZipFile(moji_zip_path, 'r') as zip_ref:
            zip_ref.extractall(app_path)

        # Remove moji.zip after extraction
        os.remove(moji_zip_path)

        print(timestamp + Fore.GREEN + "Extraction complete." + Style.RESET_ALL)
        print(" ")

def download_opencv_dll():
    os.system('cls' if os.name == 'nt' else 'clear')
    timestamp = get_timestamp()
    folder_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")
    print(" ")
    print(" ")
    print("Choose your Graphic Card Series For Download DLL:")
    print("Choose wisely! If you pick the wrong graphic card, the program will crash.")
    print(" ")
    print("1. RTX 3090 , RTX 3080 , RTX 3070 , RTX 3060 , RTX 3050")
    print("2. RTX 2080 , RTX 2070 , RTX 2060 , GTX 1660 , GTX 1650")
    print("3. GTX 1080 , GTX 1070 , GTX 1060, GTX 1050 , GT 1030, GT 1010")
    print("4. AMD and Other Graphic Card")
    print(" ")

    choice = input("Enter your choice (1-4): ")

    print(" ")
    options = {
        "1": "RTX 3090 Ti, RTX 3090, RTX 3080 Ti, RTX 3080 12GB, RTX 3080, RTX 3070 Ti, RTX 3070, RTX 3060 Ti, RTX 3060, RTX 3050",
        "2": "RTX 2080 Ti, RTX 2080 Super, RTX 2080, RTX 2070 Super, RTX 2070, RTX 2060 Super, RTX 2060 12GB, RTX 2060, GTX 1660 Ti, GTX 1660 Super, GTX 1660, GTX 1650 Super, GTX 1650",
        "3": "GTX 1080 Ti, GTX 1080, GTX 1070 Ti, GTX 1070, GTX 1060, GTX 1050 Ti, GTX 1050, GT 1030, GT 1010",
        "4": "AMD and Other Graphic Card"
    }

    if choice not in options:
        print("Invalid choice. Exiting.")
        sys.exit()

    print(f"You have selected : {options[choice]}")

    zip_names = {
        "1": "opencv_world452_86.zip",
        "2": "opencv_world452_75.zip",
        "3": "opencv_world452_61.zip",
        "4": "opencv_world452.zip"
    }

    zip_name = zip_names[choice]

    # Download and extract opencv_world452.dll
    dll_url = f"https://github.com/fiqhi19/cuda_cudnn_files/releases/download/Release/{zip_name}"

    # Download opencv_world452.dll
    opencv_zip_path = os.path.abspath(os.path.join(folder_path, zip_name))

    if download_file(dll_url, folder_path):
        print(timestamp + Fore.GREEN + f"Download of opencv_world complete." + Style.RESET_ALL)
        # Extract opencv_world452.dll
        with zipfile.ZipFile(opencv_zip_path, 'r') as zip_ref:
            zip_ref.extractall(folder_path)

        # Remove opencv_world452.zip after extraction
        os.remove(opencv_zip_path)

        print(timestamp + Fore.GREEN + "Extraction complete." + Style.RESET_ALL)
        print(" ")
    else:
        print(timestamp + Fore.RED + f"Failed to download opencv_world. Exiting." + Style.RESET_ALL)
        print(" ")
        sys.exit()

def is_process_running(process_name):
    for process in psutil.process_iter(['pid', 'name']):
        if process.info['name'] == process_name:
            return True
    return False

def lock_resize():
    # Deklarasikan konstanta-konstanta dari WinAPI
    GWL_STYLE = -16
    WS_MAXIMIZEBOX = 0x00010000
    WS_SIZEBOX = 0x00040000

    while True:
        # Dapatkan handle untuk jendela konsol
        console_window = ctypes.windll.kernel32.GetConsoleWindow()

        # Dapatkan nilai style saat ini
        style = ctypes.windll.user32.GetWindowLongW(console_window, GWL_STYLE)

        # Hapus WS_MAXIMIZEBOX dan WS_SIZEBOX dari nilai style
        new_style = style & ~WS_MAXIMIZEBOX & ~WS_SIZEBOX

        # Atur kembali nilai style untuk jendela konsol
        ctypes.windll.user32.SetWindowLongW(console_window, GWL_STYLE, new_style)

def main():
    timestamp = get_timestamp()
    random_title = build_title(20)  # Change 10 to the desired length
    set_window_title(random_title)

    _thread.start_new_thread(lock_resize, ())

    print(Fore.YELLOW + "This program requires administrative privileges." + Style.RESET_ALL)

    # Meminta hak administrator
    run_as_admin()

    # Lanjutkan dengan operasi yang memerlukan hak administrator
    print(timestamp + Fore.GREEN + "Running with administrative privileges." + Style.RESET_ALL)

    # Cek dan setup lingkungan
    check_and_setup_environment()

    # Lanjutkan dengan tugas utama Anda setelah setup
    print(timestamp + Fore.GREEN + "Environment setup complete. Proceed with the next steps." + Style.RESET_ALL)

    check_and_setup_environment2()

    opencv_dll_path = os.path.join(os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn"), "opencv_world452.dll")

    premium_exe_path = os.path.join(os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn"), "premium.exe")

    if os.path.exists(opencv_dll_path):
        print(timestamp + Fore.GREEN + "opencv_world452.dll is present." + Style.RESET_ALL)
    else:
        download_opencv_dll()

    # Pindah ke direktori yang mengandung premium.exe
    os.chdir(os.path.dirname(premium_exe_path))

    print(" ")
    print("Options:")
    print("1. Press F1 to run moji-aim.")
    print("2. Press END to reset required files contents.")
    print("2. Press HOME to reset moji-aim and opencv.")

    # Tambahkan loop untuk mendeteksi tombol yang ditekan
    while True:
         # Mendeteksi tombol F1
        if win32api.GetAsyncKeyState(win32con.VK_F1) < 0:
            if os.path.exists(premium_exe_path):
                # Cek apakah premium.exe sedang berjalan
                if is_process_running("premium.exe"):
                    print(timestamp + Fore.YELLOW + "premium.exe is already running." + Style.RESET_ALL)
                    os._exit(0)  # Menutup console Python
                else:
                    print(timestamp + Fore.GREEN + "Running moji-aim..." + Style.RESET_ALL)
                    # Menjalankan premium.exe dalam console terpisah
                    process = subprocess.Popen(["premium.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                print(timestamp + Fore.RED + "Error: moji-aim not found." + Style.RESET_ALL)
                os._exit(1)  # Menutup console Python script dengan status error
                break

        # Mendeteksi tombol F2
        if win32api.GetAsyncKeyState(win32con.VK_END) < 0:
            try:
                folder_path = os.path.join(os.environ["USERPROFILE"], "AppData", "Local", "cuda_cudnn")
                for item in os.listdir(folder_path):
                    item_path = os.path.join(folder_path, item)
                    if os.path.isfile(item_path) or os.path.islink(item_path):
                        os.unlink(item_path)
                    elif os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                print(" ")
                print(timestamp + Fore.GREEN + "Content of required files deleted successfully." + Style.RESET_ALL)
            except Exception as e:
                print(timestamp + Fore.RED + f"Error deleting required files content: {e}" + Style.RESET_ALL)
                break
            check_and_setup_environment()

        if win32api.GetAsyncKeyState(win32con.VK_HOME) < 0:
            # Menghapus opencv_world452.dll dan premium.exe
            try:
                os.remove(opencv_dll_path)
                os.remove(premium_exe_path)
                print(" ")
                print(timestamp + Fore.GREEN + "opencv_world452.dll dan premium.exe dihapus dengan berhasil." + Style.RESET_ALL)
            except Exception as e:
                print(timestamp + Fore.RED + f"Error menghapus opencv_world452.dll dan premium.exe: {e}" + Style.RESET_ALL)
            check_and_setup_environment2()
            download_opencv_dll()
            restart()

    # Restart program setelah menghapus isi folder
    print(timestamp + Fore.GREEN + "Restarting the program..." + Style.RESET_ALL)

if __name__ == "__main__":
    # Panggil fungsi utama
    disable_console_mouse_input()
    main()
