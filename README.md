# Sistema de Gestão de Faltas e Licenças

Sistema para gerenciamento de funcionários, controle de faltas, licenças e horas trabalhadas.

## Funcionalidades

- Cadastro e gerenciamento de usuários e funcionários
- Registro de faltas (justificadas, não justificadas e licenças)
- Dashboard administrativo com estatísticas
- Controle de acesso baseado em permissões
- Gestão de funcionários por empresa

## Tecnologias Utilizadas

- Django 4.2
- Bootstrap 5
- SQLite (Desenvolvimento)
- PostgreSQL (Produção)

## Requisitos

- Python 3.8+
- Django 4.2+
- Pacotes listados em requirements.txt

## Instalação e Configuração

### Configuração para Desenvolvimento

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/sistema-gestao-faltas.git
   cd sistema-gestao-faltas
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv env
   # No Windows
   env\Scripts\activate
   # No Linux/Mac
   source env/bin/activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure o banco de dados:
   ```bash
   python manage.py migrate
   ```

5. Crie um superusuário:
   ```bash
   python manage.py createsuperuser
   ```

6. Execute o servidor de desenvolvimento:
   ```bash
   python manage.py runserver
   ```

### Configuração para Produção

Siga as instruções no arquivo [DEPLOYMENT.md](DEPLOYMENT.md) para configurar o sistema em um servidor de produção.

## Estrutura do Projeto

- `sistema_login/`: Configurações principais do projeto
- `usuarios/`: App para gerenciamento de usuários e funcionários
- `static/`: Arquivos estáticos (CSS, JS, imagens)
- `media/`: Arquivos de mídia enviados pelos usuários
- `templates/`: Templates HTML

## Licença

Este projeto está licenciado sob a licença MIT - consulte o arquivo [LICENSE](LICENSE) para obter detalhes. 