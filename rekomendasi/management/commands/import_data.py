import os
import io
import pandas as pd
from django.core.management.base import BaseCommand
from rekomendasi.models import Mobil, Motor
from django.conf import settings

class Command(BaseCommand):
    help = 'Mengimpor data R2 dan R4 dari file CSV ke database MySQL'

    def bersihkan_csv_rusak(self, file_path):
        """
        Fungsi pintar untuk memperbaiki file CSV dari Excel di mana 
        seluruh baris tidak sengaja terbungkus tanda kutip tunggal raksasa ("...")
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        clean_lines = []
        for idx, line in enumerate(lines):
            line = line.strip()
            if idx > 0 and line.startswith('"') and line.endswith('"'):
                line = line[1:-1]
                line = line.replace('""', '"')
            clean_lines.append(line)

        return io.StringIO('\n'.join(clean_lines))

    def handle(self, *args, **kwargs):
        base_dir = settings.BASE_DIR
        csv_r4 = os.path.join(base_dir, 'data_mentah', 'data_r4.csv')
        csv_r2 = os.path.join(base_dir, 'data_mentah', 'data_r2.csv')

        # ==========================================
        # 1. IMPORT DATA MOBIL (R4)
        # ==========================================
        if os.path.exists(csv_r4):
            self.stdout.write('Membersihkan & Membaca file data_r4.csv...')
            file_bersih_r4 = self.bersihkan_csv_rusak(csv_r4)
            df_r4 = pd.read_csv(file_bersih_r4)
            
            df_r4.columns = df_r4.columns.str.strip()
            
            kolom_num_r4 = ['Harga', 'Jarak Tempuh', 'Kapasitas Baterai']
            for col in kolom_num_r4:
                if col in df_r4.columns:
                    df_r4[col] = df_r4[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                    df_r4[col] = pd.to_numeric(df_r4[col], errors='coerce').fillna(0)

            if 'Kapasitas Penumpang' in df_r4.columns:
                df_r4['Kapasitas Penumpang'] = pd.to_numeric(df_r4['Kapasitas Penumpang'], errors='coerce').fillna(5).astype(int)

            Mobil.objects.all().delete()
            self.stdout.write('Data lama Mobil dihapus.')

            total_r4 = 0
            for index, row in df_r4.iterrows():
                try:
                    Mobil.objects.create(
                        merek=row['Merek Mobil'], 
                        harga=row['Harga'],
                        kapasitas_penumpang=row.get('Kapasitas Penumpang', 5),
                        jarak_tempuh=row['Jarak Tempuh'],
                        kapasitas_baterai=row['Kapasitas Baterai'],
                        tipe_kendaraan=row['Tipe Kendaraan'],
                        fitur_keselamatan=row['Fitur Keselamatan'],
                        garansi=row['Garansi'],
                        jaringan_servis=row['Jaringan Servis']
                    )
                    total_r4 += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Gagal impor Mobil baris {index}: {e}"))
            self.stdout.write(self.style.SUCCESS(f'⚡ Berhasil mengimpor {total_r4} Mobil!'))
        else:
            self.stdout.write(self.style.ERROR(f'File {csv_r4} tidak ditemukan!'))

        # ==========================================
        # 2. IMPORT DATA MOTOR (R2)
        # ==========================================
        if os.path.exists(csv_r2):
            self.stdout.write('\nMembersihkan & Membaca file data_r2.csv...')
            file_bersih_r2 = self.bersihkan_csv_rusak(csv_r2)
            df_r2 = pd.read_csv(file_bersih_r2)
            df_r2.columns = df_r2.columns.str.strip()
            
            kolom_num_r2 = ['Harga', 'Jarak Tempuh', 'Kecepatan Maksimum', 'Kapasitas Baterai', 'Waktu Pengisian', 'Jumlah Baterai']
            for col in kolom_num_r2:
                if col in df_r2.columns:
                    df_r2[col] = df_r2[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                    df_r2[col] = pd.to_numeric(df_r2[col], errors='coerce').fillna(0)

            Motor.objects.all().delete()
            self.stdout.write('Data lama Motor dihapus.')

            total_r2 = 0
            for index, row in df_r2.iterrows():
                try:
                    Motor.objects.create(
                        merek=row['Merek'], 
                        harga=row['Harga'],
                        jarak_tempuh=row['Jarak Tempuh'],
                        kecepatan_maksimum=row['Kecepatan Maksimum'],
                        kapasitas_baterai=row['Kapasitas Baterai'],
                        waktu_pengisian=row['Waktu Pengisian'],
                        jumlah_baterai=row.get('Jumlah Baterai', 1) 
                    )
                    total_r2 += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Gagal impor Motor baris {index}: {e}"))
            self.stdout.write(self.style.SUCCESS(f'⚡ Berhasil mengimpor {total_r2} Motor!'))
        else:
            self.stdout.write(self.style.ERROR(f'File {csv_r2} tidak ditemukan!'))

        self.stdout.write(self.style.SUCCESS('\n✅ PROSES SEEDING DATABASE SELESAI!'))