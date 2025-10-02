# financeiro/views.py

import os
from django.conf import settings
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

def numero_para_extenso(valor: Decimal) -> str:
    """Converte um valor monetário para sua representação por extenso."""
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
        return str(valor).replace('.', ',')

@login_required
def signup(request):
    if not request.user.is_staff:
        messages.error(request, "Você não tem permissão para realizar esta ação.")
        return redirect('financeiro:dashboard')
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Novo funcionário cadastrado com sucesso!")
            return redirect('financeiro:dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/signup.html', {'form': form, 'titulo': "Cadastrar Novo Funcionário"})

@login_required
def index(request):
    hoje = timezone.now().date()
    Parcela.objects.filter(status='aberto', data_vencimento__lt=hoje).update(status='vencido')
    total_a_receber = Parcela.objects.filter(status__in=['aberto', 'vencido']).aggregate(total=Sum('valor_parcela'))['total'] or Decimal('0.00')
    total_vencido = Parcela.objects.filter(status='vencido').aggregate(total=Sum('valor_parcela'))['total'] or Decimal('0.00')
    recebido_no_mes = Parcela.objects.filter(status='pago', data_pagamento__year=hoje.year, data_pagamento__month=hoje.month).aggregate(total=Sum('valor_parcela'))['total'] or Decimal('0.00')
    clientes_ativos = Cliente.objects.get_ativos().count()
    parcelas_a_vencer = Parcela.objects.filter(status='aberto', data_vencimento__gte=hoje).select_related('conta', 'conta__cliente').order_by('data_vencimento')[:5]
    contas_em_atraso = ContaReceber.objects.filter(parcelas__status='vencido').select_related('cliente').distinct().order_by('cliente__nome_completo')
    context = {
        'total_a_receber': total_a_receber, 'total_vencido': total_vencido,
        'recebido_no_mes': recebido_no_mes, 'clientes_ativos': clientes_ativos,
        'parcelas_a_vencer': parcelas_a_vencer, 'contas_em_atraso': contas_em_atraso,
    }
    return render(request, 'financeiro/index.html', context)

@login_required
def cliente_list(request):
    clientes = Cliente.objects.all().order_by('nome_completo')
    return render(request, 'financeiro/cliente_list.html', {'clientes': clientes})

