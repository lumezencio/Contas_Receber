# config/urls.py

"""
Arquivo de configuração de URLs principal do projeto.

Responsabilidades:
1. Mapear a URL do painel de administração do Django.
2. Incluir o conjunto de URLs do sistema de autenticação padrão do Django.
3. Delegar todas as URLs da aplicação principal para o arquivo de URLs do app 'financeiro'.
4. Redirecionar a raiz do site para a página de login.
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic.base import RedirectView

urlpatterns = [
    # Rota para a área de administração interna do Django.
    # Acessível em /admin/
    path('admin/', admin.site.urls),
    
    # Inclui todas as URLs do sistema de autenticação do Django (login, logout, reset de senha, etc.).
    # Ficarão acessíveis sob o prefixo /accounts/ (ex: /accounts/login/).
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Delega todas as URLs que começam com /dashboard/ para serem gerenciadas
    # pelo arquivo 'urls.py' do nosso aplicativo 'financeiro'.
    path('dashboard/', include('financeiro.urls')),
    
    # Rota raiz do site ('/'). Redireciona permanentemente para a tela de login.
    # Garante que a primeira página que qualquer usuário vê seja a de login.
    path('', RedirectView.as_view(url='/accounts/login/', permanent=False), name='index'),
]