import csv
import os
from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
# CHAVE DE SEGURANÇA: Necessária para usar 'session'
app.secret_key = 'chave_secreta_para_desenvolvimento' 

# --- ROTA: CADASTRO (PÁGINA INICIAL) ---
@app.route('/')
def index():
    return render_template('index.html')

# --- ROTA: PROCESSAR CADASTRO ---
@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome').strip()
    senha = request.form.get('senha')
    senha_hash = generate_password_hash(senha)

    # Verifica se usuário já existe
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                if linha and linha[0].lower() == nome.lower():
                    return "<h1>Erro!</h1><p>Usuário já existe.</p><a href='/'>Voltar</a>"
    except FileNotFoundError:
        pass

    # Salva no arquivo
    with open('usuarios.csv', mode='a', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([nome, senha_hash])

    # PONTO DE ATENÇÃO 2: Login automático após cadastrar
    session['usuario_logado'] = nome
    return redirect(url_for('ver_lista'))

# --- ROTA: LOGIN (PÁGINA) ---
@app.route('/login')
def login_pagina():
    return render_template('login.html')

# --- ROTA: PROCESSAR LOGIN ---
@app.route('/logar', methods=['POST'])
def logar():
    nome_digitado = request.form.get('nome').strip()
    senha_digitada = request.form.get('senha')

    usuario_encontrado = None
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                if linha and linha[0].lower() == nome_digitado.lower():
                    usuario_encontrado = {"nome": linha[0], "hash": linha[1]}
                    break
    except FileNotFoundError:
        return "<h1>Erro!</h1><p>Nenhum usuário no sistema.</p>"

    # Verifica senha com check_password_hash
    if usuario_encontrado and check_password_hash(usuario_encontrado['hash'], senha_digitada):
        session['usuario_logado'] = usuario_encontrado['nome']
        return redirect(url_for('ver_lista'))
    else:
        return "<h1>Erro!</h1><p>Senha ou usuário incorretos.</p><a href='/login'>Tentar de novo</a>"

# --- ROTA: LISTAGEM (PROTEGIDA) ---
@app.route('/lista')
def ver_lista():
    # PONTO DE ATENÇÃO 1: Trava de segurança
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    usuarios = []
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                if linha:
                    usuarios.append({"nome": linha[0], "senha": linha[1]})
    except FileNotFoundError:
        pass
    return render_template('lista.html', lista_usuarios=usuarios)

# --- ROTA: EDITAR (PROTEGIDA) ---
@app.route('/editar/<nome_antigo>')
def editar_pagina(nome_antigo):
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    usuario_atual = None
    with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            if linha and linha[0] == nome_antigo:
                usuario_atual = {"nome": linha[0], "senha": linha[1]}
                break
    return render_template('editar.html', usuario=usuario_atual)

# --- ROTA: ATUALIZAR (PROTEGIDA) ---
@app.route('/atualizar', methods=['POST'])
def atualizar():
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    nome_original = request.form.get('nome_original')
    novo_nome = request.form.get('nome').strip()
    nova_senha_hash = generate_password_hash(request.form.get('senha'))

    linhas = []
    with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            if linha:
                if linha[0] == nome_original:
                    linhas.append([novo_nome, nova_senha_hash])
                else:
                    linhas.append(linha)

    with open('usuarios.csv', mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(linhas)
    return redirect(url_for('ver_lista'))

# --- ROTA: EXCLUIR (PROTEGIDA) ---
@app.route('/excluir/<nome>')
def excluir(nome):
    if 'usuario_logado' not in session:
        return redirect(url_for('login_pagina'))

    linhas = []
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                if linha and linha[0] != nome:
                    linhas.append(linha)
        
        with open('usuarios.csv', mode='w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerows(linhas)
    except FileNotFoundError:
        pass
    return redirect(url_for('ver_lista'))

# --- ROTA: LOGOUT ---
@app.route('/logout')
def logout():
    session.pop('usuario_logado', None)
    return redirect(url_for('login_pagina'))

if __name__ == '__main__':
    app.run(debug=True)