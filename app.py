import time

time.sleep(10.0)
from operator import itemgetter

from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mariadb
import sys

# from flask_cors import CORS

# render template: passando o nome do modelo e a variáveis ele vai renderizar o template
# request: faz as requisições da nosa aplicação
# redirect: redireciona pra outras páginas
# session: armazena informações do usuário
# flash:mensagem de alerta exibida na tela
# url_for: vai para aonde o redirect indica

app = Flask(__name__)

user = 'kleber'
password = '1234'
host = 'localhost'
port = 3306
database = 'estufa'
# CORS(app)

# chave secreta da sessão
app.secret_key = 'flask'

class Usuario:
    def __init__(self, login, Nome, Telefone, Email, Privilegios, Senha):
        self.login = login
        self.Senha = Senha
        self.Nome = Nome
        self.Telefone = Telefone
        self.Email = Email
        self.Privilegios = Privilegios

class Medicao:
    def __init__(self, id_medicao, Indentificacao, Temperatura, Umidade, Data):
        self.id_medicao = id_medicao
        self.Indentificacao = Indentificacao
        self.Temperatura = Temperatura
        self.Umidade = Umidade
        self.Data = Data

class Config:
    def __init__(self, id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, updated, obs):
        self.id_config = id_config
        self.intervalo_seconds = intervalo_seconds
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.umid_min = umid_min
        self.umid_max = umid_max
        self.updated = updated
        self.obs = obs





# configuração da rota index.
@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_medicao, Identificacao, Temperatura, Umidade, DATE_FORMAT(Data, '(%d) %H:%i') FROM Medicao"
            " WHERE year(Data)=year(now()) ORDER BY Data DESC LIMIT 35")
        medicoes = []
        temperaturas = []
        umidades = []
        dias = []
        for id_medicao, Identificacao, Temperatura, Umidade, Data in cur:
            medicoes.append(
                {'id': id_medicao, 'Sensor': Identificacao, 'Temperatura': float(Temperatura),
                 'Umidade': float(Umidade),
                 'Data': f"{Data}"})
            # temperaturas.append(float(Temperatura))
            temperaturas.insert(0, float(Temperatura))
            umidades.insert(0, float(Umidade))
            # umidades.append(float(Umidade))
            dias.insert(0, f"{Data}")


        cur.execute(
            "SELECT id_alerta, descricao, confirmado, temperatura, umidade, DATE_FORMAT(created, '(%d) %H:%i') FROM Alerta"
            " WHERE 1=1 ORDER BY created DESC LIMIT 10")
        alertas = []
        for id_alerta, descricao, confirmado, temperatura, umidade, created in cur:
            alertas.append(
                {'id': id_alerta, 'descricao': descricao,
                 'confirmado': confirmado,
                 'temperatura': float(temperatura),
                 'umidade': float(umidade),
                 'created': f"{created}"})

        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb2: {e}")
        sys.exit(1)
        cur.close()
        conn.close()

    return render_template('lista.html', titulo='Medições', medicoes=medicoes, temperaturas=temperaturas,
                           umidades=umidades, dias=dias, alertas=alertas)
    # renderizando o template lista e as variáveis desejadas.


@app.route('/medicao')
def medicao():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()

        cur.execute("SELECT id_medicao, Identificacao, Temperatura, Umidade, Data FROM Medicao"
                    " WHERE year(Data)=year(now()) and month(Data)=month(now()) ORDER BY Data DESC LIMIT 50")
        retornoBD = []
        for id_medicao, Identificacao, Temperatura, Umidade, Data in cur:
            retornoBD.append(
                {'id': id_medicao, 'Sensor': Identificacao, 'Temperatura': float(Temperatura),
                 'Umidade': float(Umidade),
                 'Data': f"{Data}"})

        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
    return jsonify(retornoBD)


