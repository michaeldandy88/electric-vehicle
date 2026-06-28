import os
import sys
import subprocess

def deploy():
    """
    Fungsi utama untuk melakukan otomatisasi deployment di server cPanel.
    Langkah-langkah yang dilakukan:
    1. Pindah ke direktori utama proyek di server.
    2. Jalankan 'git pull origin main' untuk menarik kode terbaru dari GitHub.
    3. Jalankan 'collectstatic' menggunakan interpreter Python dari virtual environment cPanel.
    4. Perbarui timestamp file 'passenger_wsgi.py' untuk memicu restart aplikasi Python.
    """
    
    # 1. Tentukan path folder utama proyek di server cPanel
    project_dir = "/home/pilihevc/sistem_rekomendasi"
    
    # Pindah ke direktori utama proyek sebelum menjalankan perintah git dan django-admin
    if os.path.exists(project_dir):
        os.chdir(project_dir)
        print(f"[INFO] Berhasil berpindah ke direktori: {project_dir}")
    else:
        # Jika dijalankan di lokal untuk testing, jalankan di direktori saat ini
        print(f"[WARNING] Direktori {project_dir} tidak ditemukan. Menggunakan direktori saat ini.")
        project_dir = os.getcwd()

    # 2. Tarik kode terbaru dari repositori GitHub (Cabang/Branch: main)
    print("[INFO] Menjalankan 'git pull origin main'...")
    try:
        git_result = subprocess.run(
            ["git", "pull", "origin", "main"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[SUCCESS] Output Git Pull:")
        print(git_result.stdout)
        if git_result.stderr:
            print("[INFO] Git Pull Stderr:", git_result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Gagal menarik kode terbaru melalui git: {e.stderr}", file=sys.stderr)
        raise e

    # 3. Jalankan perintah collectstatic untuk memperbarui aset CSS/JS secara bersih
    # Path interpreter Python virtual environment di cPanel
    venv_python = "/home/pilihevc/virtualenv/sistem_rekomendasi/3.13/bin/python"
    
    # Cek apakah interpreter python venv ada di path tersebut (hanya berjalan di server)
    if not os.path.exists(venv_python):
        print(f"[WARNING] Virtualenv Python tidak ditemukan di {venv_python}. Menggunakan sys.executable default.")
        venv_python = sys.executable

    print("[INFO] Menjalankan 'collectstatic --noinput --clear'...")
    try:
        static_result = subprocess.run(
            [venv_python, "manage.py", "collectstatic", "--noinput", "--clear"],
            capture_output=True,
            text=True,
            check=True
        )
        print("[SUCCESS] Output Collectstatic:")
        print(static_result.stdout)
        if static_result.stderr:
            print("[INFO] Collectstatic Stderr:", static_result.stderr)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Gagal mengumpulkan file statis (collectstatic): {e.stderr}", file=sys.stderr)
        raise e

    # 4. Sentuh (touch) file passenger_wsgi.py untuk memicu restart Python Application di cPanel
    passenger_wsgi_path = os.path.join(project_dir, "passenger_wsgi.py")
    if os.path.exists(passenger_wsgi_path):
        print(f"[INFO] Memperbarui timestamp '{passenger_wsgi_path}' untuk merestart Python App...")
        # Modul os.utime dengan parameter None akan memperbarui akses dan modifikasi waktu ke waktu sekarang
        os.utime(passenger_wsgi_path, None)
        print("[SUCCESS] Python Application berhasil dimintakan restart.")
    else:
        # Jika dijalankan di lokal, file passenger_wsgi.py biasanya tidak ada
        print(f"[WARNING] File '{passenger_wsgi_path}' tidak ditemukan. Lewati restart Python App.")

if __name__ == "__main__":
    print("=== Memulai Proses Otomatisasi Deployment ===")
    try:
        deploy()
        print("=== Deployment Selesai dengan Sukses ===")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"=== Deployment Gagal: Command '{' '.join(e.cmd)}' keluar dengan kode {e.returncode} ===", file=sys.stderr)
        sys.exit(e.returncode if e.returncode != 0 else 1)
    except Exception as e:
        print(f"=== Terjadi kesalahan tidak terduga: {str(e)} ===", file=sys.stderr)
        sys.exit(1)
