import time
time.sleep(2.0)
from flask import Flask, render_template, request, redirect, session, flash, url_for, jsonify
import mariadb
import sys

from flask_cors import CORS
import socket

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
CORS(app)

# chave secreta da sessão
app.secret_key = 'flask'
app.config.from_object('config')

from views import auth


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


# PARA ALTERAR DATATIME DO RASPBERRY - http://127.0.0.1:5000/updatedatasistema?datetime="Mon Aug 28 20:10:11 UTC-3 2019"
@app.route('/updatedatasistema', methods=['GET', ])
def updatedatasistema():
    try:
        datetime_request = request.args['datetime']
        return_token = auth.verify_autentication_api(request.args['token'])
        if 'autenticado' in return_token:
            print('autenticado')
        else:
            return {'erro': 'Necessario estar logado'}
    except:
        return {'erro': 'Necessario estar logado'}
    import os
    from datetime import datetime
    try:
        # c = os.popen('sudo date -s "Mon Aug 28 20:10:11 UTC-3 2019"')
        print(f"sudo date -s  {datetime_request}")
        c = os.popen(f"sudo date -s  {datetime_request}")
        c.read()
        c.close()
        now = datetime.now()
    except Exception:
        return jsonify({'datetime': f"{now}"})
    return jsonify({'datetime': f"{now}"})  # ip do raspberry
    # return jsonify({'retorno' : f"{request.remote_addr}"}) #ip do requisitante


# PARA Alterar hora do sistema
@app.route('/scan', methods=['GET', 'POST'])
def scan():
    from datetime import datetime
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
        now = datetime.now()
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return jsonify({'retorno': f"{IP}", 'datetime': f"{now}"})  # ip do raspberry
    # return jsonify({'retorno' : f"{request.remote_addr}"}) #ip do requisitante


