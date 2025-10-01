# financeiro/utils.py

"""
Módulo de Utilidades e Funções Auxiliares

Este módulo contém funções helper utilizadas em todo o sistema:
- Formatação de dados (CPF, CNPJ, telefone, moeda)
- Cálculos financeiros (parcelas, juros, multas)
- Manipulação de datas (vencimentos, dias úteis)
- Validações e análises
- Geração de relatórios

Autor: Sistema Financeiro
Data: 2025
"""

from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import List, Tuple, Optional, Dict
from dateutil.relativedelta import relativedelta
import re


# ==============================================================================
# FUNÇÕES DE FORMATAÇÃO
# ==============================================================================

def formatar_cpf(cpf: str) -> str:
    """
    Formata CPF para o padrão brasileiro XXX.XXX.XXX-XX
    
    Args:
        cpf: String com CPF (pode conter ou não formatação)
    
    Returns:
        str: CPF formatado ou string original se inválido
    
    Example:
        >>> formatar_cpf('12345678900')
        '123.456.789-00'
        >>> formatar_cpf('123.456.789-00')
        '123.456.789-00'
    """
    # Remove qualquer caractere não numérico
    cpf_limpo = ''.join(filter(str.isdigit, str(cpf)))
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return cpf
    
    # Formata: XXX.XXX.XXX-XX
    return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"


def formatar_cnpj(cnpj: str) -> str:
    """
    Formata CNPJ para o padrão brasileiro XX.XXX.XXX/XXXX-XX
    
    Args:
        cnpj: String com CNPJ (pode conter ou não formatação)
    
    Returns:
        str: CNPJ formatado ou string original se inválido
    
    Example:
        >>> formatar_cnpj('12345678000190')
        '12.345.678/0001-90'
    """
    # Remove qualquer caractere não numérico
    cnpj_limpo = ''.join(filter(str.isdigit, str(cnpj)))
    
    # Verifica se tem 14 dígitos
    if len(cnpj_limpo) != 14:
        return cnpj
    
    # Formata: XX.XXX.XXX/XXXX-XX
    return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"


def formatar_documento(documento: str) -> str:
    """
    Formata CPF ou CNPJ automaticamente baseado no tamanho
    
    Args:
        documento: String com CPF ou CNPJ
    
    Returns:
        str: Documento formatado
    
    Example:
        >>> formatar_documento('12345678900')
        '123.456.789-00'
        >>> formatar_documento('12345678000190')
        '12.345.678/0001-90'
    """
    doc_limpo = ''.join(filter(str.isdigit, str(documento)))
    
    if len(doc_limpo) == 11:
        return formatar_cpf(documento)
    elif len(doc_limpo) == 14:
        return formatar_cnpj(documento)
    
    return documento


def formatar_telefone(telefone: str) -> str:
    """
    Formata telefone brasileiro para (XX) XXXXX-XXXX ou (XX) XXXX-XXXX
    
    Args:
        telefone: String com telefone (apenas números)
    
    Returns:
        str: Telefone formatado ou string original se inválido
    
    Example:
        >>> formatar_telefone('11987654321')
        '(11) 98765-4321'
        >>> formatar_telefone('1133334444')
        '(11) 3333-4444'
    """
    # Remove qualquer caractere não numérico
    tel_limpo = ''.join(filter(str.isdigit, str(telefone)))
    
    # Celular com 11 dígitos: (XX) XXXXX-XXXX
    if len(tel_limpo) == 11:
        return f"({tel_limpo[:2]}) {tel_limpo[2:7]}-{tel_limpo[7:]}"
    
    # Fixo com 10 dígitos: (XX) XXXX-XXXX
    elif len(tel_limpo) == 10:
        return f"({tel_limpo[:2]}) {tel_limpo[2:6]}-{tel_limpo[6:]}"
    
    return telefone


