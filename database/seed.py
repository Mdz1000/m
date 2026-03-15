"""
Execute este script UMA VEZ para criar o usuário admin inicial.
Uso: python database/seed.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from werkzeug.security import generate_password_hash
import mysql.connector
from config import DB_CONFIG

conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

senha = generate_password_hash('admin123')
cursor.execute(
    "UPDATE usuarios SET senha_hash = %s WHERE login = 'admin'",
    (senha,)
)
conn.commit()
cursor.close()
conn.close()

print("Usuário admin criado com senha: admin123")
print("Troque a senha após o primeiro login!")
