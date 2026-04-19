import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .models import Mobil, Motor

def aman_qcut(kolom, persentase, label_kategori):
    if len(kolom) < 2:
        return pd.Series([label_kategori[0]] * len(kolom), index=kolom.index).astype(str)
    try:
        return pd.qcut(kolom.rank(method='first'), q=persentase, labels=label_kategori).astype(str)
    except:
        return pd.Series([label_kategori[0]] * len(kolom), index=kolom.index).astype(str)

def format_angka_rupiah(angka):
    try:
        val = float(angka)
        if val >= 1_000_000_000:
            hasil = f"{val / 1_000_000_000:.2f}".rstrip('0').rstrip('.')
            return f"{hasil} Miliar"
        elif val >= 1_000_000:
            hasil = f"{val / 1_000_000:.2f}".rstrip('0').rstrip('.')
            return f"{hasil} Juta"
        else:
            return f"{val:,.0f}"
    except:
        return str(angka)

# ==========================================
# 1. MESIN REKOMENDASI MOBIL (R4)
# ==========================================
def get_rekomendasi_mobil(kriteria_user, min_harga=None, max_harga=None, top_n=5):
    mobil_qs = Mobil.objects.all().values()
    df = pd.DataFrame(list(mobil_qs))
    if df.empty: return []

    if min_harga is not None and min_harga != '':
        df = df[df['harga'] >= float(min_harga) * 1_000_000]
    if max_harga is not None and max_harga != '':
        df = df[df['harga'] <= float(max_harga) * 1_000_000]
        
    if df.empty: return []

    kriteria_bersih = kriteria_user.lower()

    kamus_kriteria = {
        "harga terjangkau": "harga_terjangkau", "harga menengah": "harga_menengah", "harga premium": "harga_premium",
        "jarak pendek": "jarak_pendek", "jarak menengah": "jarak_menengah", "jarak jauh": "jarak_jauh",
        "baterai kecil": "baterai_kecil", "baterai sedang": "baterai_sedang", "baterai besar": "baterai_besar",
        "4 orang": "penumpang_4", "4 penumpang": "penumpang_4", "kapasitas 4": "penumpang_4",
        "5 orang": "penumpang_5", "5 penumpang": "penumpang_5", "kapasitas 5": "penumpang_5",
        "7 orang": "penumpang_7", "7 penumpang": "penumpang_7", "kapasitas 7": "penumpang_7",
    }
    for asli, sistem in kamus_kriteria.items():
        kriteria_bersih = kriteria_bersih.replace(asli, sistem)

    tipe_umum = ['suv', 'mpv', 'hatchback', 'sedan', 'crossover']
    for tipe in tipe_umum:
        if tipe in kriteria_bersih.split():
            df = df[df['tipe_kendaraan'].str.lower().str.contains(tipe)]
            break
            
    if df.empty: return []

    df['Harga_Kategori'] = aman_qcut(df['harga'], [0, 0.25, 0.75, 1.0], ['harga_terjangkau', 'harga_menengah', 'harga_premium'])
    df['Jarak_Kategori'] = aman_qcut(df['jarak_tempuh'], [0, 0.25, 0.75, 1.0], ['jarak_pendek', 'jarak_menengah', 'jarak_jauh'])
    df['Baterai_Kategori'] = aman_qcut(df['kapasitas_baterai'], [0, 0.33, 0.66, 1.0], ['baterai_kecil', 'baterai_sedang', 'baterai_besar'])

    df['Penumpang_Kategori'] = df['kapasitas_penumpang'].astype(str).apply(lambda x: 'penumpang_' + x)
    df['Tipe_Clean'] = df['tipe_kendaraan'].astype(str).str.replace(' ', '').str.lower()
    df['Fitur_Clean'] = df['fitur_keselamatan'].astype(str).str.replace(',', ' ').str.lower()
    df['Garansi_Clean'] = df['garansi'].astype(str).str.replace(',', ' ').str.lower()
    
    df['Baterai_Raw'] = df['kapasitas_baterai'].astype(str) + ' kwh'
    df['Jarak_Raw'] = df['jarak_tempuh'].astype(str) + ' km'

    df['soup'] = df.apply(lambda x: ' '.join([
        x['Harga_Kategori'], x['Jarak_Kategori'], x['Baterai_Kategori'], 
        x['Penumpang_Kategori'], x['Tipe_Clean'], x['Fitur_Clean'], 
        x['Garansi_Clean'], x['Baterai_Raw'], x['Jarak_Raw']
    ]), axis=1)

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['soup'])
    query_vec = tfidf.transform([kriteria_bersih])
    
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    mobil_indices = sim_scores.argsort()[::-1][:top_n]
    
    hasil = []
    for idx in mobil_indices:
        if sim_scores[idx] > 0:
            mobil = df.iloc[idx]
            # --- DATA EKSTRA MOBIL DIKIRIM KE HTML ---
            hasil.append({
                'id': mobil['id'],
                'merek': mobil['merek'], 
                'harga': mobil['harga'],
                'harga_format': format_angka_rupiah(mobil['harga']),
                'jarak_tempuh': mobil['jarak_tempuh'], 
                'tipe': mobil['tipe_kendaraan'],
                'penumpang': mobil['kapasitas_penumpang'],
                'baterai': mobil['kapasitas_baterai'],
                'gambar': mobil['gambar'] if 'gambar' in mobil and pd.notna(mobil['gambar']) else '',
                'skor_kecocokan': round(sim_scores[idx] * 100, 2)
            })
    return hasil

