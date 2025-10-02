# config/urls.py

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Mantém todas as URLs de autenticação (login, logout, etc.) sob /accounts/
    path('accounts/', include('django.contrib.auth.urls')),
    
    # CORREÇÃO: Todo o seu sistema agora vive sob o prefixo /dashboard/
    path('dashboard/', include('financeiro.urls')),
    
    # CORREÇÃO: A raiz do site (/) agora redireciona para a página de login.
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),
]