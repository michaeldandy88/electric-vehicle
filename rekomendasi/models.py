import os
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.db import models

def kendaraan_directory_path(instance, filename):
    # Cek tipe instance apakah Mobil (Roda 4) atau Motor (Roda 2)
    if instance.__class__.__name__ == 'Mobil':
        return f'kendaraan/roda_4/{filename}'
    elif instance.__class__.__name__ == 'Motor':
        return f'kendaraan/roda_2/{filename}'
    return f'kendaraan/{filename}'

class BaseKendaraan(models.Model):
    merek = models.TextField(help_text="Nama merek kendaraan")
    harga = models.FloatField(help_text="Harga dalam Rupiah/Jutaan")
    jarak_tempuh = models.FloatField(help_text="Jarak tempuh dalam km")
    kapasitas_baterai = models.FloatField(help_text="Kapasitas baterai dalam kWh")
    gambar = models.ImageField(upload_to=kendaraan_directory_path, null=True, blank=True)

    class Meta:
        abstract = True
        
    def save(self, *args, **kwargs):
        if self.gambar:
            # Dapatkan nama file tanpa tambahan
            nama_file = self.gambar.name
            
            # Cek apakah file sudah dalam format .webp
            if not nama_file.lower().endswith('.webp'):
                img = Image.open(self.gambar)
                img_io = BytesIO()
                
                # Konversi menjadi format RGB kalau misal aslinya punya alpha (RGBA/PNG)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(img_io, format='WEBP', quality=85)
                
                # Ganti ekstensi file menjadi .webp
                filename_baru = os.path.splitext(os.path.basename(nama_file))[0] + '.webp'
                
                # Simpan ulang field gambarnya sebagai file .webp
                # pass save=False agar tidak infinite loop calling save()
                self.gambar.save(filename_baru, ContentFile(img_io.getvalue()), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.merek
class Mobil(BaseKendaraan):
    kapasitas_penumpang = models.IntegerField()
    tipe_kendaraan = models.CharField(max_length=50, help_text="Contoh: SUV, MPV, Hatchback")
    fitur_keselamatan = models.TextField(help_text="Contoh: ABS, EBD, BA")
    garansi = models.CharField(max_length=100)
    jaringan_servis = models.CharField(max_length=100)

def interior_directory_path(instance, filename):
    # Simpan di folder interior berdasarkan ID mobil
    return f'kendaraan/roda_4/interior_{instance.mobil.id}/{filename}'

class FotoInteriorMobil(models.Model):
    mobil = models.ForeignKey(Mobil, on_delete=models.CASCADE, related_name='foto_interior')
    gambar = models.ImageField(upload_to=interior_directory_path)

    def save(self, *args, **kwargs):
        if self.gambar:
            nama_file = self.gambar.name
            if not nama_file.lower().endswith('.webp'):
                img = Image.open(self.gambar)
                img_io = BytesIO()
                
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                img.save(img_io, format='WEBP', quality=85)
                filename_baru = os.path.splitext(os.path.basename(nama_file))[0] + '.webp'
                self.gambar.save(filename_baru, ContentFile(img_io.getvalue()), save=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Interior - {self.mobil.merek}"

class Motor(BaseKendaraan):
    SISTEM_PENGISIAN_CHOICES = [
        ('Direct Charging', 'Colok Langsung (Direct Charging)'),
        ('Swap Baterai', 'Tukar Baterai (Battery Swap)'),
        ('Keduanya', 'Bisa Keduanya (Direct & Swap)')
    ]
    kecepatan_maksimum = models.FloatField(help_text="Kecepatan max dalam km/jam")
    waktu_pengisian = models.FloatField(help_text="Waktu charging penuh dalam jam")
    jumlah_baterai = models.IntegerField(default=1, help_text="Jumlah slot/baterai bawaan (misal: 1 atau 2)")
    sistem_pengisian = models.CharField(
        max_length=50,
        choices=SISTEM_PENGISIAN_CHOICES,
        default='Direct Charging',
        help_text="Pilih sistem/metode pengisian daya untuk motor ini"
    )
    jenis_baterai = models.CharField(max_length=100, null=True, blank=True, help_text="Contoh: Lithium-ion, SLA")
    garansi = models.CharField(max_length=100, null=True, blank=True)