# Guia de Implantação em Servidor Ubuntu

Este guia fornece instruções passo a passo para configurar o Sistema de Gestão de Faltas e Licenças em um servidor Ubuntu com IP 192.168.8.193, usando PostgreSQL e Gunicorn.

## 1. Configuração Inicial do Servidor

### Atualizar o Sistema

```bash
sudo apt update
sudo apt upgrade -y
```

### Instalar Dependências

```bash
sudo apt install -y python3-pip python3-dev libpq-dev git nginx
```

## 2. Instalação e Configuração do PostgreSQL

### Instalar PostgreSQL

```bash
sudo apt install -y postgresql postgresql-contrib
```

### Verificar Status do PostgreSQL

```bash
sudo systemctl status postgresql
```

### Configurar PostgreSQL

Acesse o shell do PostgreSQL:
```bash
sudo -u postgres psql
```

No shell do PostgreSQL:
```sql
CREATE DATABASE sistema_faltas;
ALTER USER postgres PASSWORD 'postgres';
\q
```

### Editar Configuração de Autenticação do PostgreSQL

```bash
sudo nano /etc/postgresql/[versao]/main/pg_hba.conf
```

Localize a linha que contém `local all postgres` e altere o método de autenticação para `md5`:
```
local   all             postgres                                md5
```

Reinicie o PostgreSQL:
```bash
sudo systemctl restart postgresql
```

## 3. Configuração do Projeto

### Clonar o Repositório

```bash
cd /var/www/
sudo mkdir sistema-faltas
sudo chown -R $USER:$USER /var/www/sistema-faltas
git clone https://github.com/mma21947/supervisores.git /var/www/sistema-faltas
cd /var/www/sistema-faltas
```

### Configurar Ambiente Virtual

```bash
sudo apt install -y python3-venv
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
cp .env.example .env
nano .env
```

Edite o arquivo com as seguintes configurações:

```
DEBUG=False
SECRET_KEY=sua_chave_secreta_muito_segura
ALLOWED_HOSTS=192.168.8.193

DB_ENGINE=django.db.backends.postgresql_psycopg2
DB_NAME=sistema_faltas
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

LANGUAGE_CODE=pt-br
TIME_ZONE=America/Sao_Paulo
```

### Usar Configuração de Produção

Copie o arquivo de configuração de produção:

```bash
cp sistema_login/production_settings.py sistema_login/local_settings.py
```

### Migrar e Preparar o Banco de Dados

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## 4. Configuração do Gunicorn

### Criar Arquivo de Serviço para o Systemd

```bash
sudo nano /etc/systemd/system/sistema-faltas.service
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=Sistema Faltas Gunicorn Daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/sistema-faltas
ExecStart=/var/www/sistema-faltas/env/bin/gunicorn --workers 3 --bind 0.0.0.0:8000 sistema_login.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### Configurar Permissões

```bash
sudo chown -R www-data:www-data /var/www/sistema-faltas
sudo chmod -R 775 /var/www/sistema-faltas/media
sudo chmod -R 775 /var/www/sistema-faltas/staticfiles
```

### Iniciar e Habilitar o Serviço

```bash
sudo systemctl start sistema-faltas
sudo systemctl enable sistema-faltas
sudo systemctl status sistema-faltas
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
    server_name 192.168.8.193;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/sistema-faltas/staticfiles/;
    }

    location /media/ {
        alias /var/www/sistema-faltas/media/;
    }

    location / {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://0.0.0.0:8000;
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
sudo ufw allow OpenSSH
sudo ufw enable
```

## 6. Verificação e Solução de Problemas

### Verificar Status dos Serviços

```bash
sudo systemctl status postgresql
sudo systemctl status sistema-faltas
sudo systemctl status nginx
```

### Verificar Logs do Sistema

```bash
# Logs do Gunicorn
sudo journalctl -u sistema-faltas

# Logs do Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# Logs do Django
sudo tail -f /var/www/sistema-faltas/django_error.log
```

### Problemas Comuns e Soluções

#### Problema de Permissão

Se encontrar problemas de permissão:

```bash
sudo chown -R www-data:www-data /var/www/sistema-faltas
sudo chmod -R 775 /var/www/sistema-faltas/media
sudo chmod -R 775 /var/www/sistema-faltas/staticfiles
```

#### Problema com o PostgreSQL

Se não conseguir conectar ao PostgreSQL:

1. Verifique se o serviço está rodando:
   ```bash
   sudo systemctl status postgresql
   ```

2. Verifique a configuração de autenticação:
   ```bash
   sudo nano /etc/postgresql/[versao]/main/pg_hba.conf
   ```

3. Reinicie o PostgreSQL:
   ```bash
   sudo systemctl restart postgresql
   ```

#### Problema com o Gunicorn

Se o Gunicorn não iniciar:

1. Verifique os logs:
   ```bash
   sudo journalctl -u sistema-faltas
   ```

2. Verifique manualmente se o Gunicorn funciona:
   ```bash
   cd /var/www/sistema-faltas
   source env/bin/activate
   gunicorn --bind 0.0.0.0:8000 sistema_login.wsgi:application
   ``` 