# financeiro/forms.py
from django import forms
from .models import Cliente, ContaReceber, Parcela
from django.core.exceptions import ValidationError
from datetime import date
import re


# ==============================================================================
# FUNÇÕES AUXILIARES DE VALIDAÇÃO DE CPF/CNPJ
# ==============================================================================

def limpar_documento(documento: str) -> str:
    """
    Remove caracteres não numéricos de CPF/CNPJ
    
    Args:
        documento: String com CPF/CNPJ (pode conter formatação)
    
    Returns:
        String contendo apenas dígitos
    
    Example:
        >>> limpar_documento('123.456.789-00')
        '12345678900'
    """
    if not documento:
        return ''
    return ''.join(re.findall(r'\d', str(documento)))


def validate_cpf(cpf: str) -> bool:
    """
    Valida CPF brasileiro segundo algoritmo oficial
    
    Args:
        cpf: String com CPF (pode conter formatação)
    
    Returns:
        bool: True se válido, False caso contrário
    
    Algorithm:
        1. Remove formatação
        2. Verifica se tem 11 dígitos
        3. Verifica se não é sequência repetida
        4. Valida primeiro dígito verificador
        5. Valida segundo dígito verificador
    """
    cpf = limpar_documento(cpf)
    
    # Verifica se tem 11 dígitos
    if not cpf or len(cpf) != 11:
        return False
    
    # Verifica se não é sequência repetida (ex: 111.111.111-11)
    if cpf == cpf[0] * 11:
        return False
    
    # Valida primeiro dígito verificador
    soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
    digito_1 = (soma * 10 % 11) % 10
    
    if digito_1 != int(cpf[9]):
        return False
    
    # Valida segundo dígito verificador
    soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
    digito_2 = (soma * 10 % 11) % 10
    
    if digito_2 != int(cpf[10]):
        return False
    
    return True