# configuração da rota index.
@app.route('/', methods=['GET', 'OPTIONS'])
def index():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_medicao, identificacao, temperatura, umidade, DATE_FORMAT(created, '(%d) %H:%i') FROM Medicao"
            " WHERE oculto = '0' ORDER BY created DESC LIMIT 40")
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
            " WHERE confirmado = '0' ORDER BY created DESC LIMIT 25")
        alertas = []
        for id_alerta, descricao, confirmado, temperatura, umidade, created in cur:
            alertas.append(
                {'id': id_alerta,
                 'descricao': descricao,
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


# API
@app.route('/medicao', methods=['GET'])
def medicao():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute("SELECT id_medicao, identificacao, temperatura, umidade, created "
                    "FROM Medicao m1 "
                    "where m1.created = (SELECT max(m2.created) FROM Medicao m2)")
        retornoBD = []
        for id_medicao, identificacao, temperatura, umidade, created in cur:
            retornoBD.append(
                {'id': id_medicao, 'Sensor': identificacao, 'Temperatura': float(temperatura),
                 'Umidade': float(umidade),
                 'Data': f"{created}"})

        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
    return jsonify(retornoBD)

# API
@app.route('/medicoes', methods=['GET'])
def medicoes():
    # para GET http://127.0.0.1:5000/medicao?datainicial=2020-12-10&datafinal=2021-01-20&oculto=1,1,1,1
    # print(request.args['datainicial']) #'2020-12-15'
    # print(request.args['datafinal']) # '2020-12-25'
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        print(request.args['oculto'])
        ocultopesq = request.args['oculto'].split(',')
        if len(ocultopesq) != 4:
            ocultopesq = [0, 1, 2, 3]
        cur.execute("SELECT id_medicao, identificacao, temperatura, umidade, created FROM Medicao"
                    " WHERE created >= ? and created <= ? and (oculto = ? or oculto = ? or oculto = ? or oculto = ?) ORDER BY created DESC LIMIT 50",
                    (request.args['datainicial'], request.args['datafinal'], ocultopesq[0], ocultopesq[1], ocultopesq[2], ocultopesq[3]))
        retornoBD = []
        for id_medicao, identificacao, temperatura, umidade, created in cur:
            retornoBD.append(
                {'id': id_medicao, 'Sensor': identificacao, 'Temperatura': float(temperatura),
                 'Umidade': float(umidade),
                 'Data': f"{created}"})
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
    return jsonify(retornoBD)


# API
@app.route('/alertas', methods=['GET'])
def alertas():
    # para GET http://127.0.0.1:5000/medicao?datainicial=2020-12-10&datafinal=2021-01-20
    # print(request.args['datainicial']) #'2020-12-15'
    # print(request.args['datafinal']) # '2020-12-25'
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()

        cur.execute(
            "SELECT id_alerta, descricao, confirmado, temperatura, umidade, created FROM Alerta"
            " WHERE confirmado = '0' ORDER BY created DESC LIMIT 25")
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
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
    print(alertas)
    return jsonify(alertas)


# API Alertas por data
@app.route('/alertasperiodo', methods=['GET'])
def alertasperiodo():
    # para GET http://127.0.0.1:5000/medicao?datainicial=2020-12-10&datafinal=2021-01-20
    # print(request.args['datainicial']) #'2020-12-15'
    # print(request.args['datafinal']) # '2020-12-25'
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_alerta, descricao, confirmado, temperatura, umidade, created FROM Alerta"
            " WHERE  created >= ? and created <= ? ORDER BY created DESC LIMIT 50",
            (request.args['datainicial'], request.args['datafinal']))
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
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
    print(alertas)
    return jsonify(alertas)


## api de configurações
@app.route('/apiconfig', methods=['GET'])
def apiconfig():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        cur.execute(
            "SELECT id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, DATE_FORMAT(updated, '%d/%m/%Y-%H:%i'), obs   FROM Config")
        configs = []
        for id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, updated, obs in cur:
            configs.append(
                {'id_config': id_config,
                 'intervalo_seconds': int(intervalo_seconds),
                 'temp_min': float(temp_min),
                 'temp_max': float(temp_max),
                 'umid_min': float(umid_min),
                 'umid_max': float(umid_max),
                 'updated': f"{updated}",
                 'obs': obs})
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
    return jsonify(configs)


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

        cur.execute("INSERT INTO Usuario(login, Senha, Nome, Telefone, Email, Privilegios) VALUES (?, ?, ?, ?, ?, ?);",
                    (
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
        # sys.exit(1)
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


@app.route('/loginapi', methods=['POST', ])
def loginapi():
    if 'senha' in request.json:
        if 'user' in request.json:
            login_retorno = auth.autentication_api(request.json['user'], request.json['senha'])
            return jsonify(login_retorno)
        else:
            return {'erro': 'Usuario invalido!'}
    else:
        return {'erro': 'Senha invalida!'}


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
        cur.execute(
            "SELECT id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, DATE_FORMAT(updated, '%d/%m/%Y-%H:%i'), obs   FROM Config")
        config = ''
        for id_config, intervalo_seconds, temp_min, temp_max, umid_min, umid_max, updated, obs in cur:
            config = Config(id_config, int(intervalo_seconds), float(temp_min), float(temp_max), float(umid_min),
                            float(umid_max), f"{updated}", obs)
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        sys.exit(1)
        cur.close()
        conn.close()
    if 'usuario_logado' not in session or session['usuario_logado'] == None:
        return redirect(url_for('login', proxima=url_for('novo')))
    print(config)
    return render_template('config.html', titulo='Configuração', config=config)


## Para realizar update nas configurações enviadas pelo form config
@app.route('/salvarconfig', methods=['POST', ])
def salvarconfig():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        intervalo = request.form['intervalo']
        if request.form['intervalo'] < 60:
            intervalo = 60
        cur.execute(
            "UPDATE Config SET intervalo_seconds= ?, temp_min = ?, temp_max = ?, umid_min = ?, umid_max = ?, updated = now(), obs = ? WHERE id_config = 'default';",
            (
                intervalo,
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
        # sys.exit(1)
        flash(e)
        return redirect(url_for('config'))
    # lista.append(usuario)
    return redirect(url_for('index'))


## API Para realizar update nas configurações enviadas pelo form config
@app.route('/apisalvarconfig', methods=['POST', ])
def apisalvarconfig():
    # print(request.headers)
    r = request.get_json()
    params = r.get("params")
    print(params)

    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        intervalo = params.get('intervalo_seconds')
        if params.get('intervalo_seconds') < 60:
            intervalo = 60

        cur.execute(
            "UPDATE Config SET intervalo_seconds= ?, temp_min = ?, temp_max = ?, umid_min = ?, umid_max = ?, updated = now(), obs = ? WHERE id_config = 'default';",
            (
                intervalo,
                params.get('temp_min'),
                params.get('temp_max'),
                params.get('umid_min'),
                params.get('umid_max'),
                params.get('obs')
            ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'retorno': f"salvo"})
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        cur.close()
        conn.close()
        # sys.exit(1)
        flash(e)
        return jsonify({'retorno': f"{e}"})
    # lista.append(usuario)
    return jsonify({'retorno': f"salvo"})


@app.route('/silenciaralertas')
def silenciaralertas():
    print('211')
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        print('231')
        cur.execute("UPDATE Alerta SET confirmado = '1' WHERE confirmado = '0';")
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
        return redirect(url_for('index'))
    # lista.append(usuario)
    return redirect(url_for('index'))


# api do Ionic para silenciar os alertas
@app.route('/silenciaralertasapi', methods=['GET'])
def silenciaralertasapi():
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        print('231')
        cur.execute("UPDATE Alerta SET confirmado = '1' WHERE confirmado = '0';")
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'retorno': f"ok"})
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        cur.close()
        conn.close()
        sys.exit(1)
        flash(e)
        return jsonify({'retorno': f"Erro Mariadb: {e}"})
    # lista.append(usuario)
    return jsonify({'retorno': f"ok"})



## API para deletar medições
@app.route('/apiocultarmedicoes', methods=['GET', ])
def apiocultarmedicoes():
    # print(request.args['id_medicao'])
    try:
        conn = mariadb.connect(user=user, password=password, host=host, port=port, database=database)
        cur = conn.cursor()
        # r = request.get_json()
        # params = r.get("params")

        # print(params)

        # id = f"{params.get('id_medicao')}"

        print(f"VALOR DE N: {request.args['id']}")
        cur.execute(
            "UPDATE Medicao SET oculto = ? WHERE id_medicao = ?;",
            (
                '9',
                request.args['id']
            ))
        conn.commit()
        cur.close()
        conn.close()
        return jsonify({'retorno': f"alterado"})
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        cur.close()
        conn.close()
        # sys.exit(1)
        flash(e)
        return jsonify({'retorno': f"{e}"})

    # lista.append(usuario)
    return jsonify({'retorno': f"salvo"})


if __name__ == "__main__":
    debug = True  # com essa opção como True, ao salvar, o "site" recarrega automaticamente.
    app.run(host='0.0.0.0', port=5000, debug=debug)


# ##app.run(host='0.0.0.0', port=8080)
#
#
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8080)