def formatar_moeda(valor: Decimal, simbolo: bool = True) -> str:
    """
    Formata valor monetário para o padrão brasileiro
    
    Args:
        valor: Valor em Decimal
        simbolo: Se True, inclui "R$ " no início
    
    Returns:
        str: Valor formatado (ex: R$ 1.234,56)
    
    Example:
        >>> formatar_moeda(Decimal('1234.56'))
        'R$ 1.234,56'
        >>> formatar_moeda(Decimal('1234.56'), simbolo=False)
        '1.234,56'
    """
    # Converte para string com 2 casas decimais
    valor_str = f"{float(valor):,.2f}"
    
    # Substitui separadores: 1,234.56 -> 1.234,56
    valor_formatado = valor_str.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    if simbolo:
        return f"R$ {valor_formatado}"
    
    return valor_formatado


def formatar_data(data: date, formato: str = 'completo') -> str:
    """
    Formata data em português brasileiro
    
    Args:
        data: Objeto date
        formato: 'completo', 'curto', 'mes_ano', 'extenso'
    
    Returns:
        str: Data formatada
    
    Example:
        >>> formatar_data(date(2025, 9, 29), 'completo')
        '29/09/2025'
        >>> formatar_data(date(2025, 9, 29), 'extenso')
        '29 de Setembro de 2025'
    """
    meses = {
        1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril',
        5: 'Maio', 6: 'Junho', 7: 'Julho', 8: 'Agosto',
        9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
    }
    
    if formato == 'completo':
        return data.strftime('%d/%m/%Y')
    
    elif formato == 'curto':
        return data.strftime('%d/%m/%y')
    
    elif formato == 'mes_ano':
        return f"{meses[data.month]}/{data.year}"
    
    elif formato == 'extenso':
        return f"{data.day} de {meses[data.month]} de {data.year}"
    
    return data.strftime('%d/%m/%Y')


# ==============================================================================
# FUNÇÕES DE CÁLCULO FINANCEIRO
# ==============================================================================

def calcular_parcelas(
    valor_total: Decimal,
    numero_parcelas: int,
    ajustar_ultima: bool = True
) -> List[Decimal]:
    """
    Calcula valores de parcelas com ajuste de centavos
    
    Distribui o valor total em parcelas iguais, ajustando
    a diferença de arredondamento na última parcela.
    
    Args:
        valor_total: Valor total a ser parcelado
        numero_parcelas: Número de parcelas
        ajustar_ultima: Se True, ajusta diferença na última parcela
    
    Returns:
        List[Decimal]: Lista com valor de cada parcela
    
    Example:
        >>> calcular_parcelas(Decimal('1000.00'), 3)
        [Decimal('333.33'), Decimal('333.33'), Decimal('333.34')]
    """
    # Calcula valor base da parcela
    valor_parcela = (valor_total / numero_parcelas).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    # Cria lista de parcelas
    parcelas = [valor_parcela] * numero_parcelas
    
    # Ajusta diferença de centavos na última parcela
    if ajustar_ultima:
        soma_parcelas = valor_parcela * numero_parcelas
        diferenca = valor_total - soma_parcelas
        parcelas[-1] += diferenca
    
    return parcelas


