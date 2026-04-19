from django.urls import path
from . import views

urlpatterns = [
    path('', views.halaman_rekomendasi, name='beranda'),
    path('admin-dashboard/', views.dashboard_admin, name='dashboard_admin'),
    path('detail/<str:jenis>/<int:id>/', views.kendaraan_detail, name='detail_kendaraan'),
    path('admin-dashboard/hapus/<str:jenis>/<int:id>/', views.hapus_kendaraan, name='hapus_kendaraan'),
    path('admin-dashboard/update-gambar/<str:jenis>/<int:id>/', views.update_gambar_kendaraan, name='update_gambar_kendaraan'),
    path('admin-dashboard/update-data/<str:jenis>/<int:id>/', views.update_data_kendaraan, name='update_data_kendaraan'),
]