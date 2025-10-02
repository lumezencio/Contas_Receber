# financeiro/models.py

from django.db import models, transaction
from django.db.models import Sum, F
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal, ROUND_DOWN
from datetime import date
import re
from typing import Dict, Union

class ClienteManager(models.Manager):
    """Manager customizado para o modelo Cliente, otimizando queries comuns."""
    def get_ativos(self):
        """Retorna um QuerySet contendo apenas clientes marcados como ativos."""
        return self.filter(ativo=True)

class Cliente(models.Model):
    """Representa um cliente no sistema, seja pessoa física ou jurídica."""
    nome_completo: str = models.CharField(max_length=200, verbose_name="Nome Completo")
    cpf_cnpj: Union[str, None] = models.CharField(max_length=18, blank=True, null=True, verbose_name="CPF/CNPJ")
    telefone: str = models.CharField(max_length=20, verbose_name="Telefone")
    email: Union[str, None] = models.EmailField(blank=True, null=True, verbose_name="E-mail")
    endereco: Union[str, None] = models.TextField(blank=True, null=True, verbose_name="Endereço")
    observacoes: Union[str, None] = models.TextField(blank=True, null=True, verbose_name="Observações")
    ativo: bool = models.BooleanField(default=True, verbose_name="Cliente Ativo")
    created_at: date = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at: date = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    objects = ClienteManager()

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome_completo']

    def __str__(self) -> str:
        return self.nome_completo
    
    def get_telefone_formatado(self) -> str:
        """Retorna o número de telefone formatado com uma máscara profissional."""
        if not self.telefone: return "Não informado"
        numeros = re.sub(r'\D', '', self.telefone)
        if len(numeros) == 11: return f"({numeros[:2]}) {numeros[2:7]}-{numeros[7:]}"
        if len(numeros) == 10: return f"({numeros[:2]}) {numeros[2:6]}-{numeros[6:]}"
        return self.telefone

class ContaReceber(models.Model):
    """Representa uma obrigação financeira a ser recebida de um Cliente."""
    cliente: Cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name='contas', verbose_name="Cliente")
    descricao: str = models.CharField(max_length=200, verbose_name="Descrição")
    valor_total: Decimal = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))], verbose_name="Valor Total")
    numero_parcelas: int = models.IntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Número de Parcelas")
    data_emissao: date = models.DateField(verbose_name="Data de Emissão")
    observacoes: Union[str, None] = models.TextField(blank=True, null=True, verbose_name="Observações")
    created_at: date = models.DateTimeField(auto_now_add=True, verbose_name="Criado em")
    updated_at: date = models.DateTimeField(auto_now=True, verbose_name="Atualizado em")

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['-data_emissao']

    def __str__(self) -> str:
        return f"{self.descricao} - {self.cliente.nome_completo}"

    def total_pago(self) -> Decimal:
        """Calcula a soma dos valores de todas as parcelas pagas desta conta."""
        total = self.parcelas.filter(status='pago').aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')

    def total_pendente(self) -> Decimal:
        """Calcula a soma dos valores de todas as parcelas não pagas (em aberto ou vencidas)."""
        total = self.parcelas.filter(status__in=['aberto', 'vencido']).aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')

    def get_parcelas_info(self) -> str:
        """Retorna uma string informativa sobre o progresso das parcelas (ex: '3 de 12')."""
        total = self.parcelas.count()
        pagas = self.parcelas.filter(status='pago').count()
        return f"{pagas} de {total}"

    def get_status_info(self) -> Dict[str, str]:
        """Retorna um dicionário com o texto do status e classes CSS para exibição no template."""
        total_parcelas = self.parcelas.count()
        if total_parcelas == 0: return {'text': 'Sem Parcelas', 'icon': 'bg-gray-400', 'badge': 'bg-gray-700 text-gray-300 border-gray-600'}
        parcelas_pagas = self.parcelas.filter(status='pago').count()
        if parcelas_pagas == total_parcelas and self.total_pago() == self.valor_total: return {'text': 'Quitada', 'icon': 'bg-green-400', 'badge': 'bg-green-900/30 text-green-400 border border-green-700'}
        if self.parcelas.filter(status='vencido').exists(): return {'text': 'Vencida', 'icon': 'bg-red-400 animate-pulse', 'badge': 'bg-red-900/30 text-red-400 border border-red-700'}
        if parcelas_pagas > 0: return {'text': 'Parcial', 'icon': 'bg-blue-400', 'badge': 'bg-blue-900/30 text-blue-400 border border-blue-700'}
        return {'text': 'Em Aberto', 'icon': 'bg-yellow-400', 'badge': 'bg-yellow-900/30 text-yellow-400 border border-yellow-700'}

    def get_percentual_pago(self) -> int:
        """Calcula a porcentagem do valor total que já foi pago, para barras de progresso."""
        if self.valor_total <= 0: return 0
        percentual = (self.total_pago() / self.valor_total) * 100
        return int(percentual.quantize(Decimal('1'), rounding=ROUND_DOWN))

class Parcela(models.Model):
    """Representa uma única parcela de uma Conta a Receber."""
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

    def __str__(self) -> str:
        return f"Parcela {self.numero_parcela}/{self.conta.numero_parcelas} - {self.conta.descricao}"

    def save(self, *args, **kwargs):
        """
        Sobrescreve o método save para incluir lógicas de negócio avançadas:
        1. Atualiza o status da parcela com base na data de pagamento/vencimento.
        2. Se o valor de uma parcela for alterado, rebalanceia automaticamente
           o valor das outras parcelas em aberto para manter a soma total.
        """
        if self.data_pagamento: self.status = 'pago'
        elif self.status != 'pago' and self.data_vencimento < date.today(): self.status = 'vencido'
        elif self.status != 'pago': self.status = 'aberto'

        if not self._state.adding and self.pk:
            try:
                versao_antiga = Parcela.objects.get(pk=self.pk)
                if versao_antiga.valor_parcela != self.valor_parcela and self.status != 'pago':
                    with transaction.atomic():
                        super().save(*args, **kwargs)
                        conta = self.conta
                        parcelas_ajustaveis = conta.parcelas.filter(status__in=['aberto', 'vencido']).exclude(pk=self.pk).order_by('numero_parcela')
                        num_ajustaveis = parcelas_ajustaveis.count()
                        if num_ajustaveis > 0:
                            soma_nao_ajustaveis = conta.parcelas.exclude(id__in=parcelas_ajustaveis.values_list('id', flat=True)).aggregate(s=Sum('valor_parcela'))['s'] or Decimal('0.00')
                            saldo_a_distribuir = conta.valor_total - soma_nao_ajustaveis
                            valor_base = (saldo_a_distribuir / num_ajustaveis).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
                            parcelas_ajustaveis.update(valor_parcela=valor_base)
                            soma_distribuida = valor_base * num_ajustaveis
                            residuo = saldo_a_distribuir - soma_distribuida
                            ultima_parcela = parcelas_ajustaveis.last()
                            if ultima_parcela and residuo != 0:
                                ultima_parcela.valor_parcela += residuo
                                ultima_parcela.save(update_fields=['valor_parcela'])
                    return
            except Parcela.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)