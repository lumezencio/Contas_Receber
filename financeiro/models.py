# financeiro/models.py

from django.db import models
from django.db.models import Sum
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date


class Cliente(models.Model):
    nome_completo = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CPF/CNPJ")
    telefone = models.CharField(max_length=20, verbose_name="Telefone")
    email = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco = models.TextField(blank=True, null=True, verbose_name="Endereço")
    observacoes = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo


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
        """Calcula o valor total já pago nas parcelas."""
        total = self.parcelas.filter(status='pago').aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')

    def total_pendente(self):
        """Calcula o valor ainda em aberto (aberto + vencido)."""
        total = self.parcelas.filter(status__in=['aberto', 'vencido']).aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')

    def get_parcelas_info(self):
        """Retorna uma string com o progresso das parcelas (ex: "3 de 12")."""
        total = self.parcelas.count()
        pagas = self.parcelas.filter(status='pago').count()
        return f"{pagas} de {total}"

    def get_status_info(self):
        """
        Retorna um dicionário com o texto do status e as classes CSS do Tailwind.
        Esta é a "fonte da verdade" para a exibição do status.
        """
        total_parcelas = self.parcelas.count()
        if total_parcelas == 0:
            return {'text': 'Sem Parcelas', 'classes': 'bg-gray-700 text-gray-300 border-gray-600'}

        parcelas_pagas = self.parcelas.filter(status='pago').count()
        
        if parcelas_pagas == total_parcelas:
            return {
                'text': 'Quitada',
                'icon_classes': 'bg-green-400',
                'badge_classes': 'bg-green-900/30 text-green-400 border border-green-700'
            }

        if self.parcelas.filter(status='vencido').exists():
            return {
                'text': 'Vencida',
                'icon_classes': 'bg-red-400 animate-pulse',
                'badge_classes': 'bg-red-900/30 text-red-400 border border-red-700'
            }

        if parcelas_pagas > 0:
            return {
                'text': 'Parcialmente Pago',
                'icon_classes': 'bg-blue-400',
                'badge_classes': 'bg-blue-900/30 text-blue-400 border border-blue-700'
            }
        
        return {
            'text': 'Em Aberto',
            'icon_classes': 'bg-yellow-400',
            'badge_classes': 'bg-yellow-900/30 text-yellow-400 border border-yellow-700'
        }


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
        if self.data_pagamento:
            self.status = 'pago'
        elif self.status != 'pago' and self.data_vencimento < date.today():
            self.status = 'vencido'
        elif self.status != 'pago' and self.data_vencimento >= date.today():
            self.status = 'aberto'
        super().save(*args, **kwargs)