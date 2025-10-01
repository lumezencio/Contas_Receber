# Aequitas - Contas a Receber

Um sistema simples e eficiente para gerenciamento de Contas a Receber, desenvolvido para escritórios e pequenas empresas.

##  sobre o Projeto

O Aequitas foi criado para simplificar o controle financeiro, focando no fluxo de recebimentos. Ele permite o cadastro de clientes, o lançamento de títulos e o acompanhamento de vencimentos e pagamentos de forma clara e objetiva.

Este projeto foi construído utilizando o framework web Django, com a linguagem Python.

## Funcionalidades Principais

* **Cadastro de Clientes:** Mantenha uma base de dados organizada dos seus clientes.
* **Lançamento de Títulos:** Registre novas contas a receber com informações como valor, data de emissão e data de vencimento.
* **Controle de Pagamentos:** Dê baixa nos títulos que foram pagos.
* **Dashboard Simples:** Visualize rapidamente os títulos vencidos, a vencer e os pagos.
* **Relatórios:** Exporte relatórios básicos para análise.

## Tecnologias Utilizadas

* [Python](https://www.python.org/)
* [Django](https://www.djangoproject.com/)
* [SQLite](https://www.sqlite.org/index.html) (Banco de dados padrão de desenvolvimento)
* HTML / CSS / JavaScript

## Instalação e Execução

Para rodar este projeto localmente, siga os passos abaixo:

1.  **Clone o repositório:**
    ```bash
    git clone [https://github.com/lumezencio/Contas_Receber.git](https://github.com/lumezencio/Contas_Receber.git)
    ```

2.  **Acesse a pasta do projeto:**
    ```bash
    cd Contas_Receber
    ```

3.  **Crie e ative um ambiente virtual:**
    ```bash
    # Criar o ambiente
    python -m venv venv

    # Ativar no Windows
    .\venv\Scripts\activate
    ```

4.  **Instale as dependências:**
    (Primeiro, certifique-se de ter um arquivo `requirements.txt`. Se não tiver, gere-o com: `pip freeze > requirements.txt`)
    ```bash
    pip install -r requirements.txt
    ```

5.  **Aplique as migrações do banco de dados:**
    ```bash
    python manage.py migrate
    ```

6.  **Execute o servidor de desenvolvimento:**
    ```bash
    python manage.py runserver
    ```
    O projeto estará disponível em `http://127.0.0.1:8000`.

## Autor

Desenvolvido por **Luciano Henrique Mezencio**.