def calcular_juros_simples(
    valor_principal: Decimal,
    taxa_mensal: Decimal,
    meses: int
) -> Decimal:
    """
    Calcula juros simples
    
    Fórmula: J = P × i × t
    Onde: J = juros, P = principal, i = taxa, t = tempo
    
    Args:
        valor_principal: Valor principal (capital)
        taxa_mensal: Taxa de juros mensal em % (ex: 2.5 para 2,5%)
        meses: Período em meses
    
    Returns:
        Decimal: Valor dos juros
    
    Example:
        >>> calcular_juros_simples(Decimal('1000'), Decimal('2.5'), 3)
        Decimal('75.00')
    """
    taxa_decimal = taxa_mensal / 100
    juros = valor_principal * taxa_decimal * meses
    
    return juros.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_juros_compostos(
    valor_principal: Decimal,
    taxa_mensal: Decimal,
    meses: int
) -> Decimal:
    """
    Calcula montante com juros compostos
    
    Fórmula: M = P × (1 + i)^t
    Onde: M = montante, P = principal, i = taxa, t = tempo
    
    Args:
        valor_principal: Valor principal (capital)
        taxa_mensal: Taxa de juros mensal em % (ex: 2.5 para 2,5%)
        meses: Período em meses
    
    Returns:
        Decimal: Montante total (principal + juros)
    
    Example:
        >>> calcular_juros_compostos(Decimal('1000'), Decimal('2.5'), 3)
        Decimal('1076.89')
    """
    taxa_decimal = taxa_mensal / 100
    montante = valor_principal * ((1 + taxa_decimal) ** meses)
    
    return Decimal(str(montante)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calcular_multa_atraso(
    valor_parcela: Decimal,
    dias_atraso: int,
    percentual_multa: Decimal = Decimal('2.0'),
    percentual_juros_dia: Decimal = Decimal('0.033')
) -> Tuple[Decimal, Decimal, Decimal]:
    """
    Calcula multa e juros por atraso no pagamento
    
    Padrão brasileiro:
    - Multa: 2% do valor da parcela
    - Juros: 1% ao mês (0,033% ao dia) pro rata
    
    Args:
        valor_parcela: Valor da parcela
        dias_atraso: Quantidade de dias em atraso
        percentual_multa: Percentual de multa (padrão 2%)
        percentual_juros_dia: Percentual de juros ao dia (padrão 0.033%)
    
    Returns:
        Tuple[Decimal, Decimal, Decimal]: (multa, juros, total_com_encargos)
    
    Example:
        >>> calcular_multa_atraso(Decimal('1000'), 30)
        (Decimal('20.00'), Decimal('9.90'), Decimal('1029.90'))
    """
    if dias_atraso <= 0:
        return Decimal('0.00'), Decimal('0.00'), valor_parcela
    
    # Calcula multa (fixo sobre o valor)
    multa = (valor_parcela * percentual_multa / 100).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    # Calcula juros (proporcional aos dias)
    juros = (valor_parcela * percentual_juros_dia * dias_atraso / 100).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    # Valor total com encargos
    total = valor_parcela + multa + juros
    
    return multa, juros, total


def calcular_desconto(
    valor_parcela: Decimal,
    dias_antecipacao: int,
    percentual_desconto_dia: Decimal = Decimal('0.1')
) -> Tuple[Decimal, Decimal]:
    """
    Calcula desconto por pagamento antecipado
    
    Args:
        valor_parcela: Valor da parcela
        dias_antecipacao: Quantidade de dias de antecipação
        percentual_desconto_dia: Desconto ao dia (padrão 0.1%)
    
    Returns:
        Tuple[Decimal, Decimal]: (desconto, valor_final)
    
    Example:
        >>> calcular_desconto(Decimal('1000'), 10)
        (Decimal('10.00'), Decimal('990.00'))
    """
    if dias_antecipacao <= 0:
        return Decimal('0.00'), valor_parcela
    
    # Calcula desconto
    desconto = (valor_parcela * percentual_desconto_dia * dias_antecipacao / 100).quantize(
        Decimal('0.01'),
        rounding=ROUND_HALF_UP
    )
    
    # Valor final com desconto
    valor_final = valor_parcela - desconto
    
    return desconto, valor_final


# ==============================================================================
# FUNÇÕES DE MANIPULAÇÃO DE DATAS
# ==============================================================================

def gerar_datas_vencimento(
    data_inicial: date,
    numero_parcelas: int,
    dia_fixo: Optional[int] = None
) -> List[date]:
    """
    Gera lista de datas de vencimento para parcelas
    
    Args:
        data_inicial: Data de vencimento da primeira parcela
        numero_parcelas: Número total de parcelas
        dia_fixo: Se fornecido, mantém dia fixo (ex: sempre dia 10)
    
    Returns:
        List[date]: Lista com datas de vencimento
    
    Example:
        >>> gerar_datas_vencimento(date(2025, 1, 15), 3)
        [date(2025, 1, 15), date(2025, 2, 15), date(2025, 3, 15)]
        >>> gerar_datas_vencimento(date(2025, 1, 15), 3, dia_fixo=10)
        [date(2025, 1, 10), date(2025, 2, 10), date(2025, 3, 10)]
    """
    datas = []
    
    for i in range(numero_parcelas):
        if dia_fixo:
            # Mantém dia fixo do mês
            nova_data = data_inicial + relativedelta(months=i)
            try:
                nova_data = nova_data.replace(day=dia_fixo)
            except ValueError:
                # Dia não existe no mês (ex: 31 em fevereiro)
                # Usa último dia do mês
                nova_data = nova_data + relativedelta(day=31)
        else:
            # Usa data relativa (mantém dia original)
            nova_data = data_inicial + relativedelta(months=i)
        
        datas.append(nova_data)
    
    return datas


def calcular_dias_uteis(data_inicio: date, data_fim: date) -> int:
    """
    Calcula dias úteis entre duas datas (exclui sábados e domingos)
    
    Args:
        data_inicio: Data inicial
        data_fim: Data final
    
    Returns:
        int: Quantidade de dias úteis
    
    Example:
        >>> calcular_dias_uteis(date(2025, 1, 1), date(2025, 1, 10))
        7
    """
    dias_uteis = 0
    data_atual = data_inicio
    
    while data_atual <= data_fim:
        # 0 = Segunda, 6 = Domingo
        if data_atual.weekday() < 5:  # Segunda a Sexta
            dias_uteis += 1
        data_atual += timedelta(days=1)
    
    return dias_uteis


def proximo_dia_util(data: date, avancar: bool = True) -> date:
    """
    Retorna o próximo dia útil (ou anterior)
    
    Args:
        data: Data de referência
        avancar: Se True avança, se False retrocede
    
    Returns:
        date: Próximo/anterior dia útil
    
    Example:
        >>> proximo_dia_util(date(2025, 1, 4))  # Sábado
        date(2025, 1, 6)  # Segunda
    """
    delta = timedelta(days=1 if avancar else -1)
    proxima_data = data + delta
    
    while proxima_data.weekday() >= 5:  # Sábado ou Domingo
        proxima_data += delta
    
    return proxima_data


def calcular_idade_dias(data_inicial: date, data_final: Optional[date] = None) -> int:
    """
    Calcula idade em dias entre duas datas
    
    Args:
        data_inicial: Data inicial
        data_final: Data final (padrão: hoje)
    
    Returns:
        int: Quantidade de dias
    
    Example:
        >>> calcular_idade_dias(date(2025, 1, 1), date(2025, 1, 31))
        30
    """
    if data_final is None:
        data_final = date.today()
    
    return (data_final - data_inicial).days


# ==============================================================================
# FUNÇÕES DE VALIDAÇÃO E ANÁLISE
# ==============================================================================

def validar_valor_minimo_parcela(
    valor_total: Decimal,
    numero_parcelas: int,
    valor_minimo: Decimal = Decimal('50.00')
) -> Tuple[bool, str]:
    """
    Valida se o valor da parcela atinge o mínimo exigido
    
    Args:
        valor_total: Valor total
        numero_parcelas: Número de parcelas
        valor_minimo: Valor mínimo aceitável por parcela
    
    Returns:
        Tuple[bool, str]: (é_valido, mensagem)
    
    Example:
        >>> validar_valor_minimo_parcela(Decimal('100'), 3, Decimal('50'))
        (False, 'Valor da parcela (R$ 33,33) abaixo do mínimo (R$ 50,00)')
    """
    valor_parcela = valor_total / numero_parcelas
    
    if valor_parcela < valor_minimo:
        return False, (
            f"Valor da parcela (R$ {valor_parcela:.2f}) está abaixo do "
            f"mínimo permitido (R$ {valor_minimo:.2f})"
        )
    
    return True, "OK"


def analisar_inadimplencia(
    total_divida: Decimal,
    total_vencido: Decimal
) -> Tuple[str, str, float]:
    """
    Analisa nível de inadimplência do cliente
    
    Args:
        total_divida: Total de dívida (a vencer + vencida)
        total_vencido: Total vencido
    
    Returns:
        Tuple[str, str, float]: (nivel, descricao, percentual)
    
    Example:
        >>> analisar_inadimplencia(Decimal('1000'), Decimal('600'))
        ('ALTA', 'Alto índice de inadimplência', 60.0)
    """
    if total_divida == 0:
        return 'NENHUMA', 'Sem dívidas', 0.0
    
    percentual = float((total_vencido / total_divida) * 100)
    
    if percentual == 0:
        return 'NENHUMA', 'Todas as parcelas em dia', 0.0
    elif percentual < 25:
        return 'BAIXA', 'Poucas parcelas vencidas', percentual
    elif percentual < 50:
        return 'MÉDIA', 'Inadimplência moderada', percentual
    elif percentual < 75:
        return 'ALTA', 'Alto índice de inadimplência', percentual
    else:
        return 'CRÍTICA', 'Inadimplência crítica', percentual


def calcular_estatisticas_conta(conta) -> Dict:
    """
    Calcula estatísticas completas de uma conta
    
    Args:
        conta: Instância de ContaReceber
    
    Returns:
        Dict: Dicionário com todas as estatísticas
    
    Example:
        >>> stats = calcular_estatisticas_conta(conta)
        >>> stats['percentual_pago']
        75.5
    """
    parcelas = conta.parcelas.all()
    
    stats = {
        'total_parcelas': parcelas.count(),
        'pagas': parcelas.filter(status='PAGA').count(),
        'a_vencer': parcelas.filter(status='A_VENCER').count(),
        'vencidas': parcelas.filter(status='VENCIDA').count(),
        'canceladas': parcelas.filter(status='CANCELADA').count(),
        'valor_pago': conta.get_total_pago(),
        'valor_pendente': conta.get_total_pendente(),
        'percentual_pago': float(conta.get_percentual_pago()),
        'quitada': conta.is_quitada(),
    }
    
    # Calcula maior atraso
    parcelas_vencidas = parcelas.filter(status='VENCIDA')
    if parcelas_vencidas.exists():
        stats['maior_atraso'] = max(p.dias_atraso() for p in parcelas_vencidas)
    else:
        stats['maior_atraso'] = 0
    
    return stats


# ==============================================================================
# FUNÇÕES DE EXPORTAÇÃO E RELATÓRIOS
# ==============================================================================

def gerar_linha_csv(dados: List) -> str:
    """
    Gera linha formatada para arquivo CSV
    
    Args:
        dados: Lista de valores
    
    Returns:
        str: Linha CSV com delimitadores e escape
    
    Example:
        >>> gerar_linha_csv(['João', '1000', 'Pago'])
        '"João","1000","Pago"\\n'
    """
    # Converte para string e escapa aspas duplas
    dados_formatados = []
    for dado in dados:
        valor = str(dado).replace('"', '""')
        dados_formatados.append(f'"{valor}"')
    
    return ','.join(dados_formatados) + '\n'


def preparar_dados_cliente_relatorio(cliente) -> Dict:
    """
    Prepara todos os dados do cliente para relatório
    
    Args:
        cliente: Instância de Cliente
    
    Returns:
        Dict: Dados formatados para relatório
    """
    from django.db.models import Sum
    
    contas = cliente.contas.all()
    
    dados = {
        'cliente': {
            'nome': cliente.nome_completo,
            'cpf_cnpj': formatar_documento(cliente.cpf_cnpj) if cliente.cpf_cnpj else 'N/A',
            'email': cliente.email or 'N/A',
            'telefone': cliente.telefone or 'N/A',
            'data_cadastro': formatar_data(cliente.created_at.date()),
        },
        'financeiro': {
            'total_contas': contas.count(),
            'valor_total': sum(c.valor_total for c in contas),
            'total_pago': cliente.get_total_pago(),
            'total_pendente': cliente.get_total_divida(),
        }
    }
    
    return dados