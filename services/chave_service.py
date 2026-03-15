from services.db import query, execute


def listar():
    return query("""
        SELECT c.*, m.data_hora AS retirada_em, p.nome AS retirada_por
        FROM chaves c
        LEFT JOIN movimentacoes m ON m.chave_id = c.id AND m.tipo = 'checkin'
            AND m.id = (
                SELECT MAX(id) FROM movimentacoes
                WHERE chave_id = c.id AND tipo = 'checkin'
            )
        LEFT JOIN pessoas p ON p.id = m.pessoa_id
        ORDER BY c.andar, c.numero
    """)


def buscar_por_id(chave_id):
    return query("SELECT * FROM chaves WHERE id = %s", (chave_id,), fetchone=True)


def criar(andar, numero, descricao=None):
    return execute(
        "INSERT INTO chaves (andar, numero, descricao) VALUES (%s, %s, %s)",
        (andar, numero, descricao)
    )


def checkin(chave_id, pessoa_id, operador_id, observacao=None):
    chave = buscar_por_id(chave_id)
    if not chave:
        raise ValueError("Chave não encontrada.")
    if chave['status'] == 'retirada':
        raise ValueError("Chave já está retirada.")
    execute(
        "INSERT INTO movimentacoes (chave_id, pessoa_id, tipo, operador_id, observacao) VALUES (%s, %s, 'checkin', %s, %s)",
        (chave_id, pessoa_id, operador_id, observacao)
    )
    execute("UPDATE chaves SET status = 'retirada' WHERE id = %s", (chave_id,))


def checkout(chave_id, operador_id, observacao=None):
    chave = buscar_por_id(chave_id)
    if not chave:
        raise ValueError("Chave não encontrada.")
    if chave['status'] == 'disponivel':
        raise ValueError("Chave já está disponível.")
    ultima_mov = query("""
        SELECT pessoa_id FROM movimentacoes
        WHERE chave_id = %s AND tipo = 'checkin'
        ORDER BY id DESC LIMIT 1
    """, (chave_id,), fetchone=True)
    pessoa_id = ultima_mov['pessoa_id'] if ultima_mov else None
    execute(
        "INSERT INTO movimentacoes (chave_id, pessoa_id, tipo, operador_id, observacao) VALUES (%s, %s, 'checkout', %s, %s)",
        (chave_id, pessoa_id, operador_id, observacao)
    )
    execute("UPDATE chaves SET status = 'disponivel' WHERE id = %s", (chave_id,))
