import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'chave_mestra_sqlite'

# --- FUNÇÃO PARA CONECTAR AO BANCO ---
def ligar_banco():
    # row_factory faz o sqlite retornar os dados como dicionários (mais fácil de usar)
    conn = sqlite3.connect('usuarios.db')
    conn.row_factory = sqlite3.Row
    return conn

# --- INICIALIZAÇÃO DO BANCO (CRIA A TABELA) ---
def init_db():
    conn = ligar_banco()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- ROTA: CADASTRO ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome').strip()
    senha_hash = generate_password_hash(request.form.get('senha'))

    try:
        conn = ligar_banco()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO usuarios (nome, senha) VALUES (?, ?)', (nome, senha_hash))
        conn.commit()
        conn.close()
        session['usuario_logado'] = nome
        return redirect(url_for('ver_lista'))
    except sqlite3.IntegrityError:
        return "<h1>Erro!</h1><p>Usuário já existe.</p><a href='/'>Voltar</a>"

# --- ROTA: LOGIN ---
@app.route('/login')
def login_pagina():
    return render_template('login.html')

@app.route('/logar', methods=['POST'])
def logar():
    nome_digitado = request.form.get('nome').strip()
    senha_digitada = request.form.get('senha')

    conn = ligar_banco()
    cursor = conn.cursor()
    # Busca o usuário pelo nome
    usuario = cursor.execute('SELECT * FROM usuarios WHERE nome = ?', (nome_digitado,)).fetchone()
    conn.close()

    if usuario and check_password_hash(usuario['senha'], senha_digitada):
        session['usuario_logado'] = usuario['nome']
        return redirect(url_for('ver_lista'))
    else:
        return "<h1>Erro!</h1><p>Login incorreto.</p><a href='/login'>Tentar de novo</a>"

# --- ROTA: LISTAGEM (READ) ---
@app.route('/lista')
def ver_lista():
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    conn = ligar_banco()
    # Pega todos os usuários da tabela
    usuarios = conn.execute('SELECT * FROM usuarios').fetchall()
    conn.close()
    return render_template('lista.html', lista_usuarios=usuarios)

# --- ROTA: EDITAR (UPDATE) ---
@app.route('/editar/<nome_antigo>')
def editar_pagina(nome_antigo):
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    conn = ligar_banco()
    usuario = conn.execute('SELECT * FROM usuarios WHERE nome = ?', (nome_antigo,)).fetchone()
    conn.close()
    return render_template('editar.html', usuario=usuario)

@app.route('/atualizar', methods=['POST'])
def atualizar():
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    nome_original = request.form.get('nome_original')
    novo_nome = request.form.get('nome').strip()
    nova_senha_hash = generate_password_hash(request.form.get('senha'))

    conn = ligar_banco()
    conn.execute('UPDATE usuarios SET nome = ?, senha = ? WHERE nome = ?', (novo_nome, nova_senha_hash, nome_original))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_lista'))

# --- ROTA: EXCLUIR (DELETE) ---
@app.route('/excluir/<nome>')
def excluir(nome):
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    conn = ligar_banco()
    conn.execute('DELETE FROM usuarios WHERE nome = ?', (nome,))
    conn.commit()
    conn.close()
    return redirect(url_for('ver_lista'))

# --- ROTA: LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('login_pagina'))

if __name__ == '__main__':
    app.run(debug=True)