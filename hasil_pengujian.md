# Hasil Evaluasi Precision@5 Sistem Rekomendasi EV

Dokumen ini berisi hasil pengujian Precision@5 otomatis untuk sistem rekomendasi kendaraan listrik berbasis **Content-Based Filtering (TF-IDF & Cosine Similarity)**.

## Tabel Perbandingan Nilai Precision Berdasarkan Jumlah Kueri

| Jumlah Kueri | Rata-rata Nilai Precision | Jumlah Kueri Sukses 100% | Jumlah Kueri < 100% |
|---|---|---|---|
| 20 Kueri | 83.00% | 13 | 7 |
| 50 Kueri | 71.60% | 26 | 24 |
| 100 Kueri | 61.40% | 43 | 57 |

## Tabel Detail Pengujian 20 Kueri

| No | Kueri | Jumlah Hasil Relevan di Top 5 | Nilai Precision |
|---|---|---|---|
| 1 | mobil murah | 3 / 5 | 60.0% |
| 2 | mobil mewah | 5 / 5 | 100.0% |
| 3 | mobil harga menengah | 4 / 5 | 80.0% |
| 4 | mobil suv | 5 / 5 | 100.0% |
| 5 | mobil hatchback | 5 / 5 | 100.0% |
| 6 | mobil mpv | 5 / 5 | 100.0% |
| 7 | mobil sedan | 5 / 5 | 100.0% |
| 8 | mobil 4 penumpang | 5 / 5 | 100.0% |
| 9 | mobil 5 penumpang | 5 / 5 | 100.0% |
| 10 | mobil 7 penumpang | 5 / 5 | 100.0% |
| 11 | mobil jarak jauh | 5 / 5 | 100.0% |
| 12 | mobil hyundai | 4 / 5 | 80.0% |
| 13 | mobil wuling | 5 / 5 | 100.0% |
| 14 | mobil byd | 5 / 5 | 100.0% |
| 15 | mobil tesla | 3 / 5 | 60.0% |
| 16 | mobil suv murah | 3 / 5 | 60.0% |
| 17 | mobil suv mewah | 5 / 5 | 100.0% |
| 18 | mobil hatchback murah | 5 / 5 | 100.0% |
| 19 | mobil hatchback mewah | 0 / 5 | 0.0% |
| 20 | mobil mpv murah | 1 / 5 | 20.0% |

## Tabel Detail Pengujian 50 Kueri

| No | Kueri | Jumlah Hasil Relevan di Top 5 | Nilai Precision |
|---|---|---|---|
| 1 | mobil murah | 3 / 5 | 60.0% |
| 2 | mobil mewah | 5 / 5 | 100.0% |
| 3 | mobil harga menengah | 4 / 5 | 80.0% |
| 4 | mobil suv | 5 / 5 | 100.0% |
| 5 | mobil hatchback | 5 / 5 | 100.0% |
| 6 | mobil mpv | 5 / 5 | 100.0% |
| 7 | mobil sedan | 5 / 5 | 100.0% |
| 8 | mobil 4 penumpang | 5 / 5 | 100.0% |
| 9 | mobil 5 penumpang | 5 / 5 | 100.0% |
| 10 | mobil 7 penumpang | 5 / 5 | 100.0% |
| 11 | mobil jarak jauh | 5 / 5 | 100.0% |
| 12 | mobil hyundai | 4 / 5 | 80.0% |
| 13 | mobil wuling | 5 / 5 | 100.0% |
| 14 | mobil byd | 5 / 5 | 100.0% |
| 15 | mobil tesla | 3 / 5 | 60.0% |
| 16 | mobil suv murah | 3 / 5 | 60.0% |
| 17 | mobil suv mewah | 5 / 5 | 100.0% |
| 18 | mobil hatchback murah | 5 / 5 | 100.0% |
| 19 | mobil hatchback mewah | 0 / 5 | 0.0% |
| 20 | mobil mpv murah | 1 / 5 | 20.0% |
| 21 | mobil mpv keluarga | 5 / 5 | 100.0% |
| 22 | mobil sedan mewah | 5 / 5 | 100.0% |
| 23 | mobil 5 penumpang murah | 3 / 5 | 60.0% |
| 24 | mobil 7 penumpang keluarga | 2 / 5 | 40.0% |
| 25 | mobil mewah jarak jauh | 5 / 5 | 100.0% |
| 26 | mobil hyundai mewah | 2 / 5 | 40.0% |
| 27 | mobil wuling murah | 2 / 5 | 40.0% |
| 28 | mobil byd mewah | 0 / 5 | 0.0% |
| 29 | mobil tesla mewah | 2 / 5 | 40.0% |
| 30 | mobil suv jarak jauh | 5 / 5 | 100.0% |
| 31 | mobil hatchback jarak jauh | 5 / 5 | 100.0% |
| 32 | mobil mpv jarak jauh | 4 / 5 | 80.0% |
| 33 | mobil sedan jarak jauh | 5 / 5 | 100.0% |
| 34 | mobil 5 penumpang jarak jauh | 5 / 5 | 100.0% |
| 35 | mobil 7 penumpang jarak jauh | 5 / 5 | 100.0% |
| 36 | mobil dengan airbag | 5 / 5 | 100.0% |
| 37 | mobil dengan abs | 5 / 5 | 100.0% |
| 38 | mobil dengan kamera belakang | 5 / 5 | 100.0% |
| 39 | mobil dengan sensor parkir | 5 / 5 | 100.0% |
| 40 | mobil dengan cruise control | 0 / 5 | 0.0% |
| 41 | mobil wuling hatchback | 2 / 5 | 40.0% |
| 42 | mobil hyundai suv | 3 / 5 | 60.0% |
| 43 | mobil byd suv | 2 / 5 | 40.0% |
| 44 | mobil tesla sedan | 2 / 5 | 40.0% |
| 45 | mobil bmw mewah | 5 / 5 | 100.0% |
| 46 | mobil gwm murah | 0 / 5 | 0.0% |
| 47 | mobil gac suv | 2 / 5 | 40.0% |
| 48 | mobil chery suv | 2 / 5 | 40.0% |
| 49 | mobil dfsk murah | 1 / 5 | 20.0% |
| 50 | mobil mini hatchback | 2 / 5 | 40.0% |

