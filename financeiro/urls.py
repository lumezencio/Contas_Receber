# financeiro/urls.py

from django.urls import path
from . import views

# Esta linha OBRIGA o uso do prefixo 'financeiro:' nos templates
app_name = 'financeiro'

urlpatterns = [
    # Rota Principal (Dashboard)
    path('', views.index, name='index'),
    
    # Rota de Cadastro de Usuário
    path('signup/', views.signup, name='signup'),
    
    # Rotas de Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'), 
    path('clientes/editar/<int:pk>/', views.cliente_update, name='cliente_update'),
    path('clientes/excluir/<int:pk>/', views.cliente_delete, name='cliente_delete'),

    # Rotas de Contas a Receber
    path('contas/', views.conta_list, name='conta_list'),
    path('contas/nova/', views.conta_create, name='conta_create'),
    path('contas/<int:pk>/', views.conta_detail, name='conta_detail'),
    path('contas/editar/<int:pk>/', views.conta_update, name='conta_update'),
    path('contas/excluir/<int:pk>/', views.conta_delete, name='conta_delete'),
    
    # Rotas de Ações de Parcelas
    path('parcela/editar/<int:pk>/', views.parcela_update, name='parcela_update'),
    path('parcela/dar-baixa/<int:pk>/', views.parcela_dar_baixa, name='parcela_dar_baixa'),
    path('parcela/estornar/<int:pk>/', views.parcela_estornar, name='parcela_estornar'),
    
    # Rota de Documentos (Recibo)
    path('parcelas/<int:pk>/recibo/', views.gerar_recibo_pdf, name='gerar_recibo_pdf'),

    # Rotas de Relatórios
    path('relatorio/cliente/<int:pk>/', views.relatorio_cliente_html, name='relatorio_cliente_html'),
    path('relatorio/cliente/pdf/<int:pk>/', views.relatorio_cliente_pdf, name='relatorio_cliente_pdf'),
]