# financeiro/forms.py

from django import forms
from .models import Cliente, ContaReceber, Parcela
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
# ... (restante das suas funções de validação e imports)

class FormStylingMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            base_classes = 'w-full rounded-lg px-4 py-3 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-cyan-500 bg-gray-100 border border-gray-200 text-gray-800 placeholder-gray-400 focus:bg-white'
            extra_classes = ' uppercase' if isinstance(widget, (forms.TextInput, forms.Textarea)) and field_name != 'email' else ''
            widget.attrs.update({'class': f'{base_classes}{extra_classes}'})
            if isinstance(widget, forms.Textarea):
                widget.attrs.setdefault('rows', 3)

class ClienteForm(FormStylingMixin, forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nome_completo', 'cpf_cnpj', 'email', 'telefone', 'endereco', 'observacoes']
        # ... (resto da classe Meta como estava)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cpf_cnpj'].widget.attrs.update({
            'x-data': "{}",
            'x-mask:dynamic': "$input.length > 14 ? '99.999.999/9999-99' : '999.999.999-99'",
            'placeholder': 'Digite o CPF ou CNPJ'
        })
        self.fields['telefone'].widget.attrs.update({
            'x-data': "{}",
            'x-mask': '(99) 99999-9999',
            'placeholder': '(XX) XXXXX-XXXX'
        })

# ... (resto dos seus formulários: CustomUserCreationForm, ContaReceberForm, etc.)