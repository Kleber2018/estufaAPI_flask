#para jwt
import hmac
import hashlib
import base64
import json
import datetime
import mariadb
from app import app


#https://medium.com/@gustavolpss/json-web-tokens-jwt-em-python-c76fb34d8d9
secret_key = '52d3f853c19f8b63c0918c126422aa2d99b1aef33ec63d41dea4fadf19406e54'

def create_jwt(payload):
    payload = json.dumps(payload).encode()
    header = json.dumps({
        'typ': 'JWT',
        'alg': 'HS256'
    }).encode()
    b64_header = base64.urlsafe_b64encode(header).decode()
    b64_payload = base64.urlsafe_b64encode(payload).decode()
    signature = hmac.new(
        key=secret_key.encode(),
        msg=f'{b64_header}.{b64_payload}'.encode(),
        digestmod=hashlib.sha256
    ).digest()
    jwt = f'{b64_header}.{b64_payload}.{base64.urlsafe_b64encode(signature).decode()}'
    return jwt


def verify_and_decode_jwt(jwt):
    b64_header, b64_payload, b64_signature = jwt.split('.')
    b64_signature_checker = base64.urlsafe_b64encode(
        hmac.new(
            key=secret_key.encode(),
            msg=f'{b64_header}.{b64_payload}'.encode(),
            digestmod=hashlib.sha256
        ).digest()
    ).decode()

    # payload extraido antes para checar o campo 'exp'
    payload = json.loads(base64.urlsafe_b64decode(b64_payload))
    unix_time_now = datetime.datetime.now().timestamp()

    if payload.get('exp') and payload['exp'] < unix_time_now:
        raise Exception('Token expirado')

    if b64_signature_checker != b64_signature:
        raise Exception('Assinatura invalida')

    return payload


def autentication_api(user, senha):
    try:
        #enviado pelo param do get na url
        #print(request.args.get('user'))
        conn = mariadb.connect(user=app.config['BD_USER'], password=app.config['BD_PASSWORD'], host=app.config['BD_HOST'], port=app.config['BD_PORT'], database=app.config['DATABASE_NAME'])
        cur = conn.cursor()
        cur.execute("SELECT login, Senha, Nome, Telefone, Email, Privilegios FROM Usuario "
                    "WHERE login = %s and Senha = %s", (user, senha))
        usuario = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        # sys.exit(1)
        return {'erro': 'Erro no banco de dados, reinicie a central!', 'description': f"Erro Mariadb: {e}"}
    # retorna ('kleber', '1234', 'Kleber Santos', '988572209', 'klebers@alunos.utfpr.edu.br', 'admin')
    if len(usuario) == 1:
        print('antes',  usuario[0][0])
        print(usuario[0][0])
        payload = {
            'login': user,
            'senha': senha
            #'exp': (datetime.datetime.now() + datetime.timedelta(weeks=2)).timestamp(),
        }
        jwt_created = create_jwt(payload)
        return {'token': jwt_created}
    else:
        return {'erro': 'Usuario ou senha invalido!'}


    #return_token = verify_autentication_api(jwt_created)
    #if 'autenticado' in return_token:
    #    print('autenticado')
    #else:
    #    print('não autenticado')
def verify_autentication_api(token):
    decoded_jwt = verify_and_decode_jwt(token)
    if 'senha' in decoded_jwt:
        if 'login' in decoded_jwt:
            print('existe')
        else:
            return {'erro': 'Usuario invalido!'}
    else:
        return {'erro': 'Senha invalida!'}

    try:
        # enviado pelo param do get na url
        # print(request.args.get('user'))
        conn = mariadb.connect(user=app.config['BD_USER'], password=app.config['BD_PASSWORD'],
                               host=app.config['BD_HOST'], port=app.config['BD_PORT'],
                               database=app.config['DATABASE_NAME'])
        cur = conn.cursor()
        cur.execute("SELECT login, Senha, Nome, Telefone, Email, Privilegios FROM Usuario "
                    "WHERE login = %s and Senha = %s", (decoded_jwt['login'], decoded_jwt['senha']))
        usuario = cur.fetchall()
        cur.close()
        conn.close()
    except mariadb.Error as e:
        print(f"Erro Mariadb: {e}")
        # sys.exit(1)
        return {'erro': 'Erro no banco de dados, reinicie a central!', 'description': f"Erro Mariadb: {e}"}
        # retorna ('kleber', '1234', 'Kleber Santos', '988572209', 'klebers@alunos.utfpr.edu.br', 'admin')
    if len(usuario) == 1:
        return {'autenticado': 'ok'}
    else:
        return {'erro': 'Usuario ou senha invalido!'}