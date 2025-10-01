# financeiro/views.py

"""
Views do Sistema Financeiro

Este módulo contém todas as views para:
- Dashboard principal com indicadores
- CRUD completo de Clientes
- CRUD completo de Contas a Receber
- Ações de Parcelas (baixa, estorno, edição)
- Geração de Relatórios (HTML e PDF)

Autor: Sistema Financeiro
Data: 2025
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q, Count
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction
from django.views.decorators.http import require_POST
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from io import BytesIO

from .models import Cliente, Parcela, ContaReceber
from .forms import (
    ClienteForm,
    ContaReceberForm,
    ContaReceberUpdateForm,
    ParcelaUpdateForm
)


# ==============================================================================
# VIEW PRINCIPAL - DASHBOARD
# ==============================================================================

# financeiro/views.py
# SUBSTITUA APENAS AS FUNÇÕES ABAIXO NO SEU ARQUIVO

# ==============================================================================
# FUNÇÃO CORRIGIDA 1: index (Dashboard)
# ==============================================================================

def index(request):
    """
    Dashboard principal do sistema financeiro - CORRIGIDO
    """
    hoje = date.today()
    
    # Indicadores financeiros principais - CORRIGIDO para calcular corretamente
    total_a_receber = Parcela.objects.filter(
        status__in=['aberto', 'vencido']
    ).aggregate(
        total=Sum('valor_parcela')
    )['total'] or Decimal('0.00')
    
    total_vencido = Parcela.objects.filter(
        status='vencido'
    ).aggregate(
        total=Sum('valor_parcela')
    )['total'] or Decimal('0.00')
    
    # CORREÇÃO: Agora busca por data_pagamento corretamente
    recebido_no_mes = Parcela.objects.filter(
        status='pago',
        data_pagamento__isnull=False,
        data_pagamento__year=hoje.year,
        data_pagamento__month=hoje.month
    ).aggregate(
        total=Sum('valor_parcela')
    )['total'] or Decimal('0.00')
    
    clientes_ativos = Cliente.objects.all().count()
    
    # Parcelas vencendo nos próximos 7 dias
    data_limite = hoje + timedelta(days=7)
    proximas_parcelas = Parcela.objects.filter(
        status='aberto',
        data_vencimento__range=[hoje, data_limite]
    ).select_related(
        'conta__cliente'
    ).order_by('data_vencimento')[:10]
    
    # Últimas 5 contas lançadas
    ultimas_contas = ContaReceber.objects.select_related(
        'cliente'
    ).order_by('-created_at')[:5]
    
    context = {
        'total_a_receber': total_a_receber,
        'total_vencido': total_vencido,
        'recebido_no_mes': recebido_no_mes,
        'clientes_ativos': clientes_ativos,
        'proximas_parcelas': proximas_parcelas,
        'ultimas_contas': ultimas_contas,
    }
    
    return render(request, 'financeiro/index.html', context)


# ==============================================================================
# FUNÇÃO CORRIGIDA 2: parcela_dar_baixa
# ==============================================================================

@require_POST
@transaction.atomic
def parcela_estornar(request, pk):
    """
    Estorna o pagamento de uma parcela
    
    Process:
        - Remove data_pagamento
        - Redefine status baseado na data de vencimento
        - Exibe mensagem de aviso
    
    Args:
        request: HttpRequest object
        pk: Primary key da parcela
    
    Returns:
        HttpResponseRedirect: Redireciona para detalhes da conta
    """
    parcela = get_object_or_404(Parcela, pk=pk)
    
    # Verifica se está paga
    if parcela.status != 'pago':
        messages.warning(
            request,
            'Esta parcela não está marcada como paga.'
        )
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    
    # Remove pagamento
    parcela.data_pagamento = None
    
    # Redefine status baseado no vencimento
    if parcela.data_vencimento < date.today():
        parcela.status = 'vencido'
    else:
        parcela.status = 'aberto'
    
    parcela.save()
    
    messages.warning(
        request,
        f'Pagamento da parcela {parcela.numero_parcela}/'
        f'{parcela.conta.numero_parcelas} estornado. '
        f'Status atual: {parcela.get_status_display_custom()}'
    )
    
    return redirect('financeiro:conta_detail', pk=parcela.conta.pk)

# ==============================================================================
# VIEWS DE CLIENTES - CRUD COMPLETO
# ==============================================================================

def cliente_list(request):
    """
    Lista todos os clientes com busca, filtros e paginação
    
    Query Parameters:
        q: Termo de busca (nome, CPF/CNPJ, email)
        page: Número da página
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Renderiza template financeiro/cliente_list.html
    """
    # Query base com anotações
    clientes_list = Cliente.objects.annotate(
        total_contas=Count('contas')
    ).order_by('nome_completo')
    
    # Busca por nome, CPF/CNPJ ou email
    query = request.GET.get('q', '').strip()
    if query:
        clientes_list = clientes_list.filter(
            Q(nome_completo__icontains=query) |
            Q(cpf_cnpj__icontains=query) |
            Q(email__icontains=query)
        )
    
    # Paginação (25 por página)
    paginator = Paginator(clientes_list, 25)
    page_number = request.GET.get('page')
    clientes = paginator.get_page(page_number)
    
    context = {
        'clientes': clientes,
        'query': query,
        'total_clientes': clientes_list.count(),
    }
    
    return render(request, 'financeiro/cliente_list.html', context)


def cliente_create(request):
    """
    Cria um novo cliente
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Renderiza form ou redireciona após sucesso
    """
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            messages.success(
                request,
                f'Cliente "{cliente.nome_completo}" cadastrado com sucesso!'
            )
            return redirect('financeiro:cliente_list')
    else:
        form = ClienteForm()
    
    context = {
        'form': form,
        'titulo': 'Adicionar Novo Cliente',
        'acao': 'Cadastrar Cliente',
        'voltar_url': 'financeiro:cliente_list'
    }
    
    return render(request, 'financeiro/cliente_form.html', context)


def cliente_detail(request, pk):
    """
    Exibe detalhes de um cliente
    
    Args:
        request: HttpRequest object
        pk: Primary key do cliente
    
    Returns:
        HttpResponse: Renderiza template com detalhes
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    contas = cliente.contas.all().order_by('-created_at')
    
    context = {
        'cliente': cliente,
        'contas': contas
    }
    
    return render(request, 'financeiro/cliente_detail.html', context)


