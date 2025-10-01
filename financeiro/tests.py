# financeiro/tests.py

"""
Suite Completa de Testes do Sistema Financeiro

Este módulo contém testes automatizados para:
- Modelos (Cliente, ContaReceber, Parcela)
- Formulários (validações, formatações)
- Views (CRUD, ações, relatórios)
- Funções auxiliares (utils.py)
- Integrações entre componentes

Como executar:
    python manage.py test financeiro
    python manage.py test financeiro.tests.ClienteModelTest
    python manage.py test financeiro --verbosity=2

Autor: Sistema Financeiro
Data: 2025
"""

from django.test import TestCase, Client as DjangoClient, TransactionTestCase
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.db.models import ProtectedError
from django.db import IntegrityError
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta

from .models import Cliente, ContaReceber, Parcela
from .forms import ClienteForm, ContaReceberForm, ParcelaUpdateForm, validate_cpf, validate_cnpj


# ==============================================================================
# TESTES DE MODELOS - CLIENTE
# ==============================================================================

class ClienteModelTest(TestCase):
    """Testes para o modelo Cliente"""
    
    def setUp(self):
        """Configura dados de teste executado antes de cada teste"""
        self.cliente = Cliente.objects.create(
            nome_completo='JOÃO DA SILVA',
            cpf_cnpj='123.456.789-00',
            email='joao@example.com',
            telefone='(11) 98765-4321',
            ativo=True
        )
    
    def test_cliente_creation(self):
        """Testa criação básica de cliente"""
        self.assertEqual(self.cliente.nome_completo, 'JOÃO DA SILVA')
        self.assertEqual(self.cliente.email, 'joao@example.com')
        self.assertTrue(self.cliente.ativo)
        self.assertIsNotNone(self.cliente.created_at)
        self.assertIsNotNone(self.cliente.updated_at)
    
    def test_cliente_str_representation(self):
        """Testa método __str__"""
        self.assertEqual(str(self.cliente), 'JOÃO DA SILVA')
    
    def test_get_total_divida_sem_parcelas(self):
        """Testa cálculo de dívida sem parcelas"""
        total = self.cliente.get_total_divida()
        self.assertEqual(total, Decimal('0.00'))
    
    def test_get_total_divida_com_parcelas(self):
        """Testa cálculo de dívida com parcelas pendentes"""
        conta = ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=2
        )
        Parcela.objects.create(
            conta_receber=conta,
            numero_parcela=1,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today(),
            status='A_VENCER'
        )
        Parcela.objects.create(
            conta_receber=conta,
            numero_parcela=2,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today() + timedelta(days=30),
            status='VENCIDA'
        )
        
        total = self.cliente.get_total_divida()
        self.assertEqual(total, Decimal('1000.00'))
    
    def test_get_total_pago(self):
        """Testa cálculo de total pago"""
        conta = ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=2
        )
        Parcela.objects.create(
            conta_receber=conta,
            numero_parcela=1,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today(),
            status='PAGA',
            data_pagamento=date.today()
        )
        Parcela.objects.create(
            conta_receber=conta,
            numero_parcela=2,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today() + timedelta(days=30),
            status='A_VENCER'
        )
        
        total = self.cliente.get_total_pago()
        self.assertEqual(total, Decimal('500.00'))
    
    def test_get_contas_ativas(self):
        """Testa busca de contas com parcelas pendentes"""
        conta1 = ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=1
        )
        Parcela.objects.create(
            conta_receber=conta1,
            numero_parcela=1,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today(),
            status='A_VENCER'
        )
        
        conta2 = ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('500.00'),
            numero_parcelas=1
        )
        Parcela.objects.create(
            conta_receber=conta2,
            numero_parcela=1,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today(),
            status='PAGA',
            data_pagamento=date.today()
        )
        
        contas_ativas = self.cliente.get_contas_ativas()
        self.assertEqual(contas_ativas.count(), 1)
        self.assertEqual(contas_ativas.first(), conta1)
    
    def test_get_total_contas(self):
        """Testa contagem de contas do cliente"""
        ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=1
        )
        ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('2000.00'),
            numero_parcelas=1
        )
        
        self.assertEqual(self.cliente.get_total_contas(), 2)


