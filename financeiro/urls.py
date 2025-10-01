# financeiro/urls.py

from django.urls import path
from . import views

app_name = 'financeiro'

urlpatterns = [
    # Dashboard
    path('', views.index, name='index'),
    
    # Clientes
    path('clientes/', views.cliente_list, name='cliente_list'),
    path('clientes/novo/', views.cliente_create, name='cliente_create'),
    path('clientes/<int:pk>/', views.cliente_detail, name='cliente_detail'),
    path('clientes/<int:pk>/editar/', views.cliente_update, name='cliente_update'),
    path('clientes/<int:pk>/deletar/', views.cliente_delete, name='cliente_delete'),
    
    # Contas a Receber
    path('contas/', views.conta_list, name='conta_list'),
    path('contas/nova/', views.conta_create, name='conta_create'),
    path('contas/<int:pk>/', views.conta_detail, name='conta_detail'),
    path('contas/<int:pk>/editar/', views.conta_update, name='conta_update'),
    path('contas/<int:pk>/deletar/', views.conta_delete, name='conta_delete'),
    
    # Parcelas
    path('parcelas/<int:pk>/editar/', views.parcela_update, name='parcela_update'),
    path('parcelas/<int:pk>/baixa/', views.parcela_dar_baixa, name='parcela_dar_baixa'),
    path('parcelas/<int:pk>/estornar/', views.parcela_estornar, name='parcela_estornar'),
    path('parcelas/<int:pk>/recibo/', views.gerar_recibo_pdf, name='gerar_recibo_pdf'),
    
    # Relatórios
    path('relatorio/cliente/<int:pk>/', views.relatorio_cliente_html, name='relatorio_cliente_html'),
    path('relatorio/cliente/pdf/<int:pk>/', views.relatorio_cliente_pdf, name='relatorio_cliente_pdf'),
]