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
        
        if kata_kunci.strip():
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

    context = {
        'hasil': hasil_pencarian,
        'kata_kunci': kata_kunci,
        'jenis': jenis_kendaraan,
        'min_harga': min_harga,
        'max_harga': max_harga,
        'merek_mobil_group': merek_mobil_group,
        'tipe_mobil': tipe_mobil,
        'merek_motor_group': merek_motor_group
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
            hasil = f"{val / 1_000_000_000:.2f}".rstrip('0').rstrip('.')
            kendaraan.harga_format = f"{hasil} Miliar"
        elif val >= 1_000_000:
            hasil = f"{val / 1_000_000:.2f}".rstrip('0').rstrip('.')
            kendaraan.harga_format = f"{hasil} Juta"
        else:
            kendaraan.harga_format = f"{val:,.0f}"
    except:
        kendaraan.harga_format = str(kendaraan.harga)

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
            
            if jenis == 'mobil':
                for index, row in df.iterrows():
                    try: harga = float(str(row.get('Harga', '0')).replace(',', ''))
                    except ValueError: harga = 0.0
                    
                    try: jarak_tempuh = float(str(row.get('Jarak Tempuh', '0')).lower().replace('km', '').strip())
                    except ValueError: jarak_tempuh = 0.0
                    
                    try: kapasitas_baterai = float(str(row.get('Kapasitas Baterai', '0')).lower().replace('kwh', '').strip())
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
                    try: harga = float(str(row.get('Harga', '0')).replace(',', ''))
                    except ValueError: harga = 0.0
                    
                    try: jarak_tempuh = float(str(row.get('Jarak Tempuh', '0')).lower().replace('km', '').strip())
                    except ValueError: jarak_tempuh = 0.0
                    
                    try: kecepatan_max = float(str(row.get('Kecepatan Maksimum', '0')).lower().replace('km/jam', '').strip())
                    except ValueError: kecepatan_max = 0.0
                    
                    try: kapasitas_baterai = float(str(row.get('Kapasitas Baterai', '0')).lower().replace('kwh', '').strip())
                    except ValueError: kapasitas_baterai = 0.0
                    
                    wp_str = str(row.get('Waktu Pengisian', '0')).lower().replace('jam', '').strip()
                    if wp_str == 'nan': wp_str = '0'
                    try: waktu_pengisian = float(wp_str)
                    except ValueError: waktu_pengisian = 0.0
                    
                    try: jb = int(row.get('Jumlah Baterai', 1))
                    except ValueError: jb = 1
                    
                    sistem_pengisian = str(row.get('Sistem Pengisian', 'Direct Charging'))
                    
                    Motor.objects.update_or_create(
                        merek=row.get('Merek', 'Unknown'),
                        defaults={
                            'harga': harga,
                            'jarak_tempuh': jarak_tempuh,
                            'kapasitas_baterai': kapasitas_baterai,
                            'kecepatan_maksimum': kecepatan_max,
                            'waktu_pengisian': waktu_pengisian,
                            'jumlah_baterai': jb,
                            'sistem_pengisian': sistem_pengisian
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
                sistem_pengisian=request.POST.get('sistem_pengisian', 'Direct Charging')
            )
            if 'gambar' in request.FILES:
                kendaraan.gambar = request.FILES['gambar']
                kendaraan.save()
            messages.success(request, f'Data Kendaraan Baru {kendaraan.merek} berhasil ditambahkan!')
            
    return redirect('dashboard_admin')