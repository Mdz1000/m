from services.db import query, execute


def listar():
    return query("SELECT * FROM pessoas ORDER BY nome")


def buscar_por_id(pessoa_id):
    return query("SELECT * FROM pessoas WHERE id = %s", (pessoa_id,), fetchone=True)


def buscar_por_nip(nip):
    return query("SELECT * FROM pessoas WHERE nip = %s AND status = 'ativo'", (nip,), fetchone=True)


def buscar_por_cpf(cpf):
    cpf_limpo = cpf.replace('.', '').replace('-', '').strip()
    return query(
        "SELECT * FROM pessoas WHERE REPLACE(REPLACE(cpf, '.', ''), '-', '') = %s AND status = 'ativo'",
        (cpf_limpo,), fetchone=True
    )


def buscar_por_nip_ou_cpf(valor):
    valor = valor.strip()
    if valor.isdigit() and len(valor) <= 10:
        return buscar_por_nip(valor)
    return buscar_por_cpf(valor)


def criar(nome, tipo, quartel=None, nip=None, cpf=None):
    return execute(
        "INSERT INTO pessoas (nome, tipo, nip, cpf, quartel) VALUES (%s, %s, %s, %s, %s)",
        (nome, tipo, nip, cpf, quartel)
    )


def atualizar(pessoa_id, nome, tipo, quartel=None, nip=None, cpf=None):
    execute(
        "UPDATE pessoas SET nome=%s, tipo=%s, nip=%s, cpf=%s, quartel=%s WHERE id=%s",
        (nome, tipo, nip, cpf, quartel, pessoa_id)
    )


def desativar(pessoa_id):
    execute("UPDATE pessoas SET status = 'inativo' WHERE id = %s", (pessoa_id,))
