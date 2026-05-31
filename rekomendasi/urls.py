from django.urls import path
from . import views

urlpatterns = [
    path('', views.halaman_rekomendasi, name='beranda'),
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('detail/<str:jenis>/<int:id>/', views.kendaraan_detail, name='detail_kendaraan'),
    path('admin-dashboard/hapus/<str:jenis>/<int:id>/', views.hapus_kendaraan, name='hapus_kendaraan'),
    path('admin-dashboard/update-gambar/<str:jenis>/<int:id>/', views.update_gambar_kendaraan, name='update_gambar_kendaraan'),
    path('admin-dashboard/update-data/<str:jenis>/<int:id>/', views.update_data_kendaraan, name='update_data_kendaraan'),
    path('admin-dashboard/tambah-data/<str:jenis>/', views.tambah_data_kendaraan, name='tambah_data_kendaraan'),
    path('admin-dashboard/upload-interior/<int:id>/', views.upload_foto_interior, name='upload_foto_interior'),
    path('admin-dashboard/hapus-interior/<int:id>/', views.hapus_foto_interior, name='hapus_foto_interior'),
    path('admin-dashboard/visualisasi/', views.visualisasi_algoritma, name='visualisasi_algoritma'),
]