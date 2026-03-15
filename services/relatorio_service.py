from services.db import query, execute


# ── Logs de auditoria ──────────────────────────────────────────────

def registrar_log(usuario_id, acao, ip=None, detalhes=None):
    execute(
        "INSERT INTO logs (usuario_id, acao, ip, detalhes) VALUES (%s, %s, %s, %s)",
        (usuario_id, acao, ip, detalhes)
    )


def listar_logs(limite=200):
    return query("""
        SELECT l.*, u.nome AS usuario_nome
        FROM logs l
        LEFT JOIN usuarios u ON u.id = l.usuario_id
        ORDER BY l.data_hora DESC
        LIMIT %s
    """, (limite,))


# ── Relatórios ─────────────────────────────────────────────────────

def relatorio_movimentacoes(data_inicio=None, data_fim=None, chave_id=None):
    filtros = []
    params = []

    if data_inicio:
        filtros.append("m.data_hora >= %s")
        params.append(data_inicio)
    if data_fim:
        filtros.append("m.data_hora <= %s")
        params.append(data_fim + " 23:59:59")
    if chave_id:
        filtros.append("m.chave_id = %s")
        params.append(chave_id)

    where = ("WHERE " + " AND ".join(filtros)) if filtros else ""

    return query(f"""
        SELECT
            m.id,
            m.tipo,
            m.data_hora,
            m.observacao,
            c.andar,
            c.numero,
            p.nome AS pessoa_nome,
            p.tipo AS pessoa_tipo,
            p.nip,
            p.cpf,
            u.nome AS operador_nome
        FROM movimentacoes m
        JOIN chaves c ON c.id = m.chave_id
        JOIN pessoas p ON p.id = m.pessoa_id
        JOIN usuarios u ON u.id = m.operador_id
        {where}
        ORDER BY m.data_hora DESC
    """, params)


def relatorio_chaves_em_uso():
    return query("""
        SELECT
            c.andar,
            c.numero,
            c.descricao,
            p.nome AS retirada_por,
            p.tipo AS tipo_pessoa,
            p.nip,
            p.cpf,
            m.data_hora AS retirada_em
        FROM chaves c
        JOIN movimentacoes m ON m.chave_id = c.id AND m.tipo = 'checkin'
            AND m.id = (
                SELECT MAX(id) FROM movimentacoes
                WHERE chave_id = c.id AND tipo = 'checkin'
            )
        JOIN pessoas p ON p.id = m.pessoa_id
        WHERE c.status = 'retirada'
        ORDER BY m.data_hora ASC
    """)


def resumo_dashboard():
    total_chaves   = query("SELECT COUNT(*) AS total FROM chaves", fetchone=True)['total']
    retiradas      = query("SELECT COUNT(*) AS total FROM chaves WHERE status = 'retirada'", fetchone=True)['total']
    total_pessoas  = query("SELECT COUNT(*) AS total FROM pessoas WHERE status = 'ativo'", fetchone=True)['total']
    mov_hoje       = query("""
        SELECT COUNT(*) AS total FROM movimentacoes
        WHERE DATE(data_hora) = CURDATE()
    """, fetchone=True)['total']

    return {
        'total_chaves':  total_chaves,
        'disponiveis':   total_chaves - retiradas,
        'retiradas':     retiradas,
        'total_pessoas': total_pessoas,
        'mov_hoje':      mov_hoje,
    }
