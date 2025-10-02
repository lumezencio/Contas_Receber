# financeiro/models.py

from django.db import models
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN
from datetime import date
import re

class Cliente(models.Model):
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo
    
    def get_telefone_formatado(self):
        if not self.telefone:
            return "Não informado"
        numeros = re.sub(r'\D', '', self.telefone)
        if len(numeros) == 11:
            return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        elif len(numeros) == 10:
            return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        else:
            return self.telefone

class ContaReceber(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='contas', verbose_name="Cliente")
    descricao = models.CharField(max_length=200, verbose_name="Descrição")
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Valor Total")
    numero_parcelas = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Número de Parcelas")
    data_emissao = models.DateField(verbose_name="Data de Emissão")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['-data_emissao']

    def __str__(self):
        return f"{self.descricao} - {self.cliente.nome_completo}"

    def total_pago(self):
        total = self.parcelas.filter(status='pago').aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')

    def total_pendente(self):
        total = self.parcelas.filter(status__in=['aberto', 'vencido']).aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')

    def get_parcelas_info(self):
        total = self.parcelas.count()
        pagas = self.parcelas.filter(status='pago').count()
        return f"{pagas} de {total}"

    def get_status_info(self):
        total_parcelas = self.parcelas.count()
        if total_parcelas == 0:
            return {'text': 'Sem Parcelas', 'icon': 'bg-gray-400', 'badge': 'bg-gray-700 text-gray-300 border-gray-600'}
        parcelas_pagas = self.parcelas.filter(status='pago').count()
        if parcelas_pagas == total_parcelas:
            return {'text': 'Quitada', 'icon': 'bg-green-400', 'badge': 'bg-green-900/30 text-green-400 border border-green-700'}
        if self.parcelas.filter(status='vencido').exists():
            return {'text': 'Vencida', 'icon': 'bg-red-400 animate-pulse', 'badge': 'bg-red-900/30 text-red-400 border border-red-700'}
        if parcelas_pagas > 0:
            return {'text': 'Parcial', 'icon': 'bg-blue-400', 'badge': 'bg-blue-900/30 text-blue-400 border border-blue-700'}
        return {'text': 'Em Aberto', 'icon': 'bg-yellow-400', 'badge': 'bg-yellow-900/30 text-yellow-400 border border-yellow-700'}

    def get_percentual_pago(self):
        if self.valor_total == 0:
            return 0
        percentual = (self.total_pago() / self.valor_total) * 100
        return int(percentual.quantize(Decimal('1'), rounding=ROUND_DOWN))


class Parcela(models.Model):
    STATUS_CHOICES = [('aberto', 'Aberto'), ('pago', 'Pago'), ('vencido', 'Vencido')]
    conta = models.ForeignKey(ContaReceber, on_delete=models.CASCADE, related_name='parcelas', verbose_name="Conta")
    numero_parcela = models.IntegerField(verbose_name="Número da Parcela")
    valor_parcela = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Valor da Parcela")
    data_vencimento = models.DateField(verbose_name="Data de Vencimento")
    data_pagamento = models.DateField(blank=True, null=True, verbose_name="Data de Pagamento")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='aberto', verbose_name="Status")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Parcela"
        verbose_name_plural = "Parcelas"
        ordering = ['conta__id', 'numero_parcela']
        unique_together = ['conta', 'numero_parcela']

    def __str__(self):
        return f"Parcela {self.numero_parcela}/{self.conta.numero_parcelas} - {self.conta.descricao}"

    def save(self, *args, **kwargs):
        # Flag para controlar a recursão e o rebalanceamento
        rebalancear = kwargs.pop('rebalancear', True)
        
        # Lógica para detectar se o valor da parcela mudou
        valor_mudou = False
        if not self._state.adding and self.pk:
            try:
                versao_antiga = Parcela.objects.get(pk=self.pk)
                if versao_antiga.valor_parcela != self.valor_parcela:
                    valor_mudou = True
            except Parcela.DoesNotExist:
                pass

        # Lógica de atualização de status (executada antes de salvar)
        if self.data_pagamento:
            self.status = 'pago'
        elif self.status != 'pago' and self.data_vencimento < date.today():
            self.status = 'vencido'
        elif self.status != 'pago' and self.data_vencimento >= date.today():
            self.status = 'aberto'
        
        # Salva a alteração atual da parcela
        super().save(*args, **kwargs)

        # ==============================================================================
        # NOVA LÓGICA PROFISSIONAL DE REBALANCEAMENTO AUTOMÁTICO
        # ==============================================================================
        if valor_mudou and rebalancear:
            conta = self.conta
            
            # Calcula a soma de todas as parcelas após a alteração
            soma_atual = conta.parcelas.aggregate(s=Sum('valor_parcela'))['s'] or Decimal('0.00')
            
            # Calcula a diferença para o valor total da conta
            diferenca = conta.valor_total - soma_atual
            
            # Encontra a última parcela não paga (que não seja a que acabamos de editar)
            # É nela que a diferença será aplicada.
            ultima_parcela_ajustavel = conta.parcelas.filter(
                status__in=['aberto', 'vencido']
            ).exclude(pk=self.pk).order_by('-numero_parcela').first()

            if ultima_parcela_ajustavel:
                # Usa F() expression para uma atualização atômica e segura no banco de dados
                Parcela.objects.filter(pk=ultima_parcela_ajustavel.pk).update(
                    valor_parcela=F('valor_parcela') + diferenca
                )