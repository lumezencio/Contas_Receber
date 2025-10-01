# financeiro/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Cliente, ContaReceber, Parcela


# ==============================================================================
# CONFIGURAÇÃO DO ADMIN - CLIENTE
# ==============================================================================

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    """Configuração avançada do admin para Cliente"""
    
    list_display = [
        'nome_completo',
        'cpf_cnpj_formatado',
        'email',
        'telefone',
        'status_badge',
        'total_contas',
        'data_cadastro_formatada'
    ]
    
    list_filter = [
        'ativo',
        'created_at',
    ]
    
    search_fields = [
        'nome_completo',
        'cpf_cnpj',
        'email',
        'telefone'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'total_contas',
        'total_divida',
        'total_pago'
    ]
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome_completo', 'cpf_cnpj', 'ativo')
        }),
        ('Contato', {
            'fields': ('email', 'telefone')
        }),
        ('Estatísticas', {
            'fields': ('total_contas', 'total_divida', 'total_pago'),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 25
    date_hierarchy = 'created_at'
    
    actions = ['ativar_clientes', 'desativar_clientes']
    
    def cpf_cnpj_formatado(self, obj):
        """Exibe CPF/CNPJ formatado ou N/A"""
        return obj.cpf_cnpj or format_html('<span style="color: #999;">N/A</span>')
    cpf_cnpj_formatado.short_description = 'CPF/CNPJ'
    
    def status_badge(self, obj):
        """Badge colorido para status ativo/inativo"""
        if obj.ativo:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">ATIVO</span>'
            )
        return format_html(
            '<span style="background: #dc3545; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">INATIVO</span>'
        )
    status_badge.short_description = 'Status'
    
    def total_contas(self, obj):
        """Quantidade de contas do cliente"""
        count = obj.contas.count()
        return format_html('<strong>{}</strong>', count)
    total_contas.short_description = 'Total de Contas'
    
    def total_divida(self, obj):
        """Total em aberto do cliente"""
        total = obj.get_total_divida()
        return format_html('<strong>R$ {:.2f}</strong>', total)
    total_divida.short_description = 'Total em Aberto'
    
    def total_pago(self, obj):
        """Total já pago pelo cliente"""
        total = obj.get_total_pago()
        return format_html('<strong style="color: green;">R$ {:.2f}</strong>', total)
    total_pago.short_description = 'Total Pago'
    
    def data_cadastro_formatada(self, obj):
        """Data de cadastro formatada"""
        return obj.created_at.strftime('%d/%m/%Y às %H:%M')
    data_cadastro_formatada.short_description = 'Cadastrado em'
    
    def ativar_clientes(self, request, queryset):
        """Ação para ativar clientes em lote"""
        updated = queryset.update(ativo=True)
        self.message_user(request, f'{updated} cliente(s) ativado(s) com sucesso.')
    ativar_clientes.short_description = 'Ativar clientes selecionados'
    
    def desativar_clientes(self, request, queryset):
        """Ação para desativar clientes em lote"""
        updated = queryset.update(ativo=False)
        self.message_user(request, f'{updated} cliente(s) desativado(s) com sucesso.')
    desativar_clientes.short_description = 'Desativar clientes selecionados'


# ==============================================================================
# CONFIGURAÇÃO DO ADMIN - PARCELA (INLINE)
# ==============================================================================

class ParcelaInline(admin.TabularInline):
    """Inline para exibir parcelas dentro de ContaReceber"""
    
    model = Parcela
    extra = 0
    can_delete = False
    
    fields = [
        'numero_parcela',
        'valor_parcela',
        'data_vencimento',
        'status',
        'data_pagamento'
    ]
    
    readonly_fields = [
        'numero_parcela',
        'valor_parcela',
        'data_vencimento'
    ]
    
    def has_add_permission(self, request, obj=None):
        """Desabilita adição manual de parcelas"""
        return False


# ==============================================================================
# CONFIGURAÇÃO DO ADMIN - CONTA A RECEBER
# ==============================================================================

@admin.register(ContaReceber)
class ContaReceberAdmin(admin.ModelAdmin):
    """Configuração avançada do admin para ContaReceber"""
    
    list_display = [
        'id',
        'cliente_link',
        'descricao_truncada',
        'valor_total_formatado',
        'numero_parcelas',
        'status_pagamento',
        'percentual_pago_display',
        'data_lancamento'
    ]
    
    list_filter = [
        'data_lancamento',
        'numero_parcelas',
        'created_at'
    ]
    
    search_fields = [
        'cliente__nome_completo',
        'descricao',
        'observacoes'
    ]
    
    readonly_fields = [
        'data_lancamento',
        'created_at',
        'updated_at',
        'total_pago_display',
        'total_pendente_display',
        'percentual_pago_display'
    ]
    
    fieldsets = (
        ('Informações da Conta', {
            'fields': (
                'cliente',
                'descricao',
                'valor_total',
                'numero_parcelas',
                'data_lancamento'
            )
        }),
        ('Observações', {
            'fields': ('observacoes',),
            'classes': ('collapse',)
        }),
        ('Estatísticas de Pagamento', {
            'fields': (
                'total_pago_display',
                'total_pendente_display',
                'percentual_pago_display'
            ),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [ParcelaInline]
    
    list_per_page = 25
    date_hierarchy = 'data_lancamento'
    
    def cliente_link(self, obj):
        """Link clicável para o cliente"""
        url = reverse('admin:financeiro_cliente_change', args=[obj.cliente.pk])
        return format_html('<a href="{}">{}</a>', url, obj.cliente.nome_completo)
    cliente_link.short_description = 'Cliente'
    
    def descricao_truncada(self, obj):
        """Descrição truncada"""
        if len(obj.descricao) > 50:
            return f"{obj.descricao[:50]}..."
        return obj.descricao
    descricao_truncada.short_description = 'Descrição'
    
    def valor_total_formatado(self, obj):
        """Valor total formatado"""
        return format_html('<strong>R$ {:.2f}</strong>', obj.valor_total)
    valor_total_formatado.short_description = 'Valor Total'
    
    def status_pagamento(self, obj):
        """Badge de status do pagamento"""
        if obj.is_quitada():
            return format_html(
                '<span style="background: #28a745; color: white; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">QUITADA</span>'
            )
        else:
            return format_html(
                '<span style="background: #ffc107; color: #000; padding: 3px 10px; '
                'border-radius: 3px; font-size: 11px;">EM ABERTO</span>'
            )
    status_pagamento.short_description = 'Status'
    
    def percentual_pago_display(self, obj):
        """Exibe percentual pago com barra de progresso"""
        percentual = obj.get_percentual_pago()
        cor = '#28a745' if percentual == 100 else '#ffc107' if percentual > 0 else '#dc3545'
        
        return format_html(
            '<div style="width: 100px; background: #eee; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background: {}; color: white; text-align: center; '
            'padding: 2px 0; font-size: 11px;">{:.0f}%</div></div>',
            percentual, cor, percentual
        )
    percentual_pago_display.short_description = '% Pago'
    
    def total_pago_display(self, obj):
        """Total já pago formatado"""
        total = obj.get_total_pago()
        return format_html('<strong style="color: green;">R$ {:.2f}</strong>', total)
    total_pago_display.short_description = 'Total Pago'
    
    def total_pendente_display(self, obj):
        """Total pendente formatado"""
        total = obj.get_total_pendente()
        cor = 'red' if total > 0 else 'green'
        return format_html('<strong style="color: {};">R$ {:.2f}</strong>', cor, total)
    total_pendente_display.short_description = 'Total Pendente'


# ==============================================================================
# CONFIGURAÇÃO DO ADMIN - PARCELA
# ==============================================================================

@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    """Configuração avançada do admin para Parcela"""
    
    list_display = [
        'id',
        'conta_link',
        'numero_parcela_display',
        'valor_formatado',
        'data_vencimento',
        'status_badge',
        'data_pagamento',
        'dias_atraso_display'
    ]
    
    list_filter = [
        'status',
        'data_vencimento',
        'data_pagamento',
        'created_at'
    ]
    
    search_fields = [
        'conta_receber__cliente__nome_completo',
        'conta_receber__descricao'
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'dias_atraso_display'
    ]
    
    fieldsets = (
        ('Informações da Parcela', {
            'fields': (
                'conta_receber',
                'numero_parcela',
                'valor_parcela'
            )
        }),
        ('Datas', {
            'fields': (
                'data_vencimento',
                'data_pagamento',
                'status'
            )
        }),
        ('Informações Adicionais', {
            'fields': ('dias_atraso_display',),
            'classes': ('collapse',)
        }),
        ('Metadados', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    list_per_page = 50
    date_hierarchy = 'data_vencimento'
    
    actions = ['marcar_como_paga', 'estornar_pagamento']
    
    def conta_link(self, obj):
        """Link para a conta relacionada"""
        url = reverse('admin:financeiro_contareceber_change', args=[obj.conta_receber.pk])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"{obj.conta_receber.cliente.nome_completo} - {obj.conta_receber.descricao[:30]}"
        )
    conta_link.short_description = 'Conta'
    
    def numero_parcela_display(self, obj):
        """Exibe número da parcela formatado"""
        return format_html(
            '<strong>{}/{}</strong>',
            obj.numero_parcela,
            obj.conta_receber.numero_parcelas
        )
    numero_parcela_display.short_description = 'Parcela'
    
    def valor_formatado(self, obj):
        """Valor formatado"""
        return format_html('<strong>R$ {:.2f}</strong>', obj.valor_parcela)
    valor_formatado.short_description = 'Valor'
    
    def status_badge(self, obj):
        """Badge colorido para status"""
        cores = {
            'A_VENCER': ('#17a2b8', 'A VENCER'),
            'VENCIDA': ('#dc3545', 'VENCIDA'),
            'PAGA': ('#28a745', 'PAGA'),
            'CANCELADA': ('#6c757d', 'CANCELADA'),
        }
        cor, texto = cores.get(obj.status, ('#6c757d', obj.status))
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            cor, texto
        )
    status_badge.short_description = 'Status'
    
    def dias_atraso_display(self, obj):
        """Exibe dias de atraso se aplicável"""
        dias = obj.dias_atraso()
        if dias > 0:
            return format_html(
                '<strong style="color: red;">{} dia(s)</strong>',
                dias
            )
        return format_html('<span style="color: green;">-</span>')
    dias_atraso_display.short_description = 'Dias em Atraso'
    
    def marcar_como_paga(self, request, queryset):
        """Ação para marcar parcelas como pagas"""
        from datetime import date
        updated = 0
        for parcela in queryset:
            if parcela.status != 'PAGA':
                parcela.status = 'PAGA'
                parcela.data_pagamento = date.today()
                parcela.save()
                updated += 1
        
        self.message_user(request, f'{updated} parcela(s) marcada(s) como paga(s).')
    marcar_como_paga.short_description = 'Marcar como paga'
    
    def estornar_pagamento(self, request, queryset):
        """Ação para estornar pagamentos"""
        from datetime import date
        updated = 0
        for parcela in queryset.filter(status='PAGA'):
            parcela.data_pagamento = None
            if parcela.data_vencimento < date.today():
                parcela.status = 'VENCIDA'
            else:
                parcela.status = 'A_VENCER'
            parcela.save()
            updated += 1
        
        self.message_user(request, f'{updated} pagamento(s) estornado(s).')
    estornar_pagamento.short_description = 'Estornar pagamento'


# ==============================================================================
# CUSTOMIZAÇÃO DO ADMIN SITE
# ==============================================================================

admin.site.site_header = 'Sistema Financeiro - Administração'
admin.site.site_title = 'Financeiro Admin'
admin.site.index_title = 'Painel de Controle Financeiro'
# ==============================================================================versaoI