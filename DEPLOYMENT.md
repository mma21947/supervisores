# Guia de Implantação em Servidor Ubuntu

Este guia fornece instruções passo a passo para configurar o Sistema de Gestão de Faltas e Licenças em um servidor Ubuntu com Nginx, Gunicorn e PostgreSQL.

## Requisitos do Servidor

- Ubuntu 20.04 LTS ou superior
- Python 3.8+
- PostgreSQL 12+
- Nginx
- Gunicorn
- Supervisor (para gerenciamento de processos)

## 1. Configuração Inicial do Servidor

### Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Instalar Dependências

```bash
sudo apt install -y python3-pip python3-dev libpq-dev postgresql postgresql-contrib nginx supervisor git
sudo pip3 install virtualenv
```

## 2. Configuração do PostgreSQL

### Criar Banco de Dados e Usuário

```bash
sudo -u postgres psql
```

No shell do PostgreSQL:
```sql
CREATE DATABASE sistema_faltas;
CREATE USER sistema_faltas_user WITH PASSWORD 'senha_segura';
ALTER ROLE sistema_faltas_user SET client_encoding TO 'utf8';
ALTER ROLE sistema_faltas_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sistema_faltas_user SET timezone TO 'America/Sao_Paulo';
GRANT ALL PRIVILEGES ON DATABASE sistema_faltas TO sistema_faltas_user;
\q
```

## 3. Configuração do Projeto

### Clonar o Repositório

```bash
cd /var/www/
sudo git clone https://github.com/seu-usuario/sistema-gestao-faltas.git
sudo chown -R $USER:$USER /var/www/sistema-gestao-faltas
cd sistema-gestao-faltas
```

### Configurar Ambiente Virtual

```bash
virtualenv env
source env/bin/activate
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

### Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
touch .env
nano .env
```

Adicione as seguintes variáveis:

```
DEBUG=False
SECRET_KEY=sua_chave_secreta_muito_segura
ALLOWED_HOSTS=seu_dominio.com,www.seu_dominio.com,IP_DO_SERVIDOR
DB_NAME=sistema_faltas
DB_USER=sistema_faltas_user
DB_PASSWORD=senha_segura
DB_HOST=localhost
DB_PORT=5432
```

### Configuração do Django para Produção

Crie um arquivo para configurações locais:

```bash
nano sistema_login/local_settings.py
```

Adicione o seguinte conteúdo:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações básicas
DEBUG = os.getenv('DEBUG', 'False') == 'True'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Configuração do banco de dados PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST', 'localhost'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Configuração de arquivos estáticos
STATIC_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'staticfiles')
STATIC_URL = '/static/'

# Configuração de arquivos de mídia
MEDIA_ROOT = os.path.join(Path(__file__).resolve().parent.parent, 'media')
MEDIA_URL = '/media/'

# Configurações de segurança
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
```

### Migrar e Preparar o Banco de Dados

```bash
python manage.py migrate
python manage.py collectstatic
python manage.py createsuperuser
```

## 4. Configuração do Gunicorn

### Criar arquivo para serviço Gunicorn

```bash
nano /etc/supervisor/conf.d/sistema-faltas.conf
```

Adicione o seguinte conteúdo:

```ini
[program:sistema-faltas]
directory=/var/www/sistema-gestao-faltas
command=/var/www/sistema-gestao-faltas/env/bin/gunicorn --workers 3 --bind unix:/var/www/sistema-gestao-faltas/sistema_faltas.sock sistema_login.wsgi:application
autostart=true
autorestart=true
stderr_logfile=/var/log/sistema-faltas/gunicorn.err.log
stdout_logfile=/var/log/sistema-faltas/gunicorn.out.log
user=www-data
group=www-data
environment=LANG=en_US.UTF-8,LC_ALL=en_US.UTF-8

[group:sistema-faltas]
programs=sistema-faltas
```

Crie o diretório para logs:

```bash
sudo mkdir -p /var/log/sistema-faltas
sudo touch /var/log/sistema-faltas/gunicorn.err.log
sudo touch /var/log/sistema-faltas/gunicorn.out.log
```

### Iniciar o serviço

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start sistema-faltas:*
```

## 5. Configuração do Nginx

### Criar arquivo de configuração para o site

```bash
sudo nano /etc/nginx/sites-available/sistema-faltas
```

Adicione o seguinte conteúdo:

```nginx
server {
    listen 80;
    server_name seu_dominio.com www.seu_dominio.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/sistema-gestao-faltas;
    }

    location /media/ {
        root /var/www/sistema-gestao-faltas;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/sistema-gestao-faltas/sistema_faltas.sock;
    }
}
```

### Ativar o site e testar a configuração do Nginx

```bash
sudo ln -s /etc/nginx/sites-available/sistema-faltas /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

### Configurar Firewall (opcional)

```bash
sudo ufw allow 'Nginx Full'
```

## 6. Configuração SSL com Let's Encrypt (opcional, mas recomendado)

### Instalar o Certbot

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obter certificado SSL

```bash
sudo certbot --nginx -d seu_dominio.com -d www.seu_dominio.com
```

### Renovação automática

O Certbot já configura a renovação automática. Verifique com:

```bash
sudo certbot renew --dry-run
```

## 7. Manutenção e Monitoramento

### Verificar status do serviço

```bash
sudo supervisorctl status sistema-faltas
```

### Reiniciar o serviço após atualizações

```bash
cd /var/www/sistema-gestao-faltas
git pull
source env/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo supervisorctl restart sistema-faltas:*
sudo systemctl restart nginx
```

### Acessar logs

```bash
# Logs do Gunicorn
sudo tail -f /var/log/sistema-faltas/gunicorn.out.log
sudo tail -f /var/log/sistema-faltas/gunicorn.err.log

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Resolução de Problemas

Se encontrar problemas durante a implantação, verifique:

1. Logs do Gunicorn e Nginx
2. Permissões de arquivos e diretórios
3. Status do serviço Supervisor
4. Configurações de firewall
5. Configurações do Django em local_settings.py 