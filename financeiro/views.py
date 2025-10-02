# financeiro/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, ProtectedError, Q
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.utils import timezone
from datetime import date
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from decimal import Decimal, ROUND_HALF_UP, ROUND_DOWN

from weasyprint import HTML
from dateutil.relativedelta import relativedelta

from .models import Cliente, Parcela, ContaReceber
from .forms import (
    ClienteForm, ContaReceberForm, ContaReceberUpdateForm,
    ParcelaUpdateForm, CustomUserCreationForm
)

def numero_para_extenso(valor):
    try:
        from num2words import num2words
        inteiro = int(valor)
        centavos = int((valor - inteiro) * 100)
        texto_inteiro = num2words(inteiro, lang='pt_BR')
        reais = "real" if inteiro == 1 else "reais"
        if centavos > 0:
            texto_centavos = num2words(centavos, lang='pt_BR')
            sufixo_centavos = "centavo" if centavos == 1 else "centavos"
            return f"{texto_inteiro} {reais} e {texto_centavos} {sufixo_centavos}"
        else:
            return f"{texto_inteiro} {reais}"
    except (ImportError, NotImplementedError):
        return str(valor)

# O restante de todas as suas views...
# (O corpo das outras views foi omitido para brevidade, mas deve ser mantido no seu arquivo)