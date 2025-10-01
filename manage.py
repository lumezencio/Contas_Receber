{% extends 'base.html' %}

{% block title %}Clientes - AEQUITAS{% endblock %}

{% block content %}
<div class="flex justify-between items-center mb-6">
    <h1 class="text-3xl font-bold text-white">Cadastro de Clientes</h1>
    
    {# LINK CORRIGIDO #}
    <a href="{% url 'financeiro:cliente_create' %}" class="bg-cyan-500 hover:bg-cyan-600 text-white font-bold py-2 px-4 rounded-lg">
        Adicionar Novo Cliente
    </a>
</div>

<div class="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
    <table class="min-w-full">
        <thead class="bg-gray-700">
            <tr>
                <th class="py-3 px-6 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Nome Completo</th>
                <th class="py-3 px-6 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">CPF/CNPJ</th>
                <th class="py-3 px-6 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Telefone</th>
                <th class="py-3 px-6 text-left text-xs font-medium text-gray-300 uppercase tracking-wider">Email</th>
                <th class="py-3 px-6 text-center text-xs font-medium text-gray-300 uppercase tracking-wider">Ações</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-gray-700 text-gray-200">
            {% for cliente in clientes %}
            <tr>
                <td class="py-4 px-6 whitespace-nowrap">{{ cliente.nome_completo }}</td>
                <td class="py-4 px-6 whitespace-nowrap">{{ cliente.cpf_cnpj }}</td>
                <td class="py-4 px-6 whitespace-nowrap">{{ cliente.telefone }}</td>
                <td class="py-4 px-6 whitespace-nowrap">{{ cliente.email }}</td>
                <td class="py-4 px-6 text-center whitespace-nowrap space-x-3">
                    
                    {# LINKS CORRIGIDOS #}
                    <a href="{% url 'financeiro:cliente_update' pk=cliente.pk %}" class="text-indigo-400 hover:text-indigo-300 font-semibold">Editar</a>
                    <a href="{% url 'financeiro:relatorio_cliente_html' pk=cliente.pk %}" class="text-green-400 hover:text-green-300 font-semibold">Extrato</a>

                </td>
            </tr>
            {% empty %}
            <tr>
                <td colspan="5" class="py-6 px-6 text-center text-gray-400">Nenhum cliente cadastrado.</td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>
{% endblock %}