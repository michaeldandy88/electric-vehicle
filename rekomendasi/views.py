import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Mobil, Motor
from .ml_engine import get_rekomendasi_mobil, get_rekomendasi_motor

def halaman_rekomendasi(request):
    hasil_pencarian = []
    kata_kunci = ""
    jenis_kendaraan = ""
    min_harga = request.GET.get('min_harga', '')
    max_harga = request.GET.get('max_harga', '')

    if 'kriteria' in request.GET and 'jenis' in request.GET:
        kata_kunci = request.GET.get('kriteria')
        jenis_kendaraan = request.GET.get('jenis')
        
        if jenis_kendaraan == 'mobil':
            hasil_pencarian = get_rekomendasi_mobil(kata_kunci, min_harga=min_harga, max_harga=max_harga, top_n=5)
        elif jenis_kendaraan == 'motor':
            hasil_pencarian = get_rekomendasi_motor(kata_kunci, min_harga=min_harga, max_harga=max_harga, top_n=5)

    # Grouping untuk Roda 4 (Mobil)
    mobil_raw = Mobil.objects.values_list('merek', flat=True).distinct()
    merek_mobil_group = {}
    for nama in mobil_raw:
        # Pengecualian atau split kata pertama sebagai merek (contoh: 'Hyundai Ioniq 5' -> brand: 'Hyundai', model: 'Ioniq 5')
        parts = nama.split(' ', 1)
        brand = parts[0]
        model = parts[1] if len(parts) > 1 else 'Base Model'
        
        if brand not in merek_mobil_group:
            merek_mobil_group[brand] = []
        merek_mobil_group[brand].append({'full': nama, 'model': model})

    # Grouping untuk Roda 2 (Motor)
    motor_raw = Motor.objects.values_list('merek', flat=True).distinct()
    merek_motor_group = {}
    for nama in motor_raw:
        parts = nama.split(' ', 1)
        brand = parts[0]
        model = parts[1] if len(parts) > 1 else 'Base Model'
        
        if brand not in merek_motor_group:
            merek_motor_group[brand] = []
        merek_motor_group[brand].append({'full': nama, 'model': model})

    tipe_mobil = list(Mobil.objects.values_list('tipe_kendaraan', flat=True).distinct().order_by('tipe_kendaraan'))
    kapasitas_penumpang_mobil = list(Mobil.objects.values_list('kapasitas_penumpang', flat=True).distinct().order_by('kapasitas_penumpang'))
    jaringan_servis_mobil = list(Mobil.objects.values_list('jaringan_servis', flat=True).distinct().order_by('jaringan_servis')) if hasattr(Mobil, 'jaringan_servis') else []
    
    sistem_pengisian_motor = list(Motor.objects.values_list('sistem_pengisian', flat=True).distinct().order_by('sistem_pengisian'))
    jumlah_baterai_motor = list(Motor.objects.values_list('jumlah_baterai', flat=True).distinct().order_by('jumlah_baterai'))
    kecepatan_motor = list(Motor.objects.values_list('kecepatan_maksimum', flat=True).distinct().order_by('kecepatan_maksimum'))
    jenis_baterai_motor = [j for j in list(Motor.objects.values_list('jenis_baterai', flat=True).distinct().order_by('jenis_baterai')) if j]
    garansi_motor = [g for g in list(Motor.objects.values_list('garansi', flat=True).distinct().order_by('garansi')) if g]

    context = {
        'hasil': hasil_pencarian,
        'kata_kunci': kata_kunci,
        'jenis': jenis_kendaraan,
        'min_harga': min_harga,
        'max_harga': max_harga,
        'merek_mobil_group': merek_mobil_group,
        'tipe_mobil': tipe_mobil,
        'kapasitas_penumpang_mobil': kapasitas_penumpang_mobil,
        'jaringan_servis_mobil': jaringan_servis_mobil,
        'merek_motor_group': merek_motor_group,
        'sistem_pengisian_motor': sistem_pengisian_motor,
        'jumlah_baterai_motor': jumlah_baterai_motor,
        'kecepatan_motor': kecepatan_motor,
        'jenis_baterai_motor': jenis_baterai_motor,
        'garansi_motor': garansi_motor,
    }
    
    return render(request, 'rekomendasi_app/beranda.html', context)

def kendaraan_detail(request, jenis, id):
    if jenis == 'mobil':
        kendaraan = get_object_or_404(Mobil, id=id)
    elif jenis == 'motor':
        kendaraan = get_object_or_404(Motor, id=id)
    else:
        return redirect('beranda')

    try:
        val = float(kendaraan.harga)
        if val >= 1_000_000_000:
            hasil = round(val / 1_000_000_000, 2)
            kendaraan.harga_format = f"Rp {hasil} Miliar (OTR)"
        elif val >= 1_000_000:
            hasil = round(val / 1_000_000, 2)
            kendaraan.harga_format = f"Rp {hasil} Juta (OTR)"
        else:
            kendaraan.harga_format = f"Rp {val:,.0f} (OTR)"
    except:
        kendaraan.harga_format = f"Rp {kendaraan.harga} (OTR)"

    return render(request, 'rekomendasi_app/detail.html', {'kendaraan': kendaraan, 'jenis': jenis})

from django.contrib.auth.decorators import login_required, user_passes_test

def is_admin(user):
    return user.is_staff

@login_required
@user_passes_test(is_admin)
def dashboard_admin(request):
    if request.method == 'POST':
        if 'csv_file' not in request.FILES:
            messages.error(request, 'Pilih file CSV terlebih dahulu!')
            return redirect('dashboard_admin')
            
        csv_file = request.FILES['csv_file']
        jenis = request.POST.get('jenis')
        
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File harus berformat .csv!')
            return redirect('dashboard_admin')

        try:
            df = pd.read_csv(csv_file)
            df = df.fillna('')
            
            if jenis == 'mobil':
                for index, row in df.iterrows():
                    try: 
                        val = str(row.get('Harga', '0')).replace(',', '').strip()
                        harga = 0.0 if val.lower() == 'nan' or val == '' else float(val)
                    except ValueError: harga = 0.0
                    
                    try: 
                        val = str(row.get('Jarak Tempuh', '0')).lower().replace('km', '').strip()
                        jarak_tempuh = 0.0 if val == 'nan' or val == '' else float(val)
                    except ValueError: jarak_tempuh = 0.0
                    
                    try: 
                        val = str(row.get('Kapasitas Baterai', '0')).lower().replace('kwh', '').strip()
                        kapasitas_baterai = 0.0 if val == 'nan' or val == '' else float(val)
                    except ValueError: kapasitas_baterai = 0.0
                    
                    try: kaps_penumpang = int(row.get('Kapasitas Penumpang', 0))
                    except: kaps_penumpang = 0
                    
                    Mobil.objects.update_or_create(
                        merek=row.get('Merek Mobil', row.get('Merek', 'Unknown')),
                        defaults={
                            'harga': harga,
                            'jarak_tempuh': jarak_tempuh,
                            'kapasitas_baterai': kapasitas_baterai,
                            'kapasitas_penumpang': kaps_penumpang,
                            'tipe_kendaraan': str(row.get('Tipe Kendaraan', '')),
                            'fitur_keselamatan': str(row.get('Fitur Keselamatan', '')),
                            'garansi': str(row.get('Garansi', '')),
                            'jaringan_servis': str(row.get('Jaringan Servis', ''))
                        }
                    )
                messages.success(request, f'Sukses upload data {len(df)} Mobil!')
                
            elif jenis == 'motor':
                for index, row in df.iterrows():
                    try: 
                        val = str(row.get('Harga', '0')).replace(',', '').strip()
                        harga = 0.0 if val.lower() == 'nan' or val == '' else float(val)
                    except ValueError: harga = 0.0
                    
                    try: 
                        val = str(row.get('Jarak Tempuh', '0')).lower().replace('km', '').strip()
                        jarak_tempuh = 0.0 if val == 'nan' or val == '' else float(val)
                    except ValueError: jarak_tempuh = 0.0
                    
                    try: 
                        val = str(row.get('Kecepatan Maksimum', '0')).lower().replace('km/jam', '').replace('km', '').strip()
                        kecepatan_max = 0.0 if val == 'nan' or val == '' else float(val)
                    except ValueError: kecepatan_max = 0.0
                    
                    try: 
                        val = str(row.get('Kapasitas Baterai', '0')).lower().replace('kwh', '').strip()
                        kapasitas_baterai = 0.0 if val == 'nan' or val == '' else float(val)
                    except ValueError: kapasitas_baterai = 0.0
                    
                    wp_str = str(row.get('Waktu Pengisian', '0')).lower().replace('jam', '').strip()
                    if wp_str == 'nan' or wp_str == '': wp_str = '0'
                    try: waktu_pengisian = float(wp_str)
                    except ValueError: waktu_pengisian = 0.0
                    
                    try: jb = int(row.get('Jumlah Baterai', 1))
                    except ValueError: jb = 1
                    
                    sistem_pengisian = str(row.get('Sistem Pengisian', 'Direct Charging'))
                    jenis_baterai = str(row.get('Jenis Baterai', ''))
                    garansi = str(row.get('Garansi', ''))
                    
                    Motor.objects.update_or_create(
                        merek=row.get('Merek', 'Unknown'),
                        defaults={
                            'harga': harga,
                            'jarak_tempuh': jarak_tempuh,
                            'kapasitas_baterai': kapasitas_baterai,
                            'kecepatan_maksimum': kecepatan_max,
                            'waktu_pengisian': waktu_pengisian,
                            'jumlah_baterai': jb,
                            'sistem_pengisian': sistem_pengisian,
                            'jenis_baterai': jenis_baterai,
                            'garansi': garansi
                        }
                    )
                messages.success(request, f'Sukses upload data {len(df)} Motor!')
        except Exception as e:
            messages.error(request, f"Terjadi kesalahan saat memproses file: {str(e)}")
            
        return redirect('dashboard_admin')

    total_mobil = Mobil.objects.count()
    total_motor = Motor.objects.count()
    context = {
        'total_mobil': total_mobil,
        'total_motor': total_motor,
        'mobil_list': Mobil.objects.all().order_by('-id'),
        'motor_list': Motor.objects.all().order_by('-id')
    }
    return render(request, 'rekomendasi_app/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def hapus_kendaraan(request, jenis, id):
    if jenis == 'mobil':
        kendaraan = get_object_or_404(Mobil, id=id)
    elif jenis == 'motor':
        kendaraan = get_object_or_404(Motor, id=id)
    else:
        return redirect('dashboard_admin')
    
    kendaraan.delete()
    messages.success(request, f'Kendaraan {kendaraan.merek} berhasil dihapus!')
    return redirect('dashboard_admin')

@login_required
@user_passes_test(is_admin)
def update_gambar_kendaraan(request, jenis, id):
    if request.method == 'POST' and 'gambar' in request.FILES:
        if jenis == 'mobil':
            kendaraan = get_object_or_404(Mobil, id=id)
        elif jenis == 'motor':
            kendaraan = get_object_or_404(Motor, id=id)
        else:
            return redirect('dashboard_admin')
            
        kendaraan.gambar = request.FILES['gambar']
        kendaraan.save()
        messages.success(request, f'Gambar untuk {kendaraan.merek} berhasil diunggah/diperbarui!')
    return redirect('dashboard_admin')

from .models import FotoInteriorMobil

@login_required
@user_passes_test(is_admin)
def upload_foto_interior(request, id):
    if request.method == 'POST' and 'gambar_interior' in request.FILES:
        mobil = get_object_or_404(Mobil, id=id)
        files = request.FILES.getlist('gambar_interior')
        for f in files:
            FotoInteriorMobil.objects.create(mobil=mobil, gambar=f)
        messages.success(request, f'{len(files)} Foto interior untuk {mobil.merek} berhasil ditambahkan!')
    return redirect('dashboard_admin')

@login_required
@user_passes_test(is_admin)
def hapus_foto_interior(request, id):
    foto = get_object_or_404(FotoInteriorMobil, id=id)
    mobil_merek = foto.mobil.merek
    foto.delete()
    messages.success(request, f'1 Foto interior {mobil_merek} berhasil dihapus!')
    return redirect('dashboard_admin')

@login_required
@user_passes_test(is_admin)
def update_data_kendaraan(request, jenis, id):
    if request.method == 'POST':
        if jenis == 'mobil':
            kendaraan = get_object_or_404(Mobil, id=id)
            kendaraan.merek = request.POST.get('merek', kendaraan.merek)
            kendaraan.harga = float(request.POST.get('harga', kendaraan.harga))
            kendaraan.jarak_tempuh = float(request.POST.get('jarak_tempuh', kendaraan.jarak_tempuh))
            kendaraan.kapasitas_baterai = float(request.POST.get('kapasitas_baterai', kendaraan.kapasitas_baterai))
            kendaraan.kapasitas_penumpang = int(request.POST.get('kapasitas_penumpang', kendaraan.kapasitas_penumpang))
            kendaraan.tipe_kendaraan = request.POST.get('tipe_kendaraan', kendaraan.tipe_kendaraan)
            kendaraan.fitur_keselamatan = request.POST.get('fitur_keselamatan', kendaraan.fitur_keselamatan)
            kendaraan.garansi = request.POST.get('garansi', kendaraan.garansi)
            kendaraan.jaringan_servis = request.POST.get('jaringan_servis', kendaraan.jaringan_servis)
            kendaraan.save()
            messages.success(request, f'Data Kendaraan {kendaraan.merek} berhasil diperbarui!')
            
        elif jenis == 'motor':
            kendaraan = get_object_or_404(Motor, id=id)
            kendaraan.merek = request.POST.get('merek', kendaraan.merek)
            kendaraan.harga = float(request.POST.get('harga', kendaraan.harga))
            kendaraan.jarak_tempuh = float(request.POST.get('jarak_tempuh', kendaraan.jarak_tempuh))
            kendaraan.kapasitas_baterai = float(request.POST.get('kapasitas_baterai', kendaraan.kapasitas_baterai))
            kendaraan.kecepatan_maksimum = float(request.POST.get('kecepatan_maksimum', kendaraan.kecepatan_maksimum))
            kendaraan.waktu_pengisian = float(request.POST.get('waktu_pengisian', kendaraan.waktu_pengisian))
            kendaraan.jumlah_baterai = int(request.POST.get('jumlah_baterai', kendaraan.jumlah_baterai))
            kendaraan.sistem_pengisian = request.POST.get('sistem_pengisian', kendaraan.sistem_pengisian)
            kendaraan.jenis_baterai = request.POST.get('jenis_baterai', kendaraan.jenis_baterai)
            kendaraan.garansi = request.POST.get('garansi', kendaraan.garansi)
            kendaraan.save()
            messages.success(request, f'Data Kendaraan {kendaraan.merek} berhasil diperbarui!')
    return redirect('dashboard_admin')

@login_required
@user_passes_test(is_admin)
def tambah_data_kendaraan(request, jenis):
    if request.method == 'POST':
        if jenis == 'mobil':
            kendaraan = Mobil.objects.create(
                merek=request.POST.get('merek', 'Unknown'),
                harga=float(request.POST.get('harga', 0)),
                jarak_tempuh=float(request.POST.get('jarak_tempuh', 0)),
                kapasitas_baterai=float(request.POST.get('kapasitas_baterai', 0)),
                kapasitas_penumpang=int(request.POST.get('kapasitas_penumpang', 0)),
                tipe_kendaraan=request.POST.get('tipe_kendaraan', ''),
                fitur_keselamatan=request.POST.get('fitur_keselamatan', ''),
                garansi=request.POST.get('garansi', ''),
                jaringan_servis=request.POST.get('jaringan_servis', '')
            )
            if 'gambar' in request.FILES:
                kendaraan.gambar = request.FILES['gambar']
                kendaraan.save()
            messages.success(request, f'Data Kendaraan Baru {kendaraan.merek} berhasil ditambahkan!')
            
        elif jenis == 'motor':
            kendaraan = Motor.objects.create(
                merek=request.POST.get('merek', 'Unknown'),
                harga=float(request.POST.get('harga', 0)),
                jarak_tempuh=float(request.POST.get('jarak_tempuh', 0)),
                kapasitas_baterai=float(request.POST.get('kapasitas_baterai', 0)),
                kecepatan_maksimum=float(request.POST.get('kecepatan_maksimum', 0)),
                waktu_pengisian=float(request.POST.get('waktu_pengisian', 0)),
                jumlah_baterai=int(request.POST.get('jumlah_baterai', 1)),
                sistem_pengisian=request.POST.get('sistem_pengisian', 'Direct Charging'),
                jenis_baterai=request.POST.get('jenis_baterai', ''),
                garansi=request.POST.get('garansi', '')
            )
            if 'gambar' in request.FILES:
                kendaraan.gambar = request.FILES['gambar']
                kendaraan.save()
            messages.success(request, f'Data Kendaraan Baru {kendaraan.merek} berhasil ditambahkan!')
            
    return redirect('dashboard_admin')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .ml_engine import aman_qcut, format_angka_rupiah

@login_required
@user_passes_test(is_admin)
def visualisasi_algoritma(request):
    jenis = request.GET.get('jenis', 'mobil')
    kriteria_user = request.GET.get('kriteria', '')
    
    context = {
        'jenis': jenis,
        'kriteria_asli': kriteria_user,
        'kriteria_bersih': '',
        'data_soup': [],
        'vocab': [],
        'query_vector': [],
        'matrix_data': []
    }
    
    if not kriteria_user:
        return render(request, 'rekomendasi_app/visualisasi.html', context)
        
    kriteria_bersih = kriteria_user.lower()
    
    # Process Mobil
    if jenis == 'mobil':
        df = pd.DataFrame(list(Mobil.objects.all().values()))
        if df.empty: return render(request, 'rekomendasi_app/visualisasi.html', context)
        
        kamus_kriteria = {
            "harga murah": "harga_terjangkau", "murah": "harga_terjangkau", "ekonomis": "harga_terjangkau",
            "harga menengah": "harga_menengah", "harga sedang": "harga_menengah",
            "harga premium": "harga_premium", "mewah": "harga_premium", "mahal": "harga_premium",
            "jarak pendek": "jarak_pendek", "range pendek": "jarak_pendek",
            "jarak menengah": "jarak_menengah", "range menengah": "jarak_menengah",
            "jarak jauh": "jarak_jauh", "range jauh": "jarak_jauh", "jarak tempuh jauh": "jarak_jauh",
            "baterai kecil": "baterai_kecil", "baterai sedang": "baterai_sedang", "baterai besar": "baterai_besar",
            "4 orang": "penumpang_4", "4 penumpang": "penumpang_4",
            "5 orang": "penumpang_5", "5 penumpang": "penumpang_5",
            "7 orang": "penumpang_7", "7 penumpang": "penumpang_7",
            "suv": "suv", "mpv": "mpv", "hatchback": "hatchback", "sedan": "sedan",
            "airbag": "airbag", "abs": "abs", "sensor parkir": "sensor parkir",
            "garansi panjang": "garansi_panjang", "jaringan servis luas": "jaringan_servis_luas"
        }
        for asli, sistem in kamus_kriteria.items():
            kriteria_bersih = kriteria_bersih.replace(asli, sistem)
            
        df['Harga_Kategori'] = aman_qcut(df['harga'], [0, 0.25, 0.75, 1.0], ['harga_terjangkau', 'harga_menengah', 'harga_premium'])
        df['Jarak_Kategori'] = aman_qcut(df['jarak_tempuh'], [0, 0.25, 0.75, 1.0], ['jarak_pendek', 'jarak_menengah', 'jarak_jauh'])
        df['Baterai_Kategori'] = aman_qcut(df['kapasitas_baterai'], [0, 0.33, 0.66, 1.0], ['baterai_kecil', 'baterai_sedang', 'baterai_besar'])
        df['Penumpang_Kategori'] = df['kapasitas_penumpang'].astype(str).apply(lambda x: 'penumpang_' + x)
        df['Tipe_Clean'] = df['tipe_kendaraan'].astype(str).str.lower()
        df['Fitur_Clean'] = df['fitur_keselamatan'].astype(str).str.replace(',', ' ').str.lower()
        df['Merek_Clean'] = df['merek'].astype(str).str.lower()

        df['soup'] = df.apply(lambda x: ' '.join([
            x['Harga_Kategori'], x['Jarak_Kategori'], x['Baterai_Kategori'], 
            x['Penumpang_Kategori'], x['Tipe_Clean'], x['Fitur_Clean'], x['Merek_Clean']
        ]), axis=1)

    # Process Motor
    else:
        df = pd.DataFrame(list(Motor.objects.all().values()))
        if df.empty: return render(request, 'rekomendasi_app/visualisasi.html', context)
        
        kamus_kriteria = {
            "harga murah": "harga_terjangkau", "murah": "harga_terjangkau",
            "harga menengah": "harga_menengah", "harga premium": "harga_premium", "mewah": "harga_premium",
            "jarak pendek": "jarak_pendek", "jarak menengah": "jarak_menengah", "jarak jauh": "jarak_jauh",
            "kecepatan standar": "kecepatan_standar", "kecepatan tinggi": "kecepatan_tinggi", "cepat": "kecepatan_tinggi",
            "cas cepat": "cas_cepat", "cas standar": "cas_standar", "cas lama": "cas_lama",
            "1 baterai": "baterai_1", "2 baterai": "baterai_2",
            "direct charging": "sistem_direct_charging", "swap baterai": "sistem_swap_baterai",
        }
        for asli, sistem in kamus_kriteria.items():
            kriteria_bersih = kriteria_bersih.replace(asli, sistem)
            
        df['Harga_Kategori'] = aman_qcut(df['harga'], [0, 0.33, 0.66, 1.0], ['harga_terjangkau', 'harga_menengah', 'harga_premium'])
        df['Jarak_Kategori'] = aman_qcut(df['jarak_tempuh'], [0, 0.33, 0.66, 1.0], ['jarak_pendek', 'jarak_menengah', 'jarak_jauh'])
        df['Kecepatan_Kategori'] = aman_qcut(df['kecepatan_maksimum'], [0, 0.5, 1.0], ['kecepatan_standar', 'kecepatan_tinggi'])
        df['Cas_Kategori'] = aman_qcut(df['waktu_pengisian'], [0, 0.33, 0.66, 1.0], ['cas_cepat', 'cas_standar', 'cas_lama'])
        df['Jumlah_Baterai_Kategori'] = df['jumlah_baterai'].astype(str).apply(lambda x: 'baterai_' + x)
        df['Sistem_Pengisian_Kategori'] = df['sistem_pengisian'].astype(str).str.replace(' ', '_').str.lower().apply(lambda x: 'sistem_' + x)
        df['Merek_Clean'] = df['merek'].astype(str).str.lower()
        
        df['soup'] = df.apply(lambda x: ' '.join([
            x['Harga_Kategori'], x['Jarak_Kategori'], x['Kecepatan_Kategori'], 
            x['Cas_Kategori'], x['Jumlah_Baterai_Kategori'], x['Sistem_Pengisian_Kategori'], x['Merek_Clean']
        ]), axis=1)

    # Calculate TF-IDF & Cosine Similarity
    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['soup'])
    query_vec = tfidf.transform([kriteria_bersih])
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    
    # Extract data for visualization
    vocab = tfidf.get_feature_names_out()
    
    # Sort indices based on similarity scores
    indices = sim_scores.argsort()[::-1]
    
    data_soup = []
    matrix_data = []
    
    for idx in indices:
        item = df.iloc[idx]
        score = float(sim_scores[idx])
        
        # We limit the matrix visual to top 20 items to not crash the browser
        if len(matrix_data) < 20:
            data_soup.append({
                'merek': item['merek'],
                'harga': format_angka_rupiah(item['harga']),
                'soup': item['soup'],
            })
            
            vector = tfidf_matrix[idx].toarray()[0]
            matrix_data.append({
                'merek': item['merek'],
                'score': round(score * 100, 2),
                'vector': [round(float(v), 3) for v in vector]
            })

    context.update({
        'kriteria_bersih': kriteria_bersih,
        'data_soup': data_soup,
        'vocab': list(vocab),
        'query_vector': [round(float(v), 3) for v in query_vec.toarray()[0]],
        'matrix_data': matrix_data
    })
    
    return render(request, 'rekomendasi_app/visualisasi.html', context)