## Tabel Detail Pengujian 100 Kueri

| No | Kueri | Jumlah Hasil Relevan di Top 5 | Nilai Precision |
|---|---|---|---|
| 1 | mobil murah | 3 / 5 | 60.0% |
| 2 | mobil mewah | 5 / 5 | 100.0% |
| 3 | mobil harga menengah | 4 / 5 | 80.0% |
| 4 | mobil suv | 5 / 5 | 100.0% |
| 5 | mobil hatchback | 5 / 5 | 100.0% |
| 6 | mobil mpv | 5 / 5 | 100.0% |
| 7 | mobil sedan | 5 / 5 | 100.0% |
| 8 | mobil 4 penumpang | 5 / 5 | 100.0% |
| 9 | mobil 5 penumpang | 5 / 5 | 100.0% |
| 10 | mobil 7 penumpang | 5 / 5 | 100.0% |
| 11 | mobil jarak jauh | 5 / 5 | 100.0% |
| 12 | mobil hyundai | 4 / 5 | 80.0% |
| 13 | mobil wuling | 5 / 5 | 100.0% |
| 14 | mobil byd | 5 / 5 | 100.0% |
| 15 | mobil tesla | 3 / 5 | 60.0% |
| 16 | mobil suv murah | 3 / 5 | 60.0% |
| 17 | mobil suv mewah | 5 / 5 | 100.0% |
| 18 | mobil hatchback murah | 5 / 5 | 100.0% |
| 19 | mobil hatchback mewah | 0 / 5 | 0.0% |
| 20 | mobil mpv murah | 1 / 5 | 20.0% |
| 21 | mobil mpv keluarga | 5 / 5 | 100.0% |
| 22 | mobil sedan mewah | 5 / 5 | 100.0% |
| 23 | mobil 5 penumpang murah | 3 / 5 | 60.0% |
| 24 | mobil 7 penumpang keluarga | 2 / 5 | 40.0% |
| 25 | mobil mewah jarak jauh | 5 / 5 | 100.0% |
| 26 | mobil hyundai mewah | 2 / 5 | 40.0% |
| 27 | mobil wuling murah | 2 / 5 | 40.0% |
| 28 | mobil byd mewah | 0 / 5 | 0.0% |
| 29 | mobil tesla mewah | 2 / 5 | 40.0% |
| 30 | mobil suv jarak jauh | 5 / 5 | 100.0% |
| 31 | mobil hatchback jarak jauh | 5 / 5 | 100.0% |
| 32 | mobil mpv jarak jauh | 4 / 5 | 80.0% |
| 33 | mobil sedan jarak jauh | 5 / 5 | 100.0% |
| 34 | mobil 5 penumpang jarak jauh | 5 / 5 | 100.0% |
| 35 | mobil 7 penumpang jarak jauh | 5 / 5 | 100.0% |
| 36 | mobil dengan airbag | 5 / 5 | 100.0% |
| 37 | mobil dengan abs | 5 / 5 | 100.0% |
| 38 | mobil dengan kamera belakang | 5 / 5 | 100.0% |
| 39 | mobil dengan sensor parkir | 5 / 5 | 100.0% |
| 40 | mobil dengan cruise control | 0 / 5 | 0.0% |
| 41 | mobil wuling hatchback | 2 / 5 | 40.0% |
| 42 | mobil hyundai suv | 3 / 5 | 60.0% |
| 43 | mobil byd suv | 2 / 5 | 40.0% |
| 44 | mobil tesla sedan | 2 / 5 | 40.0% |
| 45 | mobil bmw mewah | 5 / 5 | 100.0% |
| 46 | mobil gwm murah | 0 / 5 | 0.0% |
| 47 | mobil gac suv | 2 / 5 | 40.0% |
| 48 | mobil chery suv | 2 / 5 | 40.0% |
| 49 | mobil dfsk murah | 1 / 5 | 20.0% |
| 50 | mobil mini hatchback | 2 / 5 | 40.0% |
| 51 | motor murah | 5 / 5 | 100.0% |
| 52 | motor mewah | 3 / 5 | 60.0% |
| 53 | motor harga menengah | 0 / 5 | 0.0% |
| 54 | motor jarak jauh | 5 / 5 | 100.0% |
| 55 | motor cas cepat | 5 / 5 | 100.0% |
| 56 | motor fast charging | 5 / 5 | 100.0% |
| 57 | motor swap baterai | 2 / 5 | 40.0% |
| 58 | motor tukar baterai | 2 / 5 | 40.0% |
| 59 | motor polytron | 3 / 5 | 60.0% |
| 60 | motor alva | 5 / 5 | 100.0% |
| 61 | motor yadea | 5 / 5 | 100.0% |
| 62 | motor 1 baterai | 5 / 5 | 100.0% |
| 63 | motor 2 baterai | 5 / 5 | 100.0% |
| 64 | motor kecepatan tinggi | 3 / 5 | 60.0% |
| 65 | motor kencang | 3 / 5 | 60.0% |
| 66 | motor murah swap | 0 / 5 | 0.0% |
| 67 | motor mewah swap | 0 / 5 | 0.0% |
| 68 | motor polytron murah | 2 / 5 | 40.0% |
| 69 | motor alva mewah | 3 / 5 | 60.0% |
| 70 | motor alva swap | 0 / 5 | 0.0% |
| 71 | motor yadea murah | 5 / 5 | 100.0% |
| 72 | motor cas cepat murah | 4 / 5 | 80.0% |
| 73 | motor mewah jarak jauh | 3 / 5 | 60.0% |
| 74 | motor kecepatan tinggi mewah | 3 / 5 | 60.0% |
| 75 | motor dengan lithium | 5 / 5 | 100.0% |
| 76 | motor garansi panjang | 0 / 5 | 0.0% |
| 77 | motor polytron fox | 3 / 5 | 60.0% |
| 78 | motor alva cervo | 1 / 5 | 20.0% |
| 79 | motor yadea osta | 1 / 5 | 20.0% |
| 80 | motor 2 baterai jarak jauh | 5 / 5 | 100.0% |
| 81 | motor cas cepat swap | 0 / 5 | 0.0% |
| 82 | motor dengan direct charging | 5 / 5 | 100.0% |
| 83 | motor kecepatan tinggi swap | 0 / 5 | 0.0% |
| 84 | motor murah 1 baterai | 5 / 5 | 100.0% |
| 85 | motor mewah 2 baterai | 0 / 5 | 0.0% |
| 86 | motor dengan swap dan direct | 0 / 5 | 0.0% |
| 87 | motor jangkauan jauh | 0 / 5 | 0.0% |
| 88 | motor pengisian standar | 0 / 5 | 0.0% |
| 89 | motor murah meriah | 5 / 5 | 100.0% |
| 90 | motor mewah | 3 / 5 | 60.0% |
| 91 | motor harian murah | 5 / 5 | 100.0% |
| 92 | motor petualang jarak jauh | 5 / 5 | 100.0% |
| 93 | motor alva one | 1 / 5 | 20.0% |
| 94 | motor yadea velax | 1 / 5 | 20.0% |
| 95 | motor polytron fox 500 | 1 / 5 | 20.0% |
| 96 | motor dengan baterai sla | 0 / 5 | 0.0% |
| 97 | motor pengisian lama | 5 / 5 | 100.0% |
| 98 | motor dengan charging langsung | 0 / 5 | 0.0% |
| 99 | motor swap cepat | 0 / 5 | 0.0% |
| 100 | motor alva n3 | 1 / 5 | 20.0% |