def validate_cnpj(cnpj: str) -> bool:
    """
    Valida CNPJ brasileiro segundo algoritmo oficial
    
    Args:
        cnpj: String com CNPJ (pode conter formatação)
    
    Returns:
        bool: True se válido, False caso contrário
    
    Algorithm:
        1. Remove formatação
        2. Verifica se tem 14 dígitos
        3. Verifica se não é sequência repetida
        4. Valida primeiro dígito verificador
        5. Valida segundo dígito verificador
    """
    cnpj = limpar_documento(cnpj)
    
    # Verifica se tem 14 dígitos
    if not cnpj or len(cnpj) != 14:
        return False
    
    # Verifica se não é sequência repetida
    if cnpj == cnpj[0] * 14:
        return False
    
    # Valida primeiro dígito verificador
    multiplicadores_1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores_1[i] for i in range(12))
    digito_1 = 11 - (soma % 11)
    if digito_1 >= 10:
        digito_1 = 0
    
    if digito_1 != int(cnpj[12]):
        return False
    
    # Valida segundo dígito verificador
    multiplicadores_2 = [6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    soma = sum(int(cnpj[i]) * multiplicadores_2[i] for i in range(13))
    digito_2 = 11 - (soma % 11)
    if digito_2 >= 10:
        digito_2 = 0
    
    if digito_2 != int(cnpj[13]):
        return False
    
    return True


# ==============================================================================
# MIXIN PARA ESTILIZAÇÃO PADRÃO DE FORMULÁRIOS
# ==============================================================================

class TailwindFormMixin:
    """
    Mixin para aplicar estilos Tailwind CSS aos formulários
    
    Aplica classes padrão do Tailwind para:
    - Inputs de texto
    - Selects
    - Textareas
    - Checkboxes
    
    Usage:
        class MeuForm(TailwindFormMixin, forms.ModelForm):
            pass
    """
    
    # Classes CSS padrão para inputs
    BASE_INPUT_CLASSES = (
        'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 '
        'text-white placeholder-gray-400 focus:outline-none focus:ring-2 '
        'focus:ring-cyan-500 focus:border-transparent transition-all duration-300'
    )
    
    # Classes para textareas
    TEXTAREA_CLASSES = (
        'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 '
        'text-white placeholder-gray-400 focus:outline-none focus:ring-2 '
        'focus:ring-cyan-500 resize-none transition-all duration-300'
    )
    
    # Classes para checkboxes
    CHECKBOX_CLASSES = (
        'w-5 h-5 text-cyan-500 bg-gray-700 border-gray-600 rounded '
        'focus:ring-cyan-500 focus:ring-2'
    )
    
    def aplicar_estilos_tailwind(self):
        """
        Aplica estilos Tailwind a todos os campos do formulário
        
        Identifica o tipo de campo e aplica as classes apropriadas
        """
        for field_name, field in self.fields.items():
            widget = field.widget
            
            # Adiciona classe uppercase para campos de texto (exceto email)
            extra_classes = ''
            if field_name not in ['email'] and isinstance(widget, (forms.TextInput, forms.Textarea)):
                extra_classes = ' uppercase'
            
            # Checkbox
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs.update({
                    'class': self.CHECKBOX_CLASSES
                })
            
            # Textarea
            elif isinstance(widget, forms.Textarea):
                widget.attrs.update({
                    'class': self.TEXTAREA_CLASSES + extra_classes,
                    'autocomplete': 'off'
                })
            
            # Select
            elif isinstance(widget, forms.Select):
                widget.attrs.update({
                    'class': self.BASE_INPUT_CLASSES,
                    'autocomplete': 'off'
                })
            
            # Input padrão (text, email, number, etc)
            else:
                widget.attrs.update({
                    'class': self.BASE_INPUT_CLASSES + extra_classes,
                    'autocomplete': 'off'
                })


# ==============================================================================
# FORMULÁRIO DE CLIENTE
# ==============================================================================

class ClienteForm(TailwindFormMixin, forms.ModelForm):
    """
    Formulário para cadastro e edição de clientes
    
    Features:
        - Validação de CPF/CNPJ
        - Máscara automática para telefone e CPF/CNPJ (Alpine.js)
        - Conversão automática de nome para uppercase
        - Conversão automática de email para lowercase
        - Verificação de unicidade de CPF/CNPJ
    """
    
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
        help_texts = {
            'nome_completo': 'Nome completo do cliente (será convertido para maiúsculas)',
            'cpf_cnpj': 'CPF (11 dígitos) ou CNPJ (14 dígitos)',
            'email': 'E-mail principal para contato',
            'telefone': 'Telefone com DDD',
            'endereco': 'Endereço completo do cliente',
            'observacoes': 'Informações adicionais sobre o cliente'
        }
        widgets = {
            'endereco': forms.Textarea(attrs={'rows': 3}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica estilos Tailwind
        self.aplicar_estilos_tailwind()
        
        # Customizações específicas por campo
        
        # Nome Completo - uppercase automático via CSS
        self.fields['nome_completo'].widget.attrs.update({
            'placeholder': 'Digite o nome completo do cliente',
            'required': True
        })
        
        # CPF/CNPJ - máscara dinâmica com Alpine.js
        self.fields['cpf_cnpj'].widget.attrs.update({
            'placeholder': 'Digite o CPF ou CNPJ',
            'x-data': "{}",
            'x-mask:dynamic': "$input.length > 14 ? '99.999.999/9999-99' : '999.999.999-99'",
        })
        
        # Email - type email para validação HTML5
        self.fields['email'].widget.attrs.update({
            'placeholder': 'exemplo@email.com',
            'type': 'email'
        })
        
        # Telefone - máscara com Alpine.js
        self.fields['telefone'].widget.attrs.update({
            'placeholder': '(XX) XXXXX-XXXX',
            'x-data': "{}",
            'x-mask': '(99) 99999-9999'
        })
        
        # Torna CPF/CNPJ não obrigatório
        self.fields['cpf_cnpj'].required = False
    
    def clean_nome_completo(self):
        """
        Normaliza nome para uppercase
        
        Returns:
            str: Nome em maiúsculas e sem espaços extras
        """
        nome = self.cleaned_data.get('nome_completo', '')
        return nome.strip().upper()
    
    def clean_email(self):
        """
        Normaliza email para lowercase
        
        Returns:
            str: Email em minúsculas ou None se vazio
        """
        email = self.cleaned_data.get('email', '')
        if email:
            return email.strip().lower()
        return None
    
    def clean_cpf_cnpj(self):
        """
        Valida e verifica unicidade de CPF/CNPJ
        
        Returns:
            str: CPF/CNPJ formatado
        
        Raises:
            ValidationError: Se CPF/CNPJ for inválido ou já existir
        """
        cpf_cnpj = self.cleaned_data.get('cpf_cnpj', '')
        
        # Permite campo vazio
        if not cpf_cnpj:
            return None
        
        # Remove formatação
        documento_limpo = limpar_documento(cpf_cnpj)
        
        # Valida comprimento
        if len(documento_limpo) not in [11, 14]:
            raise ValidationError(
                'O documento deve conter 11 dígitos (CPF) ou 14 dígitos (CNPJ).'
            )
        
        # Valida CPF
        if len(documento_limpo) == 11:
            if not validate_cpf(documento_limpo):
                raise ValidationError(
                    'CPF inválido. Verifique os dígitos informados.'
                )
        
        # Valida CNPJ
        elif len(documento_limpo) == 14:
            if not validate_cnpj(documento_limpo):
                raise ValidationError(
                    'CNPJ inválido. Verifique os dígitos informados.'
                )
        
        # Verifica unicidade (exceto para o próprio registro em edição)
        queryset = Cliente.objects.filter(cpf_cnpj=cpf_cnpj)
        if self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            tipo_doc = 'CPF' if len(documento_limpo) == 11 else 'CNPJ'
            raise ValidationError(
                f'Já existe um cliente cadastrado com este {tipo_doc}.'
            )
        
        return cpf_cnpj


# ==============================================================================
# FORMULÁRIO DE CRIAÇÃO DE CONTA A RECEBER
# ==============================================================================

class ContaReceberForm(TailwindFormMixin, forms.ModelForm):
    """
    Formulário para criação de novas contas a receber
    
    Features:
        - Campo adicional para data da primeira parcela
        - Validação de valor positivo
        - Validação de número de parcelas (1-120)
        - Validação de data não pode estar no passado
        - Filtro automático de clientes ativos
    """
    
    # Campo adicional não presente no modelo
    data_vencimento_primeira_parcela = forms.DateField(
        label='Data de Vencimento da 1ª Parcela',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': (
                'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 '
                'text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 '
                'transition-all duration-300'
            )
        }),
        help_text='Data de vencimento da primeira parcela (demais serão mensais)'
    )
    
    class Meta:
        model = ContaReceber
        fields = [
            'cliente',
            'descricao',
            'valor_total',
            'numero_parcelas',
            'data_vencimento_primeira_parcela',
            'observacoes'
        ]
        labels = {
            'cliente': 'Cliente',
            'descricao': 'Descrição da Conta',
            'valor_total': 'Valor Total (R$)',
            'numero_parcelas': 'Número de Parcelas',
            'observacoes': 'Observações (Opcional)'
        }
        help_texts = {
            'cliente': 'Selecione o cliente responsável',
            'descricao': 'Descrição do serviço ou produto',
            'valor_total': 'Valor total em reais',
            'numero_parcelas': 'Quantidade de parcelas (1 a 120)',
            'observacoes': 'Informações adicionais sobre esta conta'
        }
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica estilos Tailwind
        self.aplicar_estilos_tailwind()
        
        # Customizações específicas
        self.fields['descricao'].widget.attrs.update({
            'placeholder': 'Ex: Honorários Advocatícios - Processo 123/2025'
        })
        
        self.fields['valor_total'].widget.attrs.update({
            'placeholder': '0,00',
            'step': '0.01',
            'min': '0.01'
        })
        
        self.fields['numero_parcelas'].widget.attrs.update({
            'placeholder': '1',
            'min': '1',
            'max': '120'
        })
        
        self.fields['observacoes'].widget.attrs.update({
            'placeholder': 'Digite observações adicionais (opcional)'
        })
        
        # Filtra apenas clientes
        self.fields['cliente'].queryset = Cliente.objects.all().order_by('nome_completo')
        
        # Adiciona texto vazio ao select de cliente
        self.fields['cliente'].empty_label = 'Selecione um cliente'
    
    def clean_descricao(self):
        """
        Normaliza descrição para uppercase
        
        Returns:
            str: Descrição em maiúsculas e sem espaços extras
        """
        descricao = self.cleaned_data.get('descricao', '')
        return descricao.strip().upper()
    
    def clean_valor_total(self):
        """
        Valida que o valor total é positivo
        
        Returns:
            Decimal: Valor validado
        
        Raises:
            ValidationError: Se valor <= 0
        """
        valor = self.cleaned_data.get('valor_total')
        
        if valor is None:
            raise ValidationError('O valor total é obrigatório.')
        
        if valor <= 0:
            raise ValidationError('O valor total deve ser maior que zero.')
        
        return valor
    
    def clean_numero_parcelas(self):
        """
        Valida número de parcelas
        
        Returns:
            int: Número de parcelas validado
        
        Raises:
            ValidationError: Se número inválido
        """
        num_parcelas = self.cleaned_data.get('numero_parcelas')
        
        if num_parcelas is None:
            raise ValidationError('O número de parcelas é obrigatório.')
        
        if num_parcelas < 1:
            raise ValidationError('O número de parcelas deve ser no mínimo 1.')
        
        if num_parcelas > 120:
            raise ValidationError(
                'O número de parcelas não pode exceder 120 (10 anos).'
            )
        
        return num_parcelas
    
    def clean_data_vencimento_primeira_parcela(self):
        """
        Valida data de vencimento da primeira parcela
        
        Returns:
            date: Data validada
        
        Raises:
            ValidationError: Se data no passado
        """
        data_vencimento = self.cleaned_data.get('data_vencimento_primeira_parcela')
        
        if not data_vencimento:
            raise ValidationError('A data de vencimento é obrigatória.')
        
        # Permite hoje ou futuro
        if data_vencimento < date.today():
            raise ValidationError(
                'A data de vencimento não pode estar no passado. '
                'Use a data de hoje ou uma data futura.'
            )
        
        return data_vencimento