def cliente_update(request, pk):
    """
    Atualiza dados de um cliente existente
    
    Args:
        request: HttpRequest object
        pk: Primary key do cliente
    
    Returns:
        HttpResponse: Renderiza form ou redireciona após sucesso
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Cliente "{cliente.nome_completo}" atualizado com sucesso!'
            )
            return redirect('financeiro:cliente_detail', pk=pk)
    else:
        form = ClienteForm(instance=cliente)
    
    context = {
        'form': form,
        'titulo': f'Editar Cliente: {cliente.nome_completo.title()}',
        'acao': 'Salvar Alterações',
        'voltar_url': 'financeiro:cliente_detail',
        'cliente': cliente
    }
    
    return render(request, 'financeiro/cliente_form.html', context)


def cliente_delete(request, pk):
    """
    Deleta um cliente (com validações de segurança)
    
    Não permite deletar clientes com contas associadas.
    
    Args:
        request: HttpRequest object
        pk: Primary key do cliente
    
    Returns:
        HttpResponse: Renderiza confirmação ou redireciona após sucesso
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    
    # Verifica se há contas associadas
    if cliente.contas.exists():
        messages.error(
            request,
            f'Não é possível excluir "{cliente.nome_completo}" pois existem '
            f'{cliente.contas.count()} conta(s) associada(s).'
        )
        return redirect('financeiro:cliente_list')
    
    if request.method == 'POST':
        nome_cliente = cliente.nome_completo
        cliente.delete()
        messages.success(
            request,
            f'Cliente "{nome_cliente}" excluído com sucesso!'
        )
        return redirect('financeiro:cliente_list')
    
    context = {
        'cliente': cliente,
        'voltar_url': 'financeiro:cliente_list'
    }
    
    return render(request, 'financeiro/cliente_confirm_delete.html', context)


# ==============================================================================
# VIEWS DE CONTAS A RECEBER - CRUD COMPLETO
# ==============================================================================