@login_required
def cliente_detail(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    contas = cliente.contas.all().order_by('-data_emissao')
    context = {'cliente': cliente, 'contas': contas}
    return render(request, 'financeiro/cliente_detail.html', context)

@login_required
def cliente_create(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Cliente cadastrado com sucesso.")
            return redirect('financeiro:cliente_list')
    else:
        form = ClienteForm()
    return render(request, 'financeiro/cliente_form.html', {'form': form, 'titulo': 'Adicionar Novo Cliente'})

@login_required
def cliente_update(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, "Dados do cliente atualizados com sucesso.")
            return redirect('financeiro:cliente_list')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'financeiro/cliente_form.html', {'form': form, 'titulo': f'Editar Cliente: {cliente.nome_completo.title()}'})

@login_required
def cliente_delete(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        try:
            cliente.delete()
            messages.success(request, "Cliente excluído com sucesso.")
        except ProtectedError:
            messages.error(request, "Não é possível excluir este cliente pois existem contas associadas a ele.")
        return redirect('financeiro:cliente_list')
    return render(request, 'financeiro/cliente_confirm_delete.html', {'cliente': cliente})

@login_required
def conta_list(request):
    contas_queryset = ContaReceber.objects.select_related('cliente').order_by('-data_emissao')
    query = request.GET.get('q')
    if query:
        contas_queryset = contas_queryset.filter(
            Q(cliente__nome_completo__icontains=query) | Q(descricao__icontains=query)
        )
    paginator = Paginator(contas_queryset, 10)
    page_number = request.GET.get('page')
    try:
        contas = paginator.page(page_number)
    except PageNotAnInteger:
        contas = paginator.page(1)
    except EmptyPage:
        contas = paginator.page(paginator.num_pages)
    context = {'contas': contas, 'query': query, 'total_contas': paginator.count}
    return render(request, 'financeiro/conta_list.html', context)

@login_required
def conta_create(request):
    if request.method == 'POST':
        form = ContaReceberForm(request.POST)
        if form.is_valid():
            nova_conta = form.save(commit=False)
            nova_conta.data_emissao = timezone.now().date()
            nova_conta.save()
            valor_total = form.cleaned_data['valor_total']
            num_parcelas = form.cleaned_data['numero_parcelas']
            primeiro_vencimento = form.cleaned_data['data_vencimento_primeira_parcela']
            valor_parcela_base = (valor_total / num_parcelas).quantize(Decimal('0.01'), rounding=ROUND_DOWN)
            residuo = valor_total - (valor_parcela_base * num_parcelas)
            parcelas_a_criar = []
            for i in range(num_parcelas):
                valor_parcela_atual = valor_parcela_base
                if i == num_parcelas - 1:
                    valor_parcela_atual += residuo
                vencimento = primeiro_vencimento + relativedelta(months=i)
                parcelas_a_criar.append(Parcela(conta=nova_conta, numero_parcela=i + 1, valor_parcela=valor_parcela_atual, data_vencimento=vencimento))
            Parcela.objects.bulk_create(parcelas_a_criar)
            messages.success(request, "Conta lançada e parcelas geradas com sucesso.")
            return redirect('financeiro:conta_list')
    else:
        form = ContaReceberForm()
    return render(request, 'financeiro/conta_form.html', {'form': form, 'titulo': 'Lançar Nova Conta a Receber'})

@login_required
def conta_detail(request, pk):
    conta = get_object_or_404(ContaReceber.objects.select_related('cliente'), pk=pk)
    parcelas = conta.parcelas.all().order_by('numero_parcela')
    hoje = date.today()
    vencidas_qs = parcelas.filter(status='aberto', data_vencimento__lt=hoje)
    if vencidas_qs.exists():
        vencidas_qs.update(status='vencido')
        parcelas = conta.parcelas.all().order_by('numero_parcela')
    return render(request, 'financeiro/conta_detail.html', {'conta': conta, 'parcelas': parcelas})

@login_required
def conta_update(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk)
    if request.method == 'POST':
        form = ContaReceberUpdateForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta atualizada com sucesso.")
            return redirect('financeiro:conta_detail', pk=conta.pk)
    else:
        form = ContaReceberUpdateForm(instance=conta)
    return render(request, 'financeiro/conta_form.html', {'form': form, 'titulo': f'Editar Conta: {conta.descricao}'})

@login_required
def conta_delete(request, pk):
    conta = get_object_or_404(ContaReceber, pk=pk)
    if request.method == 'POST':
        conta.delete()
        messages.success(request, "Conta e suas parcelas excluídas com sucesso.")
        return redirect('financeiro:conta_list')
    return render(request, 'financeiro/conta_confirm_delete.html', {'conta': conta})

@login_required
def parcela_update(request, pk):
    parcela = get_object_or_404(Parcela.objects.select_related('conta'), pk=pk)
    if parcela.status == 'pago':
        messages.error(request, "Não é possível editar uma parcela que já foi paga.")
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    if request.method == 'POST':
        form = ParcelaUpdateForm(request.POST, instance=parcela)
        if form.is_valid():
            form.save()
            messages.success(request, f"Parcela {parcela.numero_parcela} atualizada e valores rebalanceados.")
            return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    else:
        form = ParcelaUpdateForm(instance=parcela)
    context = { 'form': form, 'titulo': f'Editar Parcela {parcela.numero_parcela}', 'parcela': parcela }
    return render(request, 'financeiro/parcela_form.html', context)

@login_required
def parcela_dar_baixa(request, pk):
    if request.method == 'POST':
        parcela = get_object_or_404(Parcela, pk=pk)
        parcela.data_pagamento = timezone.now().date()
        parcela.save()
        messages.success(request, f"Baixa da parcela {parcela.numero_parcela} realizada com sucesso!")
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    return redirect('financeiro:conta_list')

@login_required
def parcela_estornar(request, pk):
    if request.method == 'POST':
        parcela = get_object_or_404(Parcela, pk=pk)
        parcela.data_pagamento = None
        parcela.save()
        messages.success(request, f"O pagamento da parcela {parcela.numero_parcela} foi estornado.")
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    return redirect('financeiro:conta_list')

@login_required
def gerar_recibo_pdf(request, pk):
    parcela = get_object_or_404(Parcela.objects.select_related('conta__cliente'), pk=pk)
    if parcela.status != 'pago':
        messages.error(request, "Não é possível gerar recibo para parcelas não pagas.")
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    
    logo_path = os.path.join(settings.BASE_DIR, 'financeiro', 'static', 'financeiro', 'images', 'logo.png')
    
    context = {
        'parcela': parcela, 
        'conta': parcela.conta, 
        'cliente': parcela.conta.cliente,
        'data_emissao': timezone.now().date(), 
        'valor_extenso': numero_para_extenso(parcela.valor_parcela),
        'logo_path': logo_path
    }
    html_string = render_to_string('financeiro/documentos/recibo_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    filename = f"recibo_{parcela.conta.cliente.nome_completo.lower().replace(' ', '_')}_parcela_{parcela.numero_parcela}.pdf"
    response['Content-Disposition'] = f'inline; filename="{filename}"'
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response

@login_required
def relatorio_cliente_html(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    contas = ContaReceber.objects.filter(cliente=cliente)
    return render(request, 'financeiro/relatorios/extrato_cliente.html', {'cliente': cliente, 'contas': contas})

@login_required
def relatorio_cliente_pdf(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    contas = ContaReceber.objects.filter(cliente=cliente)
    html_string = render_to_string('financeiro/relatorios/extrato_cliente_pdf.html', {'cliente': cliente, 'contas': contas})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="extrato_{cliente.nome_completo.lower().replace(" ", "_")}.pdf"'
    HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(response)
    return response