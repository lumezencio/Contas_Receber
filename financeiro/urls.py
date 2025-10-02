# financeiro/urls.py

"""
Arquivo de configuração de URLs para o aplicativo 'financeiro'.

Define todas as rotas específicas da aplicação, como dashboard, CRUD de clientes,
contas, parcelas e geração de relatórios.
"""

from django.urls import path
from . import views

# Define o namespace da aplicação. Essencial para evitar conflito de nomes de URLs
# e para ser usado nos templates (ex: {% url 'financeiro:dashboard' %}).
app_name = 'financeiro'

urlpatterns = [
    # Acessado via /dashboard/
    path('', views.index, name='dashboard'), 
    
    # Acessado via /dashboard/signup/
    path('signup/', views.signup, name='signup'),
    
    # --- CRUD de Clientes ---
    # Acessado via /dashboard/clientes/
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'), 
    path('clientes/editar/<int:pk>/', views.cliente_update, name='cliente_update'),
    path('clientes/excluir/<int:pk>/', views.cliente_delete, name='cliente_delete'),

    # --- CRUD de Contas a Receber ---
    # Acessado via /dashboard/contas/
    path('contas/', views.conta_list, name='conta_list'),
    path('contas/nova/', views.conta_create, name='conta_create'),
    path('contas/<int:pk>/', views.conta_detail, name='conta_detail'),
    path('contas/editar/<int:pk>/', views.conta_update, name='conta_update'),
    path('contas/excluir/<int:pk>/', views.conta_delete, name='conta_delete'),
    
    # --- Ações de Parcelas ---
    path('parcela/editar/<int:pk>/', views.parcela_update, name='parcela_update'),
    path('parcela/dar-baixa/<int:pk>/', views.parcela_dar_baixa, name='parcela_dar_baixa'),
    path('parcela/estornar/<int:pk>/', views.parcela_estornar, name='parcela_estornar'),
    
    # --- Documentos ---
    path('parcelas/<int:pk>/recibo/', views.gerar_recibo_pdf, name='gerar_recibo_pdf'),

    # --- Relatórios ---
    path('relatorio/cliente/<int:pk>/', views.relatorio_cliente_html, name='relatorio_cliente_html'),
    path('relatorio/cliente/pdf/<int:pk>/', views.relatorio_cliente_pdf, name='relatorio_cliente_pdf'),
]