# ==============================================================================
# TESTES DE MODELOS - CONTA RECEBER
# ==============================================================================

class ContaReceberModelTest(TestCase):
    """Testes para o modelo ContaReceber"""
    
    def setUp(self):
        """Configura dados de teste"""
        self.cliente = Cliente.objects.create(
            nome_completo='MARIA SOUZA',
            ativo=True
        )
        self.conta = ContaReceber.objects.create(
            cliente=self.cliente,
            descricao='Honorários Advocatícios',
            valor_total=Decimal('3000.00'),
            numero_parcelas=3
        )
    
    def test_conta_creation(self):
        """Testa criação básica de conta"""
        self.assertEqual(self.conta.valor_total, Decimal('3000.00'))
        self.assertEqual(self.conta.numero_parcelas, 3)
        self.assertEqual(self.conta.cliente, self.cliente)
        self.assertIsNotNone(self.conta.data_lancamento)
    
    def test_conta_str_representation(self):
        """Testa método __str__"""
        expected = 'MARIA SOUZA - R$ 3000.00'
        self.assertEqual(str(self.conta), expected)
    
    def test_get_total_pago(self):
        """Testa cálculo de total pago"""
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=1,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today(),
            status='PAGA',
            data_pagamento=date.today()
        )
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=2,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today() + timedelta(days=30),
            status='A_VENCER'
        )
        
        total = self.conta.get_total_pago()
        self.assertEqual(total, Decimal('1000.00'))
    
    def test_get_total_pendente(self):
        """Testa cálculo de total pendente"""
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=1,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today(),
            status='A_VENCER'
        )
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=2,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today() - timedelta(days=30),
            status='VENCIDA'
        )
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=3,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today() - timedelta(days=60),
            status='PAGA',
            data_pagamento=date.today()
        )
        
        total = self.conta.get_total_pendente()
        self.assertEqual(total, Decimal('2000.00'))
    
    def test_get_percentual_pago(self):
        """Testa cálculo de percentual pago"""
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=1,
            valor_parcela=Decimal('1500.00'),
            data_vencimento=date.today(),
            status='PAGA',
            data_pagamento=date.today()
        )
        
        percentual = self.conta.get_percentual_pago()
        self.assertEqual(percentual, Decimal('50.00'))
    
    def test_is_quitada_true(self):
        """Testa verificação de conta quitada"""
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=1,
            valor_parcela=Decimal('3000.00'),
            data_vencimento=date.today(),
            status='PAGA',
            data_pagamento=date.today()
        )
        
        self.assertTrue(self.conta.is_quitada())
    
    def test_is_quitada_false(self):
        """Testa verificação de conta não quitada"""
        Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=1,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today(),
            status='A_VENCER'
        )
        
        self.assertFalse(self.conta.is_quitada())


# ==============================================================================
# TESTES DE MODELOS - PARCELA
# ==============================================================================