def conta_list(request):
    """
    Lista todas as contas a receber com filtros e busca
    
    Query Parameters:
        q: Termo de busca (cliente, descrição)
        status: Filtro de status (em_aberto/quitada)
        page: Número da página
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Renderiza template financeiro/conta_list.html
    """
    # Query base com anotações para performance
    contas_list = ContaReceber.objects.select_related(
        'cliente'
    ).annotate(
        total_pago=Sum(
            'parcelas__valor_parcela',
            filter=Q(parcelas__status='pago')
        ),
        total_pendente=Sum(
            'parcelas__valor_parcela',
            filter=Q(parcelas__status__in=['aberto', 'vencido'])
        )
    ).order_by('-data_emissao')
    
    # Busca por cliente ou descrição
    query = request.GET.get('q', '').strip()
    if query:
        contas_list = contas_list.filter(
            Q(cliente__nome_completo__icontains=query) |
            Q(descricao__icontains=query)
        )
    
    # Filtro por status
    status_filtro = request.GET.get('status', '')
    if status_filtro == 'em_aberto':
        contas_list = contas_list.filter(
            parcelas__status__in=['aberto', 'vencido']
        ).distinct()
    elif status_filtro == 'quitada':
        contas_list = contas_list.exclude(
            parcelas__status__in=['aberto', 'vencido']
        ).distinct()
    
    # Paginação (20 por página)
    paginator = Paginator(contas_list, 20)
    page_number = request.GET.get('page')
    contas = paginator.get_page(page_number)
    
    context = {
        'contas': contas,
        'query': query,
        'status_filtro': status_filtro,
        'total_contas': contas_list.count(),
    }
    
    return render(request, 'financeiro/conta_list.html', context)


@transaction.atomic
def conta_create(request):
    """
    Cria uma nova conta a receber e gera suas parcelas automaticamente
    
    Process:
        1. Valida formulário
        2. Cria conta
        3. Calcula valor de cada parcela
        4. Gera parcelas em lote (bulk_create)
        5. Ajusta diferença de centavos na última parcela
    
    Args:
        request: HttpRequest object
    
    Returns:
        HttpResponse: Renderiza form ou redireciona após sucesso
    """
    if request.method == 'POST':
        form = ContaReceberForm(request.POST)
        
        if form.is_valid():
            # Salva a conta
            nova_conta = form.save(commit=False)
            nova_conta.data_emissao = date.today()
            nova_conta.save()
            
            # Extrai dados para geração de parcelas
            valor_total = form.cleaned_data['valor_total']
            num_parcelas = form.cleaned_data['numero_parcelas']
            primeiro_vencimento = form.cleaned_data['data_vencimento_primeira_parcela']
            
            # Calcula valor base da parcela com arredondamento
            valor_parcela = (valor_total / num_parcelas).quantize(
                Decimal('0.01'),
                rounding=ROUND_HALF_UP
            )
            
            # Cria lista de parcelas para inserção em lote
            parcelas_a_criar = []
            for i in range(num_parcelas):
                parcela = Parcela(
                    conta=nova_conta,
                    numero_parcela=i + 1,
                    valor_parcela=valor_parcela,
                    data_vencimento=primeiro_vencimento + relativedelta(months=i),
                    status='aberto'
                )
                parcelas_a_criar.append(parcela)
            
            # Insere todas as parcelas de uma vez (performance)
            Parcela.objects.bulk_create(parcelas_a_criar)
            
            # Ajusta diferença de centavos na última parcela
            soma_parcelas = valor_parcela * num_parcelas
            diferenca = valor_total - soma_parcelas
            
            if diferenca != 0:
                ultima_parcela = Parcela.objects.filter(
                    conta=nova_conta
                ).order_by('-numero_parcela').first()
                
                if ultima_parcela:
                    ultima_parcela.valor_parcela += diferenca
                    ultima_parcela.save()
            
            messages.success(
                request,
                f'Conta a receber lançada com sucesso! '
                f'{num_parcelas} parcela(s) gerada(s) no valor total de R$ {valor_total:.2f}.'
            )
            
            return redirect('financeiro:conta_detail', pk=nova_conta.pk)
    else:
        form = ContaReceberForm()
    
    context = {
        'form': form,
        'titulo': 'Lançar Nova Conta a Receber',
        'acao': 'Lançar Conta',
        'voltar_url': 'financeiro:conta_list'
    }
    
    return render(request, 'financeiro/conta_form.html', context)


