from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mariadb
import sys
from flask_cors import CORS

#render template: passando o nome do modelo e a variáveis ele vai renderizar o template
#request: faz as requisições da nosa aplicação
#redirect: redireciona pra outras páginas
#session: armazena informações do usuário
#flash:mensagem de alerta exibida na tela
#url_for: vai para aonde o redirect indica
app = Flask(__name__)
CORS(app)
# Instantiate Connection
try:
    conn = mariadb.connect(
        user="kleber",
        password="1234",
        host="localhost",
        port=3306,
        database='estufa')
except mariadb.Error as e:
    print("Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

cur = conn.cursor()
app.secret_key = 'flask'

#chave secreta da sessão

class Pokemon:
    def __init__(self, nome, especie, tipo):
        self.nome = nome
        self.especie = especie
        self.tipo = tipo

class Treinadora:
    def __init__(self, id, nome, senha):
        self.id = id
        self.nome = nome
        self.senha = senha

#criação das terindoras
treinadora1 = Treinadora('Mary', 'Mary Jackson ', '1234')
treinadora2 = Treinadora('Ada', 'Ada Lovelace', '1234')
treinadora3 = Treinadora('Katherine', 'Katherine Johnson', '1234')

treinadoras = {treinadora1.id: treinadora1,
            treinadora2.id: treinadora2,
            treinadora3.id: treinadora3}

#base de dados de pokemons
pokemon1 = Pokemon('Meowth', 'Arranha Gato', 'Normal')
pokemon2 = Pokemon('Charmander', 'Lagarto', 'Fogo')


lista = [pokemon1, pokemon2]

#configuração da rota index.
@app.route('/')
def index():
    cur.execute("SELECT id_medicao, Identificacao, Temperatura, Umidade, DATE_FORMAT(Data, '(%d) %H:%i') FROM Medicao"
                    " WHERE year(Data)=year(now()) and month(Data)=month(now()) ORDER BY Data DESC LIMIT 20")
    medicoes = []
    temperaturas = []
    umidades = []
    dias = []
    for id_medicao, Identificacao, Temperatura, Umidade, Data in cur:
        medicoes.append(
           {'id': id_medicao, 'Sensor': Identificacao, 'Temperatura': float(Temperatura), 'Umidade': float(Umidade), 'Data': f"{Data}"})
        temperaturas.append(float(Temperatura))
        umidades.append(float(Umidade))
        dias.append(f"{Data}")

    return render_template('lista.html', titulo='Medições', medicoes=medicoes, temperaturas=temperaturas, umidades=umidades, dias=dias)
    #renderizando o template lista e as variáveis desejadas.


@app.route('/medicao')
def medicao():
    cur.execute("SELECT id_medicao, Identificacao, Temperatura, Umidade, Data FROM Medicao"
                " WHERE year(Data)=year(now()) and month(Data)=month(now()) ORDER BY Data DESC LIMIT 50")
    retornoBD = []
    for id_medicao, Identificacao, Temperatura, Umidade, Data in cur:
        retornoBD.append(
           {'id': id_medicao, 'Sensor': Identificacao, 'Temperatura': float(Temperatura), 'Umidade': float(Umidade), 'Data': f"{Data}"})


    return jsonify(retornoBD)


#configuração da rota novo, ela só poderá ser acessda se o usuário estiver logado, caso contrário redireciona para a tela de login
@app.route('/novo')
def novo():
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('novo.html', titulo='Novo Pokemon')
        #renderiza o template novo

#configuração da rpta criar que usa o método post para enviar dados dos nossos pokemons
@app.route('/criar', methods=['POST',])
def criar():
    nome = request. form['nome']
    especie = request. form['especie']
    tipo = request. form['tipo']
    pokemon = Pokemon(nome, especie, tipo)
    lista.append(pokemon)
    return redirect(url_for('index'))
#já inclui o novo pokemon na lista e joga na tela inicial

#configuração da rota login
@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)

#configuração da rota autenticar que verific as credenciais das terinadoras
@app.route('/autenticar', methods=['POST', ])
def autenticar():
    if request.form['treinadora'] in treinadoras:
        treinadora = treinadoras[request.form['treinadora']]
        if treinadora.senha == request.form['senha']:
            session['usuario_logado'] = treinadora.id
            flash(treinadora.nome + ' acesso permitido!')
            proxima_pagina = request.form['proxima']
            return redirect(proxima_pagina)
    else:
        #caso as credenciais não sejam validadas, exibe mensagem de erro e redirecion para o login
        flash('Acesso negado, digite novamente!')
        return redirect(url_for('login'))

#configuração da rota logout
@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Treinadora, logue novamente para cadastrar os pokemons que encontrar!')
    return redirect(url_for('index'))



# app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


# from flask_cors import CORS
# import json
#

#
# # Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
#
# from flask import Flask, jsonify, render_template
#
# app = Flask(__name__)
# CORS(app)
#
#
# @app.route('/estufa')
# def estufaHtml():
#
#     cur.execute("SELECT id_medicao, Identificacao, Temperatura, Umidade, Data FROM Medicao"
#                 " WHERE year(Data)=year(now()) and month(Data)=month(now()) LIMIT 20")
#     retornoBD = []
#     for id_medicao, Identificacao, Temperatura, Umidade, Data in cur:
#         retornoBD.append(
#            {'id': id_medicao, 'Sensor': Identificacao, 'Temperatura': float(Temperatura), 'Umidade': float(Umidade), 'Data': f"{Data}"})
#     return render_template('index.html', titulo='Estufa', medicoes=retornoBD)
#
#

#
#
# @app.route('/medicoes')
# def medicoes():
#
#     cur.execute("SELECT id_medicao, Identificacao, Temperatura, Umidade FROM Medicao")
#     retornoBD = []
#     for id_medicao, Identificacao, Temperatura, Umidade, Data in cur:
#         retornoBD.append({'id': id_medicao, 'Identificação': Identificacao, 'Temperatura': Temperatura, 'Umidade': Umidade,  'Data': Data})
#         print(f"Identificacao: {retornoBD}")
#     print(retornoBD)
#
#     return f"Identificafddcao: {retornoBD}"
#
#
#
#
# ##app.run(host='0.0.0.0', port=8080)
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)