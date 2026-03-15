from werkzeug.security import check_password_hash, generate_password_hash
from services.db import query, execute


def autenticar(login, senha):
    usuario = query(
        "SELECT * FROM usuarios WHERE login = %s AND ativo = TRUE",
        (login,), fetchone=True
    )
    if usuario and check_password_hash(usuario['senha_hash'], senha):
        return usuario
    return None


def buscar_por_id(usuario_id):
    return query(
        "SELECT id, login, nome, perfil FROM usuarios WHERE id = %s",
        (usuario_id,), fetchone=True
    )


def listar_usuarios():
    return query("SELECT id, login, nome, perfil, ativo, criado_em FROM usuarios ORDER BY nome")


def criar_usuario(login, senha, nome, perfil):
    senha_hash = generate_password_hash(senha)
    return execute(
        "INSERT INTO usuarios (login, senha_hash, nome, perfil) VALUES (%s, %s, %s, %s)",
        (login, senha_hash, nome, perfil)
    )


def alterar_senha(usuario_id, nova_senha):
    execute(
        "UPDATE usuarios SET senha_hash = %s WHERE id = %s",
        (generate_password_hash(nova_senha), usuario_id)
    )