class ParcelaModelTest(TestCase):
    """Testes para o modelo Parcela"""
    
    def setUp(self):
        """Configura dados de teste"""
        cliente = Cliente.objects.create(
            nome_completo='TESTE PARCELA',
            ativo=True
        )
        self.conta = ContaReceber.objects.create(
            cliente=cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=2
        )
        self.parcela = Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=1,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today() - timedelta(days=10),
            status='A_VENCER'
        )
    
    def test_parcela_creation(self):
        """Testa criação básica de parcela"""
        self.assertEqual(self.parcela.valor_parcela, Decimal('500.00'))
        self.assertEqual(self.parcela.numero_parcela, 1)
        self.assertEqual(self.parcela.status, 'A_VENCER')
    
    def test_parcela_str_representation(self):
        """Testa método __str__"""
        expected = 'Parcela 1/2 - TESTE PARCELA'
        self.assertEqual(str(self.parcela), expected)
    
    def test_parcela_auto_update_status_vencida(self):
        """Testa atualização automática de status para VENCIDA"""
        self.parcela.save()
        self.parcela.refresh_from_db()
        self.assertEqual(self.parcela.status, 'VENCIDA')
    
    def test_parcela_auto_set_data_pagamento(self):
        """Testa definição automática de data de pagamento"""
        parcela = Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=2,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today(),
            status='PAGA'
        )
        self.assertIsNotNone(parcela.data_pagamento)
        self.assertEqual(parcela.data_pagamento, date.today())
    
    def test_is_vencida_true(self):
        """Testa verificação de parcela vencida"""
        self.parcela.save()  # Atualiza status
        self.assertTrue(self.parcela.is_vencida())
    
    def test_is_vencida_false_futura(self):
        """Testa verificação de parcela futura não vencida"""
        parcela = Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=3,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today() + timedelta(days=30),
            status='A_VENCER'
        )
        self.assertFalse(parcela.is_vencida())
    
    def test_dias_atraso(self):
        """Testa cálculo de dias em atraso"""
        self.parcela.save()  # Atualiza status para VENCIDA
        self.assertEqual(self.parcela.dias_atraso(), 10)
    
    def test_dias_atraso_zero_quando_paga(self):
        """Testa que parcelas pagas têm zero dias de atraso"""
        parcela = Parcela.objects.create(
            conta_receber=self.conta,
            numero_parcela=3,
            valor_parcela=Decimal('500.00'),
            data_vencimento=date.today() - timedelta(days=30),
            status='PAGA',
            data_pagamento=date.today()
        )
        self.assertEqual(parcela.dias_atraso(), 0)
    
    def test_unique_together_constraint(self):
        """Testa constraint unique_together"""
        with self.assertRaises((IntegrityError, Exception)):
            Parcela.objects.create(
                conta_receber=self.conta,
                numero_parcela=1,  # Já existe
                valor_parcela=Decimal('500.00'),
                data_vencimento=date.today()
            )


# ==============================================================================
# TESTES DE FORMULÁRIOS - CLIENTE
# ==============================================================================