# ==============================================================================
# FORMULÁRIO DE EDIÇÃO DE CONTA (APENAS CAMPOS EDITÁVEIS)
# ==============================================================================

class ContaReceberUpdateForm(TailwindFormMixin, forms.ModelForm):
    """
    Formulário para edição de contas existentes
    
    Permite editar apenas:
    - Descrição
    - Observações
    
    Valor total, cliente e parcelas não podem ser alterados após criação.
    """
    
    class Meta:
        model = ContaReceber
        fields = ['descricao', 'observacoes']
        labels = {
            'descricao': 'Descrição da Conta',
            'observacoes': 'Observações'
        }
        help_texts = {
            'descricao': 'Atualize a descrição se necessário',
            'observacoes': 'Informações adicionais sobre esta conta'
        }
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 3})
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica estilos Tailwind
        self.aplicar_estilos_tailwind()
        
        self.fields['descricao'].widget.attrs.update({
            'placeholder': 'Descrição da conta'
        })
        
        self.fields['observacoes'].widget.attrs.update({
            'placeholder': 'Observações adicionais (opcional)'
        })
    
    def clean_descricao(self):
        """
        Normaliza descrição para uppercase
        
        Returns:
            str: Descrição em maiúsculas e sem espaços extras
        """
        descricao = self.cleaned_data.get('descricao', '')
        return descricao.strip().upper()


