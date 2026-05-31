import requests
from django import forms
from django.contrib.admin.forms import AdminAuthenticationForm
from django.conf import settings
from django.core.exceptions import ValidationError

class TurnstileAdminAuthenticationForm(AdminAuthenticationForm):
    def clean(self):
        cleaned_data = super().clean()
        
        # Turnstile token sent from frontend
        turnstile_response = self.request.POST.get('cf-turnstile-response')
        
        if not turnstile_response:
            raise ValidationError("Silakan selesaikan verifikasi keamanan (Turnstile).")
            
        # Verify with Cloudflare API
        verify_url = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
        payload = {
            'secret': settings.TURNSTILE_SECRET_KEY,
            'response': turnstile_response,
            'remoteip': self.request.META.get('REMOTE_ADDR')
        }
        
        try:
            response = requests.post(verify_url, data=payload, timeout=5)
            result = response.json()
            if not result.get('success'):
                raise ValidationError("Verifikasi keamanan (Turnstile) gagal. Silakan coba lagi.")
        except requests.exceptions.RequestException:
            raise ValidationError("Gagal terhubung ke Cloudflare Turnstile. Silakan coba lagi nanti.")
            
        return cleaned_data