class ClienteFormTest(TestCase):
    """Testes para o formulário ClienteForm"""
    
    def test_form_valid_com_cpf(self):
        """Testa formulário válido com CPF"""
        form_data = {
            'nome_completo': 'João Silva',
            'cpf_cnpj': '111.444.777-35',
            'email': 'joao@example.com',
            'telefone': '(11) 98765-4321',
            'ativo': True
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_form_invalid_cpf(self):
        """Testa formulário com CPF inválido"""
        form_data = {
            'nome_completo': 'João Silva',
            'cpf_cnpj': '111.111.111-11',
            'ativo': True
        }
        form = ClienteForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('cpf_cnpj', form.errors)
    
    def test_form_cpf_cnpj_opcional(self):
        """Testa que CPF/CNPJ é opcional"""
        form_data = {
            'nome_completo': 'João Silva',
            'ativo': True
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
    
    def test_form_nome_uppercase(self):
        """Testa conversão do nome para maiúsculas"""
        form_data = {
            'nome_completo': 'joão silva',
            'ativo': True
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
        cliente = form.save()
        self.assertEqual(cliente.nome_completo, 'JOÃO SILVA')
    
    def test_form_email_lowercase(self):
        """Testa conversão do email para minúsculas"""
        form_data = {
            'nome_completo': 'João Silva',
            'email': 'JOAO@EXAMPLE.COM',
            'ativo': True
        }
        form = ClienteForm(data=form_data)
        self.assertTrue(form.is_valid())
        cliente = form.save()
        self.assertEqual(cliente.email, 'joao@example.com')


# ==============================================================================
# TESTES DE FORMULÁRIOS - CONTA RECEBER
# ==============================================================================

class ContaReceberFormTest(TestCase):
    """Testes para o formulário ContaReceberForm"""
    
    def setUp(self):
        """Configura dados de teste"""
        self.cliente = Cliente.objects.create(
            nome_completo='TESTE',
            ativo=True
        )
    
    def test_form_valid(self):
        """Testa formulário válido"""
        form_data = {
            'cliente': self.cliente.pk,
            'descricao': 'Honorários',
            'valor_total': Decimal('1000.00'),
            'numero_parcelas': 3,
            'data_vencimento_primeira_parcela': date.today() + timedelta(days=30),
            'observacoes': 'Teste'
        }
        form = ContaReceberForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_form_invalid_valor_zero(self):
        """Testa validação de valor zero"""
        form_data = {
            'cliente': self.cliente.pk,
            'descricao': 'Teste',
            'valor_total': Decimal('0.00'),
            'numero_parcelas': 1,
            'data_vencimento_primeira_parcela': date.today()
        }
        form = ContaReceberForm(data=form_data)
        self.assertFalse(form.is_valid())
    
    def test_form_invalid_numero_parcelas_zero(self):
        """Testa validação de número de parcelas zero"""
        form_data = {
            'cliente': self.cliente.pk,
            'descricao': 'Teste',
            'valor_total': Decimal('1000.00'),
            'numero_parcelas': 0,
            'data_vencimento_primeira_parcela': date.today()
        }
        form = ContaReceberForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('numero_parcelas', form.errors)
    
    def test_form_invalid_data_passado(self):
        """Testa validação de data no passado"""
        form_data = {
            'cliente': self.cliente.pk,
            'descricao': 'Teste',
            'valor_total': Decimal('1000.00'),
            'numero_parcelas': 1,
            'data_vencimento_primeira_parcela': date.today() - timedelta(days=1)
        }
        form = ContaReceberForm(data=form_data)
        self.assertFalse(form.is_valid())


# ==============================================================================
# TESTES DE VALIDAÇÃO (CPF/CNPJ)
# ==============================================================================

class ValidationTest(TestCase):
    """Testes para funções de validação"""
    
    def test_validate_cpf_valido(self):
        """Testa validação de CPFs válidos"""
        cpfs_validos = [
            '111.444.777-35',
            '11144477735',
        ]
        
        for cpf in cpfs_validos:
            with self.subTest(cpf=cpf):
                self.assertTrue(validate_cpf(cpf))
    
    def test_validate_cpf_invalido(self):
        """Testa validação de CPFs inválidos"""
        cpfs_invalidos = [
            '111.111.111-11',
            '123.456.789-00',
            '000.000.000-00',
        ]
        
        for cpf in cpfs_invalidos:
            with self.subTest(cpf=cpf):
                self.assertFalse(validate_cpf(cpf))
    
    def test_validate_cpf_tamanho_incorreto(self):
        """Testa CPF com tamanho incorreto"""
        self.assertFalse(validate_cpf('123'))
        self.assertFalse(validate_cpf('12345678901234'))
    
    def test_validate_cnpj_valido(self):
        """Testa validação de CNPJs válidos"""
        cnpjs_validos = [
            '11.222.333/0001-81',
            '11222333000181',
        ]
        
        for cnpj in cnpjs_validos:
            with self.subTest(cnpj=cnpj):
                self.assertTrue(validate_cnpj(cnpj))
    
    def test_validate_cnpj_invalido(self):
        """Testa validação de CNPJs inválidos"""
        cnpjs_invalidos = [
            '11.111.111/1111-11',
            '00.000.000/0000-00',
        ]
        
        for cnpj in cnpjs_invalidos:
            with self.subTest(cnpj=cnpj):
                self.assertFalse(validate_cnpj(cnpj))


# ==============================================================================
# TESTES DE VIEWS
# ==============================================================================

class ViewsTest(TestCase):
    """Testes para as views"""
    
    def setUp(self):
        """Configura cliente de teste"""
        self.client_http = DjangoClient()
        self.cliente = Cliente.objects.create(
            nome_completo='TESTE VIEW',
            ativo=True
        )
    
    def test_index_view_status_code(self):
        """Testa se dashboard carrega corretamente"""
        response = self.client_http.get(reverse('financeiro:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_cliente_list_view(self):
        """Testa listagem de clientes"""
        response = self.client_http.get(reverse('financeiro:cliente_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'TESTE VIEW')
    
    def test_cliente_create_view_get(self):
        """Testa view de criação de cliente (GET)"""
        response = self.client_http.get(reverse('financeiro:cliente_create'))
        self.assertEqual(response.status_code, 200)
    
    def test_conta_list_view(self):
        """Testa listagem de contas"""
        response = self.client_http.get(reverse('financeiro:conta_list'))
        self.assertEqual(response.status_code, 200)
    
    def test_parcela_dar_baixa(self):
        """Testa dar baixa em parcela"""
        conta = ContaReceber.objects.create(
            cliente=self.cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=1
        )
        parcela = Parcela.objects.create(
            conta_receber=conta,
            numero_parcela=1,
            valor_parcela=Decimal('1000.00'),
            data_vencimento=date.today(),
            status='A_VENCER'
        )
        
        response = self.client_http.post(
            reverse('financeiro:parcela_dar_baixa', kwargs={'pk': parcela.pk})
        )
        
        parcela.refresh_from_db()
        self.assertEqual(parcela.status, 'PAGA')
        self.assertIsNotNone(parcela.data_pagamento)
        self.assertEqual(response.status_code, 302)


# ==============================================================================
# TESTES DE INTEGRAÇÃO
# ==============================================================================

class IntegrationTest(TransactionTestCase):
    """Testes de integração do sistema"""
    
    def test_fluxo_completo_conta(self):
        """Testa fluxo completo: criar conta, gerar parcelas, dar baixa"""
        # 1. Cria cliente
        cliente = Cliente.objects.create(
            nome_completo='CLIENTE TESTE',
            cpf_cnpj='111.444.777-35',
            ativo=True
        )
        
        # 2. Cria conta
        conta = ContaReceber.objects.create(
            cliente=cliente,
            descricao='Honorários de Teste',
            valor_total=Decimal('3000.00'),
            numero_parcelas=3
        )
        
        # 3. Cria parcelas
        for i in range(3):
            Parcela.objects.create(
                conta_receber=conta,
                numero_parcela=i + 1,
                valor_parcela=Decimal('1000.00'),
                data_vencimento=date.today() + relativedelta(months=i),
                status='A_VENCER'
            )
        
        # 4. Verifica criação
        self.assertEqual(conta.parcelas.count(), 3)
        self.assertEqual(conta.get_total_pendente(), Decimal('3000.00'))
        self.assertEqual(conta.get_total_pago(), Decimal('0.00'))
        
        # 5. Dá baixa na primeira parcela
        primeira_parcela = conta.parcelas.first()
        primeira_parcela.status = 'PAGA'
        primeira_parcela.data_pagamento = date.today()
        primeira_parcela.save()
        
        # 6. Verifica pagamento
        self.assertEqual(conta.get_total_pago(), Decimal('1000.00'))
        self.assertEqual(conta.get_total_pendente(), Decimal('2000.00'))
        self.assertFalse(conta.is_quitada())
        
        # 7. Paga todas as parcelas
        conta.parcelas.update(status='PAGA', data_pagamento=date.today())
        
        # 8. Verifica quitação
        self.assertTrue(conta.is_quitada())
        self.assertEqual(conta.get_total_pago(), Decimal('3000.00'))
    
    def test_protecao_delete_cliente_com_contas(self):
        """Testa que não é possível deletar cliente com contas"""
        cliente = Cliente.objects.create(nome_completo='TESTE', ativo=True)
        ContaReceber.objects.create(
            cliente=cliente,
            valor_total=Decimal('1000.00'),
            numero_parcelas=1
        )
        
        # Deve lançar exceção ao tentar deletar
        with self.assertRaises(ProtectedError):
            cliente.delete()