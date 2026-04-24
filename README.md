# Sistema de Controle de Chaves

Sistema web para controle de retirada e devolução de chaves, desenvolvido com Python (Flask) e MySQL.

## Funcionalidades

- Check-in e check-out de chaves por NIP (militares) ou CPF (civis)
- Busca automática de pessoa ao digitar NIP/CPF
- Painel com resumo em tempo real
- Relatório de movimentações com filtros por data e chave
- Logs de auditoria de todas as ações do sistema
- Controle de usuários com perfis (admin / operador)

## Tecnologias

- Python 3.11+
- Flask 3.0
- MySQL 8.0
- Bootstrap 5

## Instalação

### 1. Clone o repositório
```bash
git clone https://github.com/seu-usuario/sistema-chaves.git
cd sistema-chaves
```

### 2. Crie e ative o ambiente virtual
```bash
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure o banco de dados
```bash
mysql -u root -p < database/schema.sql
```

### 5. Configure as variáveis de ambiente (opcional)
```bash
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=sua_senha
export DB_NAME=sistema_chaves
export SECRET_KEY=sua-chave-secreta
```

Ou edite diretamente o arquivo `config.py`.

### 6. Crie o usuário admin
```bash
python database/seed.py
```

### 7. Execute o sistema
```bash
python app.py
```

## Estrutura do projeto

```
sistema_chaves/
├── app.py                  # Aplicação Flask e rotas
├── config.py               # Configurações
├── requirements.txt
├── database/
│   ├── schema.sql          # Criação das tabelas
│   └── seed.py             # Dados iniciais
├── services/
│   ├── db.py               # Conexão com MySQL
│   ├── auth_service.py     # Autenticação
│   ├── chave_service.py    # Lógica de chaves
│   ├── pessoa_service.py   # Lógica de pessoas
│   └── relatorio_service.py# Relatórios e logs
└── templates/
    ├── base.html
    ├── login.html
    ├── dashboard.html
    ├── checkin.html
    ├── checkout.html
    ├── chaves.html
    ├── pessoas.html
    ├── relatorios.html
    ├── relatorio_em_uso.html
    ├── logs.html
    └── usuarios.html
```
