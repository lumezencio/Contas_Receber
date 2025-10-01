# financeiro/urls.py

from django.urls import path
# Importa o arquivo views.py do mesmo diretório (financeiro)
from . import views

# Definir o app_name é altamente recomendado no Django.
# Isso cria um "namespace" para as URLs desta aplicação, evitando colisões com outras apps.
app_name = 'financeiro'

urlpatterns = [
    # Rota para a listagem de contas (a página que estava dando erro)
    # Exemplo: /contas/
    path('contas/', views.conta_list, name='conta_list'),
    
    # ROTA CRUCIAL: Esta linha define a rota que o template estava procurando.
    # O parâmetro name='conta_create' resolve o erro NoReverseMatch.
    # Exemplo: /contas/nova/
    path('contas/nova/', views.conta_create, name='conta_create'),

    # Você provavelmente terá outras rotas aqui no futuro, como:
    # path('contas/editar/<int:pk>/', views.conta_update, name='conta_update'),
    # path('contas/deletar/<int:pk>/', views.conta_delete, name='conta_delete'),
]