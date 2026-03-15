from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from functools import wraps
from config import SECRET_KEY, DEBUG
import services.auth_service as auth
import services.chave_service as chave_svc
import services.pessoa_service as pessoa_svc
import services.relatorio_service as rel_svc

app = Flask(__name__)
app.secret_key = SECRET_KEY


# ── Decoradores ────────────────────────────────────────────────────

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'usuario_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get('perfil') != 'admin':
            flash('Acesso restrito a administradores.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return login_required(decorated)


def ip_atual():
    return request.headers.get('X-Forwarded-For', request.remote_addr)


# ── Autenticação ───────────────────────────────────────────────────

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'usuario_id' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        usuario = auth.autenticar(request.form['login'], request.form['senha'])
        if usuario:
            session['usuario_id'] = usuario['id']
            session['usuario_nome'] = usuario['nome']
            session['perfil'] = usuario['perfil']
            rel_svc.registrar_log(usuario['id'], 'login', ip_atual())
            return redirect(url_for('dashboard'))
        flash('Login ou senha inválidos.', 'danger')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    rel_svc.registrar_log(session['usuario_id'], 'logout', ip_atual())
    session.clear()
    return redirect(url_for('login'))


# ── Dashboard ──────────────────────────────────────────────────────

@app.route('/dashboard')
@login_required
def dashboard():
    resumo = rel_svc.resumo_dashboard()
    chaves_em_uso = rel_svc.relatorio_chaves_em_uso()
    return render_template('dashboard.html', resumo=resumo, chaves_em_uso=chaves_em_uso)


# ── Chaves ─────────────────────────────────────────────────────────

@app.route('/chaves')
@login_required
def listar_chaves():
    chaves = chave_svc.listar()
    return render_template('chaves.html', chaves=chaves)


@app.route('/chaves/nova', methods=['GET', 'POST'])
@admin_required
def nova_chave():
    if request.method == 'POST':
        chave_svc.criar(
            request.form['andar'],
            request.form['numero'],
            request.form.get('descricao')
        )
        rel_svc.registrar_log(session['usuario_id'], 'nova_chave', ip_atual(),
                              f"Andar {request.form['andar']} nº {request.form['numero']}")
        flash('Chave cadastrada com sucesso.', 'success')
        return redirect(url_for('listar_chaves'))
    return render_template('chave_form.html')


# ── Check-in / Check-out ───────────────────────────────────────────

@app.route('/checkin', methods=['GET', 'POST'])
@login_required
def checkin():
    if request.method == 'POST':
        identificador = request.form.get('identificador', '').strip()
        chave_id = request.form.get('chave_id')
        observacao = request.form.get('observacao')

        pessoa = pessoa_svc.buscar_por_nip_ou_cpf(identificador)
        if not pessoa:
            flash('Pessoa não encontrada. Verifique o NIP ou CPF.', 'danger')
            return redirect(url_for('checkin'))

        try:
            chave_svc.checkin(chave_id, pessoa['id'], session['usuario_id'], observacao)
            rel_svc.registrar_log(session['usuario_id'], 'checkin', ip_atual(),
                                  f"Chave {chave_id} → {pessoa['nome']}")
            flash(f"Check-in registrado para {pessoa['nome']}.", 'success')
        except ValueError as e:
            flash(str(e), 'danger')

        return redirect(url_for('checkin'))

    chaves_disponiveis = [c for c in chave_svc.listar() if c['status'] == 'disponivel']
    return render_template('checkin.html', chaves=chaves_disponiveis)


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    if request.method == 'POST':
        chave_id = request.form.get('chave_id')
        observacao = request.form.get('observacao')

        try:
            chave_svc.checkout(chave_id, session['usuario_id'], observacao)
            rel_svc.registrar_log(session['usuario_id'], 'checkout', ip_atual(),
                                  f"Chave {chave_id} devolvida")
            flash('Check-out registrado com sucesso.', 'success')
        except ValueError as e:
            flash(str(e), 'danger')

        return redirect(url_for('checkout'))

    chaves_retiradas = [c for c in chave_svc.listar() if c['status'] == 'retirada']
    return render_template('checkout.html', chaves=chaves_retiradas)


# ── Pessoas ────────────────────────────────────────────────────────

@app.route('/pessoas')
@login_required
def listar_pessoas():
    pessoas = pessoa_svc.listar()
    return render_template('pessoas.html', pessoas=pessoas)


@app.route('/pessoas/nova', methods=['GET', 'POST'])
@login_required
def nova_pessoa():
    if request.method == 'POST':
        tipo = request.form['tipo']
        pessoa_svc.criar(
            nome=request.form['nome'],
            tipo=tipo,
            quartel=request.form.get('quartel'),
            nip=request.form.get('nip') if tipo == 'militar' else None,
            cpf=request.form.get('cpf') if tipo == 'civil' else None,
        )
        rel_svc.registrar_log(session['usuario_id'], 'nova_pessoa', ip_atual(),
                              request.form['nome'])
        flash('Pessoa cadastrada com sucesso.', 'success')
        return redirect(url_for('listar_pessoas'))
    return render_template('pessoa_form.html')


# ── API: busca rápida por NIP/CPF (usada no checkin via JS) ────────

@app.route('/api/buscar_pessoa')
@login_required
def api_buscar_pessoa():
    valor = request.args.get('q', '').strip()
    if not valor:
        return jsonify(None)
    pessoa = pessoa_svc.buscar_por_nip_ou_cpf(valor)
    if pessoa:
        return jsonify({'id': pessoa['id'], 'nome': pessoa['nome'],
                        'tipo': pessoa['tipo'], 'quartel': pessoa['quartel']})
    return jsonify(None)


# ── Relatórios ─────────────────────────────────────────────────────

@app.route('/relatorios')
@login_required
def relatorios():
    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    chave_id = request.args.get('chave_id')

    movimentacoes = rel_svc.relatorio_movimentacoes(data_inicio, data_fim, chave_id)
    chaves = chave_svc.listar()
    return render_template('relatorios.html',
                           movimentacoes=movimentacoes,
                           chaves=chaves,
                           filtros={'data_inicio': data_inicio,
                                    'data_fim': data_fim,
                                    'chave_id': chave_id})


@app.route('/relatorios/em_uso')
@login_required
def relatorio_em_uso():
    chaves = rel_svc.relatorio_chaves_em_uso()
    return render_template('relatorio_em_uso.html', chaves=chaves)


# ── Logs ───────────────────────────────────────────────────────────

@app.route('/logs')
@admin_required
def logs():
    registros = rel_svc.listar_logs()
    return render_template('logs.html', registros=registros)


# ── Usuários (admin) ───────────────────────────────────────────────

@app.route('/usuarios')
@admin_required
def listar_usuarios():
    usuarios = auth.listar_usuarios()
    return render_template('usuarios.html', usuarios=usuarios)


@app.route('/usuarios/novo', methods=['GET', 'POST'])
@admin_required
def novo_usuario():
    if request.method == 'POST':
        auth.criar_usuario(
            request.form['login'],
            request.form['senha'],
            request.form['nome'],
            request.form['perfil']
        )
        rel_svc.registrar_log(session['usuario_id'], 'novo_usuario', ip_atual(),
                              request.form['login'])
        flash('Usuário criado com sucesso.', 'success')
        return redirect(url_for('listar_usuarios'))
    return render_template('usuario_form.html')


if __name__ == '__main__':
    app.run(debug=DEBUG, host='0.0.0.0', port=5000)
