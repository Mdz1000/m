import os

DB_CONFIG = {
    'host':     os.getenv('DB_HOST', 'localhost'),
    'user':     os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'admin123'),
    'database': os.getenv('DB_NAME', 'sistema_chaves'),
    'charset':  'utf8mb4',
}

SECRET_KEY = os.getenv('SECRET_KEY', 'troque-esta-chave-em-producao')
DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