def conta_detail(request, pk):
    """
    Exibe detalhes completos de uma conta e suas parcelas
    
    Features:
        - Atualiza status de parcelas vencidas automaticamente
        - Calcula estatísticas (total pago, pendente, percentual)
        - Lista todas as parcelas ordenadas
    
    Args:
        request: HttpRequest object
        pk: Primary key da conta
    
    Returns:
        HttpResponse: Renderiza template financeiro/conta_detail.html
    """
    conta = get_object_or_404(
        ContaReceber.objects.select_related('cliente'),
        pk=pk
    )
    
    parcelas = conta.parcelas.all().order_by('numero_parcela')
    hoje = date.today()
    
    # Atualiza status de parcelas vencidas automaticamente
    parcelas_vencidas = parcelas.filter(
        status='aberto',
        data_vencimento__lt=hoje
    )
    
    if parcelas_vencidas.exists():
        parcelas_vencidas.update(status='vencido')
        # Recarrega parcelas para refletir mudanças
        parcelas = conta.parcelas.all().order_by('numero_parcela')
    
    # Calcula estatísticas da conta
    total_pago = parcelas.filter(status='pago').aggregate(
        total=Sum('valor_parcela')
    )['total'] or Decimal('0.00')
    
    total_pendente = parcelas.filter(
        status__in=['aberto', 'vencido']
    ).aggregate(
        total=Sum('valor_parcela')
    )['total'] or Decimal('0.00')
    
    percentual_pago = 0
    if conta.valor_total > 0:
        percentual_pago = float(
            (total_pago / conta.valor_total * 100).quantize(Decimal('0.01'))
        )
    
    context = {
        'conta': conta,
        'parcelas': parcelas,
        'total_pago': total_pago,
        'total_pendente': total_pendente,
        'percentual_pago': percentual_pago,
    }
    
    return render(request, 'financeiro/conta_detail.html', context)


def conta_update(request, pk):
    """
    Atualiza dados editáveis de uma conta
    
    Permite editar apenas:
        - Descrição
        - Observações
    
    Valor, cliente e parcelas não podem ser alterados.
    
    Args:
        request: HttpRequest object
        pk: Primary key da conta
    
    Returns:
        HttpResponse: Renderiza form ou redireciona após sucesso
    """
    conta = get_object_or_404(ContaReceber, pk=pk)
    
    if request.method == 'POST':
        form = ContaReceberUpdateForm(request.POST, instance=conta)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                'Conta atualizada com sucesso!'
            )
            return redirect('financeiro:conta_detail', pk=conta.pk)
    else:
        form = ContaReceberUpdateForm(instance=conta)
    
    context = {
        'form': form,
        'titulo': f'Editar Conta: {conta.descricao}',
        'acao': 'Salvar Alterações',
        'voltar_url': 'financeiro:conta_detail',
        'voltar_pk': conta.pk,
        'conta': conta
    }
    
    return render(request, 'financeiro/conta_form.html', context)


@transaction.atomic
def conta_delete(request, pk):
    """
    Deleta uma conta e todas suas parcelas (CASCADE)
    
    Args:
        request: HttpRequest object
        pk: Primary key da conta
    
    Returns:
        HttpResponse: Renderiza confirmação ou redireciona após sucesso
    """
    conta = get_object_or_404(ContaReceber, pk=pk)
    
    # Verifica parcelas pagas
    parcelas_pagas = conta.parcelas.filter(status='pago').count()
    
    if request.method == 'POST':
        descricao = conta.descricao
        cliente_nome = conta.cliente.nome_completo
        
        conta.delete()
        
        messages.success(
            request,
            f'Conta "{descricao}" do cliente "{cliente_nome}" excluída com sucesso!'
        )
        return redirect('financeiro:conta_list')
    
    context = {
        'conta': conta,
        'parcelas_pagas': parcelas_pagas,
        'voltar_url': 'financeiro:conta_detail',
        'voltar_pk': conta.pk
    }
    
    return render(request, 'financeiro/conta_confirm_delete.html', context)


# ==============================================================================
# VIEWS DE AÇÕES DAS PARCELAS
# ==============================================================================

@require_POST
@transaction.atomic
def parcela_dar_baixa(request, pk):
    """
    Registra o pagamento de uma parcela - CORRIGIDO
    """
    parcela = get_object_or_404(Parcela, pk=pk)
    
    if parcela.status == 'pago':
        messages.warning(
            request,
            'Esta parcela já está marcada como paga.'
        )
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    
    parcela.data_pagamento = date.today()
    parcela.save()
    
    messages.success(
        request,
        f'✓ Baixa da parcela {parcela.numero_parcela}/'
        f'{parcela.conta.numero_parcelas} realizada com sucesso! '
        f'Valor: R$ {parcela.valor_parcela:.2f}'
    )
    
    return redirect('financeiro:conta_detail', pk=parcela.conta.pk)


