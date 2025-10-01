# financeiro/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Cliente, ContaReceber, Parcela
from django.core.exceptions import ValidationError
from datetime import date
import re

# ==============================================================================
# FUNÇÕES AUXILIARES DE VALIDAÇÃO
# ==============================================================================
def limpar_documento(documento: str) -> str:
    if not documento: return ''
    return ''.join(re.findall(r'\d', str(documento)))

def validate_cpf(cpf: str) -> bool:
    cpf = limpar_documento(cpf)
    if not cpf or len(cpf) != 11 or cpf == cpf[0] * 11: return False
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito_1 = (soma * 10 % 11) % 10
    if digito_1 != int(cpf[9]): return False
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito_2 = (soma * 10 % 11) % 10
    if digito_2 != int(cpf[10]): return False
    return True

def validate_cnpj(cnpj: str) -> bool:
    cnpj = limpar_documento(cnpj)
    if not cnpj or len(cnpj) != 14 or cnpj == cnpj[0] * 14: return False
    multiplicadores_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores_1[i] for i in range(12))
    digito_1 = 11 - (soma % 11)
    if digito_1 >= 10: digito_1 = 0
    if digito_1 != int(cnpj[12]): return False
    multiplicadores_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores_2[i] for i in range(13))
    digito_2 = 11 - (soma % 11)
    if digito_2 >= 10: digito_2 = 0
    if digito_2 != int(cnpj[13]): return False
    return True

# ==============================================================================
# MIXIN DE ESTILIZAÇÃO PARA FORMULÁRIOS
# ==============================================================================
class FormStylingMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            
            base_classes = 'w-full rounded-lg px-4 py-3 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-cyan-500'
            light_theme_classes = 'bg-gray-100 border border-gray-200 text-gray-800 placeholder-gray-400 focus:bg-white'
            
            # Aplica classes a todos os tipos de input comuns
            if isinstance(widget, (forms.TextInput, forms.EmailInput, forms.NumberInput, forms.DateInput, forms.PasswordInput)):
                widget.attrs.update({'class': f'{base_classes} {light_theme_classes}'})

            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({'class': f'{base_classes} {light_theme_classes}', 'rows': 4})
            
            elif isinstance(widget, forms.Select):
                widget.attrs.update({'class': f'{base_classes} {light_theme_classes}'})

# ==============================================================================
# FORMULÁRIO DE CRIAÇÃO DE USUÁRIO
# ==============================================================================
class CustomUserCreationForm(FormStylingMixin, UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "first_name", "last_name", "email")
        labels = {
            "username": "Nome de Usuário",
            "first_name": "Primeiro Nome",
            "last_name": "Sobrenome",
            "email": "E-mail",
        }

# ==============================================================================
# FORMULÁRIO DE CLIENTE
# ==============================================================================
class ClienteForm(FormStylingMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome_completo', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'observacoes']
        labels = {
            'nome_completo': 'Nome Completo',
            'cpf_cnpj': 'CPF ou CNPJ',
            'email': 'E-mail',
            'telefone': 'Telefone de Contato',
            'endereco': 'Endereço',
            'observacoes': 'Observações'
        }

    def clean_nome_completo(self):
        nome = self.cleaned_data.get('nome_completo', '')
        return nome.strip().upper()

    def clean_email(self):
        email = self.cleaned_data.get('email', '')
        if email: return email.strip().lower()
        return None

    def clean_cpf_cnpj(self):
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj', '')
        if not cpf_cnpj: return None
        documento_limpo = limpar_documento(cpf_cnpj)
        if len(documento_limpo) not in [11, 14]: raise ValidationError('O documento deve conter 11 (CPF) ou 14 (CNPJ) dígitos.')
        if len(documento_limpo) == 11 and not validate_cpf(documento_limpo): raise ValidationError('CPF inválido.')
        if len(documento_limpo) == 14 and not validate_cnpj(documento_limpo): raise ValidationError('CNPJ inválido.')
        queryset = Cliente.objects.filter(cpf_cnpj=cpf_cnpj)
        if self.instance.pk: queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists(): raise ValidationError('Já existe um cliente cadastrado com este documento.')
        return cpf_cnpj

# ==============================================================================
# FORMULÁRIO DE CONTA A RECEBER
# ==============================================================================
class ContaReceberForm(FormStylingMixin, forms.ModelForm):
    data_vencimento_primeira_parcela = forms.DateField(label='Data de Vencimento da 1ª Parcela', widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = ContaReceber
        fields = ['cliente', 'descricao', 'valor_total', 'numero_parcelas', 'data_vencimento_primeira_parcela', 'observacoes']
        labels = {
            'cliente': 'Cliente',
            'descricao': 'Descrição da Conta',
            'valor_total': 'Valor Total (R$)',
            'numero_parcelas': 'Número de Parcelas',
            'observacoes': 'Observações (Opcional)'
        }

# ==============================================================================
# FORMULÁRIOS DE ATUALIZAÇÃO
# ==============================================================================
class ContaReceberUpdateForm(FormStylingMixin, forms.ModelForm):
    class Meta:
        model = ContaReceber
        fields = ['descricao', 'observacoes']
        labels = {
            'descricao': 'Descrição da Conta',
            'observacoes': 'Observações'
        }

class ParcelaUpdateForm(FormStylingMixin, forms.ModelForm):
    data_vencimento = forms.DateField(
        label='Data de Vencimento',
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    
    class Meta:
        model = Parcela
        fields = ['valor_parcela', 'data_vencimento']
        labels = {
            'valor_parcela': 'Valor da Parcela (R$)'
        }