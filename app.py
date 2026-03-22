import csv
import os  # Adicione esta importação no topo
from flask import Flask, render_template, request, redirect

app = Flask(__name__)

# ... (mantenha as outras rotas igual)

@app.route('/excluir/<nome>')
def excluir(nome):
    linhas_restantes = []
    
    # Passo 1: Ler todos, exceto o que queremos apagar
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                if linha and linha[0] != nome:
                    linhas_restantes.append(linha)
        
        # Passo 2: Sobrescrever o arquivo com a nova lista
        with open('usuarios.csv', mode='w', newline='', encoding='utf-8') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerows(linhas_restantes)
            
    except FileNotFoundError:
        pass

    return redirect('/lista')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome_novo = request.form.get('nome').strip() # .strip() remove espaços extras
    senha_nova = request.form.get('senha')

    # Passo 1: Verificar se o usuário já existe
    usuario_existe = False
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                if linha and linha[0].lower() == nome_novo.lower():
                    usuario_existe = True
                    break
    except FileNotFoundError:
        pass # Se o arquivo não existir, o usuário certamente não existe

    # Passo 2: Decidir se salva ou se avisa o erro
    if usuario_existe:
        return f"<h1>Erro!</h1><p>O usuário <b>{nome_novo}</b> já está cadastrado.</p><a href='/'>Tentar outro nome</a>"
    
    # Se não existe, salvamos normalmente
    with open('usuarios.csv', mode='a', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([nome_novo, senha_nova])

    return redirect('/lista') # Agora ele pula direto para a lista após salvar

@app.route('/lista')
def ver_lista():
    usuarios = []
    try:
        with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
            leitor = csv.reader(arquivo)
            for linha in leitor:
                # Cada 'linha' é uma lista como ['joao', '123']
                usuarios.append({"nome": linha[0], "senha": linha[1]})
    except FileNotFoundError:
        # Se o arquivo ainda não existir, a lista continua vazia
        pass

    return render_template('lista.html', lista_usuarios=usuarios)

@app.route('/editar/<nome_antigo>')
def editar_pagina(nome_antigo):
    # Procura os dados atuais desse usuário para mostrar no formulário
    usuario_atual = None
    with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            if linha and linha[0] == nome_antigo:
                usuario_atual = {"nome": linha[0], "senha": linha[1]}
                break
    return render_template('editar.html', usuario=usuario_atual)

@app.route('/atualizar', methods=['POST'])
def atualizar():
    nome_original = request.form.get('nome_original') # Nome antes da mudança
    novo_nome = request.form.get('nome').strip()
    nova_senha = request.form.get('senha')

    linhas_atualizadas = []
    with open('usuarios.csv', mode='r', encoding='utf-8') as arquivo:
        leitor = csv.reader(arquivo)
        for linha in leitor:
            if linha:
                if linha[0] == nome_original:
                    # Se for o usuário que queremos mudar, salvamos os novos dados
                    linhas_atualizadas.append([novo_nome, nova_senha])
                else:
                    # Se não for, mantemos o que já estava lá
                    linhas_atualizadas.append(linha)

    # Salva tudo de volta no arquivo
    with open('usuarios.csv', mode='w', newline='', encoding='utf-8') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerows(linhas_atualizadas)

    return redirect('/lista')

if __name__ == '__main__':
    app.run(debug=True)