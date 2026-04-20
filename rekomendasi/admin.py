from django.contrib import admin
from .models import Mobil, Motor

@admin.register(Mobil)
class MobilAdmin(admin.ModelAdmin):
    list_display = ('merek', 'harga', 'jarak_tempuh')
    search_fields = ('merek',)

@admin.register(Motor)
class MotorAdmin(admin.ModelAdmin):
    list_display = ('merek', 'harga', 'jarak_tempuh', 'sistem_pengisian')
    search_fields = ('merek',)