# ==============================================================================
# FORMULÁRIO DE EDIÇÃO DE PARCELA
# ==============================================================================

class ParcelaUpdateForm(TailwindFormMixin, forms.ModelForm):
    """
    Formulário para edição de parcelas individuais
    
    Permite editar:
    - Valor da parcela
    - Data de vencimento
    
    Note:
        Não permite editar parcelas já pagas (validação na view)
    """
    
    # Override do campo data_vencimento para usar input type="date"
    data_vencimento = forms.DateField(
        label='Data de Vencimento',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': (
                'w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 '
                'text-white focus:outline-none focus:ring-2 focus:ring-cyan-500 '
                'transition-all duration-300'
            )
        }),
        help_text='Nova data de vencimento da parcela'
    )
    
    class Meta:
        model = Parcela
        fields = ['valor_parcela', 'data_vencimento']
        labels = {
            'valor_parcela': 'Valor da Parcela (R$)'
        }
        help_texts = {
            'valor_parcela': 'Novo valor da parcela em reais',
            'data_vencimento': 'Nova data de vencimento'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplica estilos Tailwind
        self.aplicar_estilos_tailwind()
        
        self.fields['valor_parcela'].widget.attrs.update({
            'placeholder': '0,00',
            'step': '0.01',
            'min': '0.01'
        })
    
    def clean_valor_parcela(self):
        """
        Valida valor da parcela
        
        Returns:
            Decimal: Valor validado
        
        Raises:
            ValidationError: Se valor <= 0
        """
        valor = self.cleaned_data.get('valor_parcela')
        
        if valor is None:
            raise ValidationError('O valor da parcela é obrigatório.')
        
        if valor <= 0:
            raise ValidationError('O valor da parcela deve ser maior que zero.')
        
        return valor
    
    def clean_data_vencimento(self):
        """
        Valida data de vencimento
        
        Returns:
            date: Data validada
        
        Raises:
            ValidationError: Se data não fornecida
        """
        data = self.cleaned_data.get('data_vencimento')
        
        if not data:
            raise ValidationError('A data de vencimento é obrigatória.')
        
        return data