def parcela_update(request, pk):
    """
    Edita valor e data de vencimento de uma parcela
    
    Note:
        Não permite editar parcelas já pagas
    
    Args:
        request: HttpRequest object
        pk: Primary key da parcela
    
    Returns:
        HttpResponse: Renderiza form ou redireciona após sucesso
    """
    parcela = get_object_or_404(Parcela, pk=pk)
    
    # Não permite editar parcelas pagas
    if parcela.status == 'pago':
        messages.error(
            request,
            'Não é possível editar uma parcela já paga. '
            'Estorne o pagamento primeiro se necessário.'
        )
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    
    if request.method == 'POST':
        form = ParcelaUpdateForm(request.POST, instance=parcela)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                f'Parcela {parcela.numero_parcela} atualizada com sucesso!'
            )
            return redirect('financeiro:conta_detail', pk=parcela.conta.pk)
    else:
        form = ParcelaUpdateForm(instance=parcela)
    
    context = {
        'form': form,
        'titulo': (
            f'Editar Parcela {parcela.numero_parcela}/'
            f'{parcela.conta.numero_parcelas} - '
            f'{parcela.conta.cliente.nome_completo}'
        ),
        'acao': 'Salvar Alterações',
        'voltar_url': 'financeiro:conta_detail',
        'voltar_pk': parcela.conta.pk,
        'parcela': parcela,
        'is_paid': parcela.status == 'pago'
    }
    
    return render(request, 'financeiro/parcela_update.html', context)


# ==============================================================================
# VIEWS DE RELATÓRIOS
# ==============================================================================

def relatorio_cliente_html(request, pk):
    """
    Relatório HTML do cliente
    
    Args:
        request: HttpRequest object
        pk: Primary key do cliente
    
    Returns:
        HttpResponse: Renderiza template do relatório
    """
    cliente = get_object_or_404(Cliente, pk=pk)
    contas = cliente.contas.all()
    
    context = {
        'cliente': cliente,
        'contas': contas,
    }
    
    return render(request, 'financeiro/relatorio_cliente.html', context)


def relatorio_cliente_pdf(request, pk):
    """
    Relatório PDF do cliente (em desenvolvimento)
    
    Args:
        request: HttpRequest object
        pk: Primary key do cliente
    
    Returns:
        HttpResponseRedirect: Redireciona para detalhes do cliente
    """
    messages.info(request, 'Função de PDF em desenvolvimento')
    return redirect('financeiro:cliente_detail', pk=pk)
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from io import BytesIO

