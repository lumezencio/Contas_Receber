# financeiro/apps.py

"""
Configuração da Aplicação Financeiro

Este módulo define as configurações básicas da aplicação Django,
incluindo nome, label e configurações de inicialização.

O método ready() é executado uma vez quando o Django inicia,
sendo ideal para:
- Registro de signals
- Importação de tarefas assíncronas (Celery)
- Verificações de sistema customizadas
- Configurações de logging

Autor: Sistema Financeiro
Data: 2025
"""

from django.apps import AppConfig


class FinanceiroConfig(AppConfig):
    """
    Classe de configuração para a aplicação Financeiro
    
    Attributes:
        default_auto_field: Tipo de campo para chaves primárias automáticas
        name: Nome interno da aplicação (deve corresponder ao diretório)
        verbose_name: Nome amigável exibido no Django Admin
    
    Example:
        No settings.py:
        INSTALLED_APPS = [
            ...
            'financeiro.apps.FinanceiroConfig',
            ...
        ]
    """
    
    # Define o tipo de campo auto-incremento padrão para PKs
    # BigAutoField suporta valores até 9.223.372.036.854.775.807
    default_auto_field = 'django.db.models.BigAutoField'
    
    # Nome da aplicação (deve corresponder ao nome do diretório)
    name = 'financeiro'
    
    # Nome amigável exibido no Django Admin
    verbose_name = 'Sistema Financeiro'
    
    def ready(self):
        """
        Método executado quando a aplicação está pronta
        
        Este método é chamado uma única vez durante a inicialização
        do Django, após todos os modelos serem carregados.
        
        Use cases:
            - Registrar signals para automação de eventos
            - Importar tarefas do Celery para execução assíncrona
            - Configurar checks customizados do sistema
            - Inicializar conexões externas
            - Configurar logging específico da aplicação
        
        Warning:
            Evite operações pesadas ou queries ao banco de dados aqui,
            pois isso pode aumentar o tempo de inicialização da aplicação.
        
        Example:
            >>> def ready(self):
            ...     # Importa signals
            ...     import financeiro.signals
            ...     
            ...     # Importa tarefas do Celery
            ...     import financeiro.tasks
            ...     
            ...     # Registra checks customizados
            ...     from django.core.checks import register
            ...     from .checks import check_configuracao_financeira
            ...     register(check_configuracao_financeira)
        """
        
        # =======================================================================
        # IMPORTAÇÃO DE SIGNALS (SE HOUVER)
        # =======================================================================
        # Descomente a linha abaixo quando criar o módulo signals.py
        # import financeiro.signals
        
        # Signals úteis para este sistema:
        # - pre_save/post_save: Auditar alterações em modelos
        # - pre_delete/post_delete: Registrar exclusões
        # - m2m_changed: Monitorar mudanças em relacionamentos
        
        
        # =======================================================================
        # IMPORTAÇÃO DE TAREFAS ASSÍNCRONAS (CELERY)
        # =======================================================================
        # Descomente a linha abaixo quando configurar o Celery
        # import financeiro.tasks
        
        # Tarefas úteis para este sistema:
        # - Enviar emails de cobrança para parcelas vencidas
        # - Gerar relatórios mensais automaticamente
        # - Atualizar status de parcelas em lote
        # - Calcular juros e multas automaticamente
        # - Enviar lembretes de vencimento
        
        
        # =======================================================================
        # CONFIGURAÇÃO DE LOGGING
        # =======================================================================
        # import logging
        # logger = logging.getLogger('financeiro')
        # logger.info('Aplicação Financeiro inicializada com sucesso')
        
        
        # =======================================================================
        # VERIFICAÇÕES DE SISTEMA (SYSTEM CHECKS)
        # =======================================================================
        # from django.core.checks import register, Warning
        # 
        # @register()
        # def check_weasyprint_instalado(app_configs, **kwargs):
        #     """Verifica se WeasyPrint está instalado para geração de PDFs"""
        #     errors = []
        #     try:
        #         import weasyprint
        #     except ImportError:
        #         errors.append(
        #             Warning(
        #                 'WeasyPrint não está instalado',
        #                 hint='Instale com: pip install weasyprint',
        #                 id='financeiro.W001',
        #             )
        #         )
        #     return errors
        
        
        # =======================================================================
        # PLACEHOLDER PARA FUTURAS IMPLEMENTAÇÕES
        # =======================================================================
        # Por enquanto, mantemos o método vazio mas documentado
        # para facilitar futuras expansões do sistema
        pass


# ==============================================================================
# CONFIGURAÇÕES ADICIONAIS (OPCIONAL)
# ==============================================================================

# Se você precisar de múltiplas configurações para diferentes ambientes,
# pode criar subclasses desta config:

# class FinanceiroDevConfig(FinanceiroConfig):
#     """Configuração para ambiente de desenvolvimento"""
#     verbose_name = 'Sistema Financeiro (DEV)'
#     
#     def ready(self):
#         super().ready()
#         # Configurações específicas de desenvolvimento
#         import logging
#         logging.getLogger('financeiro').setLevel(logging.DEBUG)


# class FinanceiroProdConfig(FinanceiroConfig):
#     """Configuração para ambiente de produção"""
#     verbose_name = 'Sistema Financeiro'
#     
#     def ready(self):
#         super().ready()
#         # Configurações específicas de produção
#         # Ativa monitoramento, sentry, etc
#         pass