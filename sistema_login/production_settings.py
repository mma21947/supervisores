"""
Configurações para o ambiente de produção
Este arquivo deve ser colocado no servidor de produção
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env
load_dotenv()

# Caminho base do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Configurações básicas
DEBUG = False
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-hgj(*a#9g7lvc_3kecs^#re4wu&v9-c_w6mb6dy-i5p7&=%@m7')
ALLOWED_HOSTS = ['192.168.8.193']

# Configuração do banco de dados PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'sistema_faltas',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Configuração de arquivos estáticos
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Configuração de arquivos de mídia
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Idioma e fuso horário
LANGUAGE_CODE = 'pt-br'
TIME_ZONE = 'America/Sao_Paulo'

# Configurações de segurança
SECURE_SSL_REDIRECT = False  # Altere para True se estiver usando HTTPS
SESSION_COOKIE_SECURE = False  # Altere para True se estiver usando HTTPS
CSRF_COOKIE_SECURE = False  # Altere para True se estiver usando HTTPS
SECURE_BROWSER_XSS_FILTER = True

# Configurações de log
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(BASE_DIR, 'django_error.log'),
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
} 