# ==========================================
# 2. MESIN REKOMENDASI MOTOR (R2)
# ==========================================
def get_rekomendasi_motor(kriteria_user, min_harga=None, max_harga=None, top_n=5):
    motor_qs = Motor.objects.all().values()
    df = pd.DataFrame(list(motor_qs))
    if df.empty: return []

    if min_harga is not None and min_harga != '':
        df = df[df['harga'] >= float(min_harga) * 1_000_000]
    if max_harga is not None and max_harga != '':
        df = df[df['harga'] <= float(max_harga) * 1_000_000]
        
    if df.empty: return []

    kriteria_bersih = kriteria_user.lower()

    kamus_kriteria = {
        "harga terjangkau": "harga_terjangkau", "harga menengah": "harga_menengah", "harga premium": "harga_premium",
        "jarak pendek": "jarak_pendek", "jarak menengah": "jarak_menengah", "jarak jauh": "jarak_jauh",
        "cas cepat": "cas_cepat", "cas standar": "cas_standar", "cas lama": "cas_lama",
        "kecepatan standar": "kecepatan_standar", "kecepatan tinggi": "kecepatan_tinggi",
        "1 baterai": "baterai_1", "2 baterai": "baterai_2",
    }
    for asli, sistem in kamus_kriteria.items():
        kriteria_bersih = kriteria_bersih.replace(asli, sistem)

    if "baterai_2" in kriteria_bersih:
        df = df[df['jumlah_baterai'] == 2]
    elif "baterai_1" in kriteria_bersih:
        df = df[df['jumlah_baterai'] == 1]

    if df.empty: return []

    df['Harga_Kategori'] = aman_qcut(df['harga'], [0, 0.33, 0.66, 1.0], ['harga_terjangkau', 'harga_menengah', 'harga_premium'])
    df['Jarak_Kategori'] = aman_qcut(df['jarak_tempuh'], [0, 0.33, 0.66, 1.0], ['jarak_pendek', 'jarak_menengah', 'jarak_jauh'])
    df['Kecepatan_Kategori'] = aman_qcut(df['kecepatan_maksimum'], [0, 0.5, 1.0], ['kecepatan_standar', 'kecepatan_tinggi'])
    df['Cas_Kategori'] = aman_qcut(df['waktu_pengisian'], [0, 0.33, 0.66, 1.0], ['cas_cepat', 'cas_standar', 'cas_lama'])
    df['Jumlah_Baterai_Kategori'] = df['jumlah_baterai'].astype(str).apply(lambda x: 'baterai_' + x)
    
    df['Baterai_Raw'] = df['kapasitas_baterai'].astype(str) + ' kwh'
    df['Jarak_Raw'] = df['jarak_tempuh'].astype(str) + ' km'
    df['Kecepatan_Raw'] = df['kecepatan_maksimum'].astype(str) + ' km/jam'
    
    df['soup'] = df.apply(lambda x: ' '.join([
        x['Harga_Kategori'], x['Jarak_Kategori'], x['Kecepatan_Kategori'], 
        x['Cas_Kategori'], x['Jumlah_Baterai_Kategori'], 
        x['Baterai_Raw'], x['Jarak_Raw'], x['Kecepatan_Raw']
    ]), axis=1)

    tfidf = TfidfVectorizer()
    tfidf_matrix = tfidf.fit_transform(df['soup'])
    query_vec = tfidf.transform([kriteria_bersih])
    
    sim_scores = cosine_similarity(query_vec, tfidf_matrix).flatten()
    motor_indices = sim_scores.argsort()[::-1][:top_n]
    
    hasil = []
    for idx in motor_indices:
        if sim_scores[idx] > 0:
            motor = df.iloc[idx]
            # --- DATA EKSTRA MOTOR DIKIRIM KE HTML ---
            hasil.append({
                'id': motor['id'],
                'merek': motor['merek'], 
                'harga': motor['harga'],
                'harga_format': format_angka_rupiah(motor['harga']),
                'jarak_tempuh': motor['jarak_tempuh'], 
                'jml_baterai': motor['jumlah_baterai'],
                'baterai': motor['kapasitas_baterai'],
                'kecepatan': motor['kecepatan_maksimum'],
                'cas': motor['waktu_pengisian'],
                'gambar': motor['gambar'] if 'gambar' in motor and pd.notna(motor['gambar']) else '',
                'skor_kecocokan': round(sim_scores[idx] * 100, 2)
            })
    return hasil