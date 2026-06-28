"""
URL configuration for ev_config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rekomendasi.forms import TurnstileAdminAuthenticationForm
from rekomendasi.views import github_webhook

# Override admin login form with Turnstile validation
admin.site.login_form = TurnstileAdminAuthenticationForm

urlpatterns = [
    path('admin/', admin.site.urls),
    # Path deployment otomatis berbasis GitHub Webhooks
    path('proses-deploy-otomatis-rahasia-99/', github_webhook, name='github_webhook'),
    path('', include('rekomendasi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
