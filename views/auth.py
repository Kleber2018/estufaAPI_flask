#para jwt
import hmac
import hashlib
import base64
import json
import datetime

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
        raise Exception('Assinatura inválida')

    return payload