# configuração da rota novo, ela só poderá ser acessda se o usuário estiver logado, caso contrário redireciona para a tela de login
@app.route('/novo')
def novo():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute("SELECT login, Nome, Telefone, Email, Privilegios FROM Usuario")
        usuarios = []
        for login, Nome, Telefone, Email, Privilegios in cur:
            usuarios.append(Usuario(login, Nome, Telefone, Email, Privilegios, ' '))

        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
        cur.close()
        conn.close()

    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))

    return render_template('novo.html', titulo='Novo Usuario', usuarios=usuarios)
    # renderiza o template novo


# configuração da rpta criar que usa o método post para enviar dados dos nossos pokemons
@app.route('/criar', methods=['POST', ])
def criar():
    # nome = request.form['nome']
    # email = request.form['email']
    # tipo = request.form['tipo']
    usuario = Usuario(
        request.form['login'],
        request.form['Nome'],
        request.form['Telefone'],
        request.form['Email'],
        request.form['Privilegios'],
        request.form['Senha']
    )

    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()

        login = request.form['login'],
        senha = request.form['Senha'],

        cur.execute("INSERT INTO Usuario(login, Senha, Nome, Telefone, Email, Privilegios) VALUES (?, ?, ?, ?, ?, ?);", (
            login.lower(),
            senha.lower(),
            request.form['Nome'],
            request.form['Telefone'],
            request.form['Email'],
            request.form['Privilegios']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        cur.close()
        conn.close()
        sys.exit(1)
        flash(e)
        return redirect(url_for('novo'))

    # lista.append(usuario)
    return redirect(url_for('index'))



# configuração da rota login
@app.route('/login')
def login():
    proxima = request.args.get('proxima')
    return render_template('login.html', proxima=proxima)


# configuração da rota autenticar que verifica se existe o usuário no bd
@app.route('/autenticar', methods=['POST', ])
def autenticar():

    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()

        login = request.form['login'],
        senha = request.form['senha'],

        cur.execute("SELECT login, Senha, Nome, Telefone, Email, Privilegios FROM Usuario "
                    "WHERE login = %s and Senha = %s", (login[0].lower(), senha[0].lower(),))
        usuario = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        #sys.exit(1)
        return redirect(url_for('login'))
        flask(f"erro: {e}")

    # retorna ('kleber', '1234', 'Kleber Santos', '988572209', 'klebers@alunos.utfpr.edu.br', 'admin')
    if len(usuario) == 1:
        session['usuario_logado'] = usuario[0][0]
        flash(usuario[0][2] + ' acesso permitido!')
        proxima_pagina = request.form['proxima']
        return redirect(proxima_pagina)
    else:
        # caso as credenciais não sejam validadas, exibe mensagem de erro e redirecion para o login
        flash('Acesso negado, digite novamente!')
        return redirect(url_for('login'))


# configuração da rota logout
@app.route('/logout')
def logout():
    session['usuario_logado'] = None
    flash('Não autenticado, necessário efetuar o login')
    return redirect(url_for('index'))

## formulário de configuração
@app.route('/config')
def config():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute("SELECT id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, DATE_FORMAT(updated, '%d/%m/%Y-%H:%i'), obs   FROM Config")
        config = ''
        for id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, updated, obs in cur:
            config = Config(id_config, int(intervalo_seconds),  float(temp_min),  float(temp_max),  float(umid_min), float(umid_max), f"{updated}", obs)
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
        cur.close()
        conn.close()
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    return render_template('config.html', titulo='Configuração', config=config)



## Para realizar update nas configurações enviadas pelo form config
@app.route('/salvarconfig', methods=['POST', ])
def salvarconfig():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()

        cur.execute("UPDATE Config SET intervalo_seconds= ?, temp_min = ?, temp_max = ?, umid_min = ?, umid_max = ?, updated = now(), obs = ? WHERE id_config = 'default';", (
            request.form['intervalo'],
            request.form['temperaturaMinima'],
            request.form['temperaturaMaxima'],
            request.form['umidadeMinima'],
            request.form['umidadeMaxima'],
            request.form['obs']
        ))
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('index'))
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        cur.close()
        conn.close()
        #sys.exit(1)
        flash(e)
        return redirect(url_for('config'))

    # lista.append(usuario)
    return redirect(url_for('index'))


# app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

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
