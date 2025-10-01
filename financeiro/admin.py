# financeiro/admin.py

from django.contrib import admin
from .models import Cliente, ContaReceber, Parcela

# Configuração do Admin para Cliente
@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    # CORREÇÃO: 'data_cadastro' trocado para 'created_at'
    list_display = ('id', 'nome_completo', 'cpf_cnpj', 'telefone', 'created_at') 
    search_fields = ('nome_completo', 'cpf_cnpj', 'email')
    list_filter = ('created_at',) # CORREÇÃO
    ordering = ('nome_completo',)

# Configuração do Admin para ContaReceber
@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    # CORREÇÃO: 'data_lancamento' trocado para 'data_emissao'
    list_display = ('id', 'cliente', 'descricao', 'valor_total', 'numero_parcelas', 'data_emissao')
    search_fields = ('cliente__nome_completo', 'descricao')
    list_filter = ('data_emissao', 'cliente') # CORREÇÃO
    date_hierarchy = 'data_emissao' # CORREÇÃO
    ordering = ('-data_emissao',) # CORREÇÃO
    list_select_related = ('cliente',) 

# Configuração do Admin para Parcela
@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    # CORREÇÃO: 'conta_receber' trocado para 'conta'
    list_display = ('id', 'conta', 'numero_parcela', 'valor_parcela', 'data_vencimento', 'status', 'data_pagamento')
    search_fields = ('conta__cliente__nome_completo', 'conta__descricao') # CORREÇÃO
    list_filter = ('status', 'data_vencimento', 'data_pagamento')
    date_hierarchy = 'data_vencimento'
    ordering = ('data_vencimento',)
    list_select_related = ('conta', 'conta__cliente') # CORREÇÃO