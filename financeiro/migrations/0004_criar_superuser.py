# Dentro do seu novo arquivo de migração (ex: 0004_criar_superuser.py)

from django.db import migrations
from django.contrib.auth import get_user_model

def criar_superuser(apps, schema_editor):
    """
    Cria um superusuário de forma não-interativa.
    """
    User = get_user_model()
    
    # NÃO use senhas simples em produção real. Troque esta senha após o primeiro login.
    username = 'luciano'
    email = 'lucianomezencio@gmail.com'
    password = '88171741'

    # Verifica se o usuário já não existe
    if not User.objects.filter(username=username).exists():
        print(f"Criando superusuário: {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print(f"Superusuário '{username}' já existe. Nenhuma ação necessária.")


class Migration(migrations.Migration):

    dependencies = [
        ('financeiro', '0003_alter_parcela_options_cliente_ativo'), # Verifique se este é o nome da sua última migração
    ]

    operations = [
        migrations.RunPython(criar_superuser),
    ]