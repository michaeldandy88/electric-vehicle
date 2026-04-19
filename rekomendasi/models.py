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

class Motor(BaseKendaraan):
    kecepatan_maksimum = models.FloatField(help_text="Kecepatan max dalam km/jam")
    waktu_pengisian = models.FloatField(help_text="Waktu charging penuh dalam jam")
    jumlah_baterai = models.IntegerField(default=1, help_text="Jumlah slot/baterai bawaan (misal: 1 atau 2)")