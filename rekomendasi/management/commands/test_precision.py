import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from rekomendasi.models import Mobil, Motor
from rekomendasi.ml_engine import get_rekomendasi_mobil, get_rekomendasi_motor

class Command(BaseCommand):
    help = 'Menguji Precision@5 Sistem Rekomendasi dengan 20, 50, dan 100 Kueri serta menyimpan hasilnya ke hasil_pengujian.md'

    def handle(self, *args, **options):
        # 1. Dataset 100 Kueri String Unik
        queries = [
            # --- 50 Kueri Mobil ---
            "mobil murah",
            "mobil mewah",
            "mobil harga menengah",
            "mobil suv",
            "mobil hatchback",
            "mobil mpv",
            "mobil sedan",
            "mobil 4 penumpang",
            "mobil 5 penumpang",
            "mobil 7 penumpang",
            "mobil jarak jauh",
            "mobil hyundai",
            "mobil wuling",
            "mobil byd",
            "mobil tesla",
            "mobil suv murah",
            "mobil suv mewah",
            "mobil hatchback murah",
            "mobil hatchback mewah",
            "mobil mpv murah",
            "mobil mpv keluarga",
            "mobil sedan mewah",
            "mobil 5 penumpang murah",
            "mobil 7 penumpang keluarga",
            "mobil mewah jarak jauh",
            "mobil hyundai mewah",
            "mobil wuling murah",
            "mobil byd mewah",
            "mobil tesla mewah",
            "mobil suv jarak jauh",
            "mobil hatchback jarak jauh",
            "mobil mpv jarak jauh",
            "mobil sedan jarak jauh",
            "mobil 5 penumpang jarak jauh",
            "mobil 7 penumpang jarak jauh",
            "mobil dengan airbag",
            "mobil dengan abs",
            "mobil dengan kamera belakang",
            "mobil dengan sensor parkir",
            "mobil dengan cruise control",
            "mobil wuling hatchback",
            "mobil hyundai suv",
            "mobil byd suv",
            "mobil tesla sedan",
            "mobil bmw mewah",
            "mobil gwm murah",
            "mobil gac suv",
            "mobil chery suv",
            "mobil dfsk murah",
            "mobil mini hatchback",

            # --- 50 Kueri Motor ---
            "motor murah",
            "motor mewah",
            "motor harga menengah",
            "motor jarak jauh",
            "motor cas cepat",
            "motor fast charging",
            "motor swap baterai",
            "motor tukar baterai",
            "motor polytron",
            "motor alva",
            "motor yadea",
            "motor 1 baterai",
            "motor 2 baterai",
            "motor kecepatan tinggi",
            "motor kencang",
            "motor murah swap",
            "motor mewah swap",
            "motor polytron murah",
            "motor alva mewah",
            "motor alva swap",
            "motor yadea murah",
            "motor cas cepat murah",
            "motor mewah jarak jauh",
            "motor kecepatan tinggi mewah",
            "motor dengan lithium",
            "motor garansi panjang",
            "motor polytron fox",
            "motor alva cervo",
            "motor yadea osta",
            "motor 2 baterai jarak jauh",
            "motor cas cepat swap",
            "motor dengan direct charging",
            "motor kecepatan tinggi swap",
            "motor murah 1 baterai",
            "motor mewah 2 baterai",
            "motor dengan swap dan direct",
            "motor jangkauan jauh",
            "motor pengisian standar",
            "motor murah meriah",
            "motor mewah",
            "motor harian murah",
            "motor petualang jarak jauh",
            "motor alva one",
            "motor yadea velax",
            "motor polytron fox 500",
            "motor dengan baterai sla",
            "motor pengisian lama",
            "motor dengan charging langsung",
            "motor swap cepat",
            "motor alva n3"
        ]

        def get_vehicle_type(query):
            q = query.lower()
            if "motor" in q or "roda 2" in q:
                return "motor"
            return "mobil"

        # 2. Fungsi Ground Truth Relevance
        def is_relevant(query_str, instance, item_type):
            q = query_str.lower()
            
            # Merek/Brand Check (Dibuat dinamis mengambil kata pertama merek dari database)
            db_brands_mobil = list(Mobil.objects.values_list('merek', flat=True).distinct())
            db_brands_motor = list(Motor.objects.values_list('merek', flat=True).distinct())
            brands = list(set([m.split()[0].lower() for m in (db_brands_mobil + db_brands_motor) if m]))
            
            for b in brands:
                if b in q:
                    if b not in instance.merek.lower():
                        return False
            
            # Model Name specific check
            if 'ioniq' in q and 'ioniq' not in instance.merek.lower():
                return False
            if 'cervo' in q and 'cervo' not in instance.merek.lower():
                return False
            if 'fox 500' in q and '500' not in instance.merek.lower():
                return False
            if 'fox' in q and 'fox' not in instance.merek.lower():
                return False
            if 'n3' in q and 'n3' not in instance.merek.lower():
                return False
            if 'one' in q and 'one' not in instance.merek.lower():
                return False
            if 'velax' in q and 'velax' not in instance.merek.lower():
                return False
            if 'osta' in q and 'osta' not in instance.merek.lower():
                return False

            # Price Category Check
            if 'murah' in q or 'ekonomis' in q or 'meriah' in q or 'harian' in q:
                if item_type == 'mobil':
                    if instance.harga >= 300000000:
                        return False
                else:
                    if instance.harga >= 25000000:
                        return False
                        
            if 'premium' in q or 'mewah' in q:
                if item_type == 'mobil':
                    if instance.harga <= 1200000000:
                        return False
                else:
                    if instance.harga <= 40000000:
                        return False
                        
            if 'menengah' in q:
                if item_type == 'mobil':
                    if instance.harga < 300000000 or instance.harga > 1200000000:
                        return False
                else:
                    if instance.harga < 25000000 or instance.harga > 40000000:
                        return False

            # Body Type Check (for Mobil)
            if item_type == 'mobil':
                if 'suv' in q:
                    if 'suv' not in instance.tipe_kendaraan.lower():
                        return False
                if 'hatchback' in q:
                    if 'hatchback' not in instance.tipe_kendaraan.lower():
                        return False
                if 'mpv' in q or 'keluarga' in q:
                    if 'mpv' not in instance.tipe_kendaraan.lower() and 'wagon' not in instance.tipe_kendaraan.lower() and 'van' not in instance.tipe_kendaraan.lower():
                        return False
                if 'sedan' in q:
                    if 'sedan' not in instance.tipe_kendaraan.lower():
                        return False

            # Passenger Capacity Check
            if item_type == 'mobil':
                match = re.search(r'(\d+)\s*penumpang', q)
                if match:
                    kap = int(match.group(1))
                    if instance.kapasitas_penumpang != kap:
                        return False

            # Distance Range Check
            if 'jarak jauh' in q or 'jangkauan jauh' in q or 'petualang' in q:
                if item_type == 'mobil':
                    if instance.jarak_tempuh < 350:
                        return False
                else:
                    if instance.jarak_tempuh < 100:
                        return False

            # Charging Time Check (for Motor)
            if item_type == 'motor':
                if 'cas cepat' in q or 'fast charging' in q or 'swap cepat' in q:
                    if instance.waktu_pengisian > 4:
                        return False
                if 'pengisian standar' in q:
                    if instance.waktu_pengisian <= 4 or instance.waktu_pengisian > 5:
                        return False
                if 'pengisian lama' in q:
                    if instance.waktu_pengisian <= 5:
                        return False

            # Battery Swap Check (for Motor)
            if item_type == 'motor':
                if 'swap baterai' in q or 'tukar baterai' in q or 'swap' in q:
                    if 'swap' not in instance.sistem_pengisian.lower() and 'keduanya' not in instance.sistem_pengisian.lower():
                        return False
                if 'direct charging' in q or 'cas langsung' in q or 'charging langsung' in q:
                    if 'direct' not in instance.sistem_pengisian.lower() and 'keduanya' not in instance.sistem_pengisian.lower():
                        return False
                if 'swap dan direct' in q:
                    if 'keduanya' not in instance.sistem_pengisian.lower():
                        return False

            # Battery Slot Quantity Check (for Motor)
            if item_type == 'motor':
                if '1 baterai' in q or 'satu baterai' in q:
                    if instance.jumlah_baterai != 1:
                        return False
                if '2 baterai' in q or 'dua baterai' in q:
                    if instance.jumlah_baterai != 2:
                        return False

            # Max Speed Check (for Motor)
            if item_type == 'motor':
                if 'kecepatan tinggi' in q or 'kencang' in q:
                    if instance.kecepatan_maksimum < 90:
                        return False

            # Battery Chemistry Check (for Motor)
            if item_type == 'motor':
                if 'lithium' in q:
                    if 'lithium' not in (instance.jenis_baterai or '').lower():
                        return False
                if 'sla' in q:
                    if 'sla' not in (instance.jenis_baterai or '').lower():
                        return False

            # Safety Features Check (for Mobil)
            if item_type == 'mobil':
                if 'airbag' in q:
                    if 'airbag' not in instance.fitur_keselamatan.lower() and 'kantong udara' not in instance.fitur_keselamatan.lower():
                        return False
                if 'abs' in q:
                    if 'abs' not in instance.fitur_keselamatan.lower() and 'anti lock' not in instance.fitur_keselamatan.lower() and 'anti-lock' not in instance.fitur_keselamatan.lower():
                        return False
                if 'kamera belakang' in q:
                    if 'kamera' not in instance.fitur_keselamatan.lower() and 'camera' not in instance.fitur_keselamatan.lower():
                        return False
                if 'sensor parkir' in q:
                    if 'sensor' not in instance.fitur_keselamatan.lower() and 'parking' not in instance.fitur_keselamatan.lower():
                        return False
                if 'cruise control' in q:
                    if 'cruise' not in instance.fitur_keselamatan.lower():
                        return False

            return True

        # 3. Logika Pengujian Skenario
        scenarios = [20, 50, 100]
        results = {}

        for num_queries in scenarios:
            self.stdout.write(f"Menjalankan pengujian untuk skenario {num_queries} kueri...")
            scenario_queries = queries[:num_queries]
            query_details = []
            
            success_count = 0
            less_count = 0
            precision_sum = 0.0

            for index, query in enumerate(scenario_queries, 1):
                item_type = get_vehicle_type(query)
                
                # Memanggil mesin rekomendasi top 5
                if item_type == 'mobil':
                    recs = get_rekomendasi_mobil(query, top_n=5)
                else:
                    recs = get_rekomendasi_motor(query, top_n=5)
                
                # Menghitung jumlah hasil relevan di Top 5
                relevant_in_top5 = 0
                for rec in recs:
                    try:
                        # Ambil instance dari database berdasarkan ID untuk mengecek spesifikasi lengkap
                        if item_type == 'mobil':
                            instance = Mobil.objects.get(id=rec['id'])
                        else:
                            instance = Motor.objects.get(id=rec['id'])
                        
                        if is_relevant(query, instance, item_type):
                            relevant_in_top5 += 1
                    except Exception as e:
                        self.stdout.write(self.style.WARNING(f"Gagal mengambil data untuk ID {rec.get('id')}: {str(e)}"))

                # Menghitung Precision@5
                precision = (relevant_in_top5 / 5.0) * 100.0
                precision_sum += precision

                if precision == 100.0:
                    success_count += 1
                else:
                    less_count += 1

                query_details.append({
                    'no': index,
                    'query': query,
                    'relevant': relevant_in_top5,
                    'precision': precision
                })

            avg_precision = precision_sum / num_queries
            results[num_queries] = {
                'avg_precision': avg_precision,
                'success_count': success_count,
                'less_count': less_count,
                'details': query_details
            }

        md_content = []
        md_content.append("# Hasil Evaluasi Precision@5 Sistem Rekomendasi EV")
        md_content.append("\nDokumen ini berisi hasil pengujian Precision@5 otomatis untuk sistem rekomendasi kendaraan listrik berbasis **Content-Based Filtering (TF-IDF & Cosine Similarity)**.")
        
        # a. Tabel Perbandingan Nilai Precision Berdasarkan Jumlah Kueri
        md_content.append("\n## Tabel Perbandingan Nilai Precision Berdasarkan Jumlah Kueri\n")
        md_content.append("| Jumlah Kueri | Rata-rata Nilai Precision | Jumlah Kueri Sukses 100% | Jumlah Kueri < 100% |")
        md_content.append("|---|---|---|---|")
        for num in scenarios:
            avg_p = f"{results[num]['avg_precision']:.2f}%"
            succ = results[num]['success_count']
            less = results[num]['less_count']
            md_content.append(f"| {num} Kueri | {avg_p} | {succ} | {less} |")

        # b, c, d. Tabel Detail Pengujian masing-masing skenario
        for num in scenarios:
            md_content.append(f"\n## Tabel Detail Pengujian {num} Kueri\n")
            md_content.append("| No | Kueri | Jumlah Hasil Relevan di Top 5 | Nilai Precision |")
            md_content.append("|---|---|---|---|")
            for detail in results[num]['details']:
                md_content.append(f"| {detail['no']} | {detail['query']} | {detail['relevant']} / 5 | {detail['precision']:.1f}% |")

        output_path = os.path.join(settings.BASE_DIR, 'hasil_pengujian.md')
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(md_content))
            self.stdout.write(self.style.SUCCESS(f"\n[SUKSES] Hasil evaluasi lengkap telah ditulis ke: {output_path}\n"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Gagal menulis file hasil_pengujian.md: {str(e)}"))

        self.stdout.write('\n'.join(md_content))