def gerar_recibo_pdf(request, pk):
    """
    Gera recibo profissional em PDF - Versão Final (ajustada: emissor visível)
    """
    from io import BytesIO
    from decimal import Decimal, ROUND_HALF_UP
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages

    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import Paragraph, Frame
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER

    # Dependências opcionais
    try:
        from num2words import num2words
    except Exception:
        num2words = None

    from financeiro.models import Parcela  # ajuste o import conforme seu app

    parcela = get_object_or_404(Parcela, pk=pk)

    if parcela.status != 'pago':
        messages.error(request, 'Só é possível gerar recibo de parcelas pagas.')
        return redirect('financeiro:conta_detail', pk=parcela.conta.pk)

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    margin = 2.5 * cm

    # ========= BORDA =========
    p.saveState()
    p.setStrokeColorRGB(0.2, 0.3, 0.5)
    p.setLineWidth(2)
    p.rect(1.5*cm, 1.5*cm, width-3*cm, height-3*cm)
    p.setLineWidth(0.5)
    p.rect(1.7*cm, 1.7*cm, width-3.4*cm, height-3.4*cm)
    p.restoreState()

    # ========= CABEÇALHO =========
    y = height - 3.5 * cm
    p.setFillColorRGB(0.2, 0.3, 0.5)
    p.setFont("Helvetica-Bold", 24)
    p.drawCentredString(width/2, y, "RECIBO DE PAGAMENTO")

    y -= 0.6 * cm
    p.setFont("Helvetica", 10)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    numero_recibo = f"Nº {parcela.conta.pk:05d}/{parcela.numero_parcela:02d}"
    p.drawCentredString(width/2, y, numero_recibo)

    # Linha decorativa
    y -= 0.7 * cm
    p.setStrokeColorRGB(0.7, 0.75, 0.85)
    p.setLineWidth(1)
    p.line(margin + 2*cm, y, width - margin - 2*cm, y)

    # ========= VALOR CENTRAL =========
    y -= 2 * cm
    box_height = 1.8 * cm
    box_y = y - box_height
    box_width = width - 2*margin - 2*cm
    box_x = margin + 1*cm

    # Fundo da caixa
    p.setFillColorRGB(0.93, 0.95, 0.98)
    p.roundRect(box_x, box_y, box_width, box_height, 0.3*cm, fill=1, stroke=0)

    # Borda da caixa
    p.setStrokeColorRGB(0.3, 0.4, 0.6)
    p.setLineWidth(1.5)
    p.roundRect(box_x, box_y, box_width, box_height, 0.3*cm, fill=0, stroke=1)

    # Valor formatado BR
    valor = Decimal(parcela.valor_parcela)
    valor_str = f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')

    p.setFillColorRGB(0.1, 0.2, 0.4)
    p.setFont("Helvetica-Bold", 36)
    valor_y = box_y + (box_height / 2) - 0.3*cm
    p.drawCentredString(width/2, valor_y, valor_str)

    # ========= TEXTO JUSTIFICADO =========
    y -= 2.8 * cm

    # Valor por extenso (com Decimal, sem perdas)
    valor_centavos = (valor * 100).to_integral_value(rounding=ROUND_HALF_UP)
    inteiro = int(valor_centavos // 100)
    centavos = int(valor_centavos % 100)

    if num2words:
        try:
            valor_extenso = num2words(inteiro, lang='pt_BR')
            centavos_extenso = num2words(centavos, lang='pt_BR')
            extenso_completo = f"{valor_extenso} reais e {centavos_extenso} centavos"
        except Exception:
            extenso_completo = f"{inteiro} reais e {centavos:02d} centavos"
    else:
        extenso_completo = f"{inteiro} reais e {centavos:02d} centavos"

    cliente = parcela.conta.cliente
    cliente_nome = getattr(cliente, "nome_completo", "") or getattr(cliente, "nome", "") or "Cliente"
    cliente_cpf = getattr(cliente, "cpf_cnpj", "") or "não informado"

    style_justified = ParagraphStyle(
        'Justified',
        fontName="Helvetica",
        fontSize=11,
        leading=16,
        alignment=TA_JUSTIFY,
        firstLineIndent=1.25*cm,
        textColor=colors.HexColor('#2c3e50')
    )

    texto_recibo = (
        f"<b>Recebi</b> de <b>{cliente_nome}</b>, portador(a) do CPF/CNPJ "
        f"<b>{cliente_cpf}</b>, a quantia de <b>{valor_str}</b> "
        f"(<i>{extenso_completo}</i>), referente ao pagamento da "
        f"<b>parcela {parcela.numero_parcela}/{parcela.conta.numero_parcelas}</b> "
        f"da conta descrita como: <b>{parcela.conta.descricao}</b>."
    )

    para = Paragraph(texto_recibo, style_justified)
    # Frame para o texto principal (4 cm de altura como você já usava)
    frame = Frame(margin, y - 4*cm, width - 2*margin, 4*cm, showBoundary=0)
    frame.addFromList([para], p)

    # ========= DATAS =========
    y -= 5 * cm
    p.setFillColorRGB(0.9, 0.92, 0.95)
    p.roundRect(margin, y - 1.5*cm, width - 2*margin, 1.5*cm, 0.2*cm, fill=1, stroke=0)

    # Datas (com fallback seguro)
    p.setFillColorRGB(0.2, 0.3, 0.5)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin + 0.5*cm, y - 0.6*cm, "Data de Vencimento:")
    p.setFont("Helvetica", 10)
    try:
        venc = parcela.data_vencimento.strftime("%d/%m/%Y")
    except Exception:
        venc = "-"
    p.drawString(margin + 5*cm, y - 0.6*cm, venc)

    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin + 0.5*cm, y - 1.1*cm, "Data de Pagamento:")
    p.setFont("Helvetica", 10)
    try:
        pag = parcela.data_pagamento.strftime("%d/%m/%Y")
    except Exception:
        pag = "-"
    p.drawString(margin + 5*cm, y - 1.1*cm, pag)

    # ========= DADOS DO EMISSOR (AJUSTE CRÍTICO) =========
    # Em vez de Frame pequeno/baixo, vamos medir e desenhar o parágrafo
    y -= 2.5 * cm

    # linha separadora
    p.setStrokeColorRGB(0.7, 0.75, 0.85)
    p.setLineWidth(0.5)
    p.line(margin, y, width - margin, y)

    y -= 0.7 * cm
    p.setFillColorRGB(0.2, 0.3, 0.5)
    p.setFont("Helvetica-Bold", 10)
    p.drawString(margin, y, "DADOS DO EMISSOR")

    # Parágrafo dos dados do emissor (sem <para>, style controla o justify)
    y -= 0.6 * cm
    style_emissor = ParagraphStyle(
        'Emissor',
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        alignment=TA_JUSTIFY,
        textColor=colors.HexColor('#333333')
    )

    texto_emissor = (
        "Dr. LUCIANO HENRIQUE MEZENCIO, brasileiro, casado, filho de Iraides Câmara Mezencio "
        "e José Reis Mezencio, advogado, inscrito nos quadros da Ordem dos Advogados do Brasil "
        "sob o nº 165.740 OAB/MG, 415.401 OAB/SP, Portador do CPF: 005.904.176-57, sócio "
        "administrador no escritório MEZENCIO SOCIEDADE INDIVIDUAL DE ADVOCACIA, devidamente "
        "inscrita no cadastro de pessoa jurídica CNPJ nº 29.235.654/0001-86, todos com escritório "
        "profissional na Rua Mato Grosso, 2485, Jardim Colégio de Passos, CEP: 37900-227, "
        "Passos-Minas Gerais."
    )

    para_emissor = Paragraph(texto_emissor, style_emissor)

    # Largura disponível
    avail_w = width - 2*margin
    # Mede a altura necessária
    needed_w, needed_h = para_emissor.wrap(avail_w, height)

    # Garante que não invada a área da assinatura (reserva ~3 cm)
    assinatura_reserva = 3.5 * cm
    base_y = y  # topo onde queremos começar a desenhar
    min_y = margin + assinatura_reserva

    # Se faltar espaço, sobe o topo para caber o texto acima da assinatura
    draw_y = base_y - needed_h
    if draw_y < min_y:
        # sobe o bloco para ficar logo acima da área de assinatura
        draw_y = min_y

    para_emissor.drawOn(p, margin, draw_y)

    # ========= ASSINATURA =========
    # Linha de assinatura centralizada, garantida abaixo do bloco do emissor
    assinatura_y = draw_y - 1.2*cm  # deixa um respiro
    if assinatura_y < margin + 2.0*cm:
        assinatura_y = margin + 2.0*cm

    assinatura_x = width / 2.0
    p.setStrokeColorRGB(0.2, 0.3, 0.5)
    p.setLineWidth(1)
    p.line(assinatura_x - 4.5*cm, assinatura_y, assinatura_x + 4.5*cm, assinatura_y)

    p.setFillColorRGB(0.1, 0.2, 0.4)
    p.setFont("Helvetica-Bold", 11)
    p.drawCentredString(assinatura_x, assinatura_y - 0.5*cm, "Dr. LUCIANO HENRIQUE MEZENCIO")

    p.setFont("Helvetica", 9)
    p.setFillColorRGB(0.4, 0.4, 0.4)
    p.drawCentredString(assinatura_x, assinatura_y - 0.9*cm, "OAB/MG 165.740 | OAB/SP 415.401")

    # ========= RODAPÉ =========
    from datetime import datetime
    p.setFont("Helvetica-Oblique", 7)
    p.setFillColorRGB(0.5, 0.5, 0.5)
    data_emissao = datetime.now().strftime("%d/%m/%Y às %H:%M")
    p.drawCentredString(width/2, 2.2*cm, f"Documento emitido eletronicamente em {data_emissao}")
    p.drawCentredString(width/2, 1.9*cm, "Este recibo tem validade jurídica conforme legislação vigente")

    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="recibo_{parcela.conta.pk}_{parcela.numero_parcela}.pdf"'
    return response


def extenso_valor(valor):
    """Converte valor para extenso (versão simplificada)"""
    valor_int = int(valor)
    centavos = int((valor - valor_int) * 100)
    
    # Simplificado - você pode usar biblioteca como 'num2words' para melhorar
    if valor_int == 0:
        return f"zero reais e {centavos} centavos"
    
    return f"{valor_int} reais e {centavos:02d} centavos"