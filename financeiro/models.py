# financeiro/models.py

from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from decimal import Decimal
from datetime import date


class Cliente(models.Model):
    """
    Modelo para representar clientes do sistema
    """
    nome_completo = models.CharField(
        max_length=200, 
        verbose_name="Nome Completo"
    )
    cpf_cnpj = models.CharField(
        max_length=18, 
        blank=True, 
        null=True, 
        verbose_name="CPF/CNPJ"
    )
    telefone = models.CharField(
        max_length=20, 
        verbose_name="Telefone"
    )
    email = models.EmailField(
        blank=True, 
        null=True, 
        verbose_name="E-mail"
    )
    endereco = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Endereço"
    )
    observacoes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observações"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ['nome_completo']

    def __str__(self):
        return self.nome_completo
    
    def total_a_receber(self):
        """Retorna o total a receber deste cliente"""
        from django.db.models import Sum
        total = Parcela.objects.filter(
            conta__cliente=self,
            status__in=['aberto', 'vencido']
        ).aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')
    
    def total_recebido(self):
        """Retorna o total já recebido deste cliente"""
        from django.db.models import Sum
        total = Parcela.objects.filter(
            conta__cliente=self,
            status='pago'
        ).aggregate(total=Sum('valor_parcela'))['total']
        return total or Decimal('0.00')


class ContaReceber(models.Model):
    """
    Modelo para representar contas a receber
    """
    cliente = models.ForeignKey(
        Cliente, 
        on_delete=models.PROTECT, 
        related_name='contas',
        verbose_name="Cliente"
    )
    descricao = models.CharField(
        max_length=200, 
        verbose_name="Descrição"
    )
    valor_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor Total"
    )
    numero_parcelas = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name="Número de Parcelas"
    )
    data_emissao = models.DateField(
        verbose_name="Data de Emissão"
    )
    observacoes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observações"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Conta a Receber"
        verbose_name_plural = "Contas a Receber"
        ordering = ['-data_emissao']

    def __str__(self):
        return f"{self.descricao} - {self.cliente.nome_completo}"

    def calcular_valor_pago(self):
        """Calcula o valor total já pago nas parcelas"""
        total = self.parcelas.filter(status='pago').aggregate(
            total=models.Sum('valor_parcela')
        )['total']
        return total or Decimal('0.00')

    def calcular_valor_aberto(self):
        """Calcula o valor ainda em aberto"""
        return self.valor_total - self.calcular_valor_pago()

    def get_status_display(self):
        """Retorna status da conta baseado nas parcelas"""
        total_parcelas = self.parcelas.count()
        if total_parcelas == 0:
            return 'Sem Parcelas'
        
        parcelas_pagas = self.parcelas.filter(status='pago').count()
        
        if parcelas_pagas == total_parcelas:
            return 'Quitada'
        elif parcelas_pagas > 0:
            return 'Parcialmente Pago'
        elif self.parcelas.filter(status='vencido').exists():
            return 'Vencida'
        else:
            return 'Em Aberto'


class Parcela(models.Model):
    """
    Modelo para representar parcelas de uma conta a receber
    """
    STATUS_CHOICES = [
        ('aberto', 'Aberto'),
        ('pago', 'Pago'),
        ('vencido', 'Vencido'),
    ]

    conta = models.ForeignKey(
        ContaReceber, 
        on_delete=models.CASCADE, 
        related_name='parcelas',
        verbose_name="Conta"
    )
    numero_parcela = models.IntegerField(
        verbose_name="Número da Parcela"
    )
    valor_parcela = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Valor da Parcela"
    )
    data_vencimento = models.DateField(
        verbose_name="Data de Vencimento"
    )
    data_pagamento = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Data de Pagamento"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='aberto', 
        verbose_name="Status"
    )
    observacoes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Observações"
    )
    created_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name="Criado em"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        verbose_name="Atualizado em"
    )

    class Meta:
        verbose_name = "Parcela"
        verbose_name_plural = "Parcelas"
        ordering = ['numero_parcela']
        unique_together = ['conta', 'numero_parcela']

    def __str__(self):
        return f"Parcela {self.numero_parcela}/{self.conta.numero_parcelas} - {self.conta.descricao}"

    def esta_vencida(self):
        """Verifica se a parcela está vencida"""
        return self.status == 'aberto' and self.data_vencimento < date.today()
    
    def dias_ate_vencimento(self):
        """Retorna quantos dias faltam para o vencimento"""
        if self.status == 'pago':
            return None
        delta = self.data_vencimento - date.today()
        return delta.days
    
    def get_status_badge_class(self):
        """Retorna classe CSS para badge de status"""
        if self.status == 'pago':
            return 'bg-success'
        elif self.esta_vencida() or self.status == 'vencido':
            return 'bg-danger'
        else:
            return 'bg-warning'
    
    def get_status_display_custom(self):
        """Retorna status formatado"""
        if self.status == 'pago':
            return 'PAGA'
        elif self.esta_vencida() or self.status == 'vencido':
            return 'ATRASADA'
        else:
            return 'A VENCER'

    def save(self, *args, **kwargs):
        """
        Atualiza status automaticamente ao salvar
        CORREÇÃO: Agora atualiza corretamente quando dá baixa
        """
        # Se tem data de pagamento, marca como pago
        if self.data_pagamento:
            self.status = 'pago'
        # Se não tem data de pagamento e está vencida, marca como vencido
        elif self.status != 'pago' and self.data_vencimento < date.today():
            self.status = 'vencido'
        # Se não está vencida e não foi paga, marca como aberto
        elif self.status != 'pago' and self.data_vencimento >= date.today():
            self.status = 'aberto'
        
        super().save(*args, **kwargs)