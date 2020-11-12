import mariadb
import sys
import json

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

# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from flask import Flask

app = Flask(__name__)


@app.route('/teste')
def hello_world():
    return 'Hello World!'


@app.route('/medicao')
def medicao():

    cur.execute("SELECT Identificacao FROM Medicao WHERE id_medicao=?", (7,))
    for Identificacao in cur:
        idem = Identificacao
        print(f"Identificacao: {Identificacao}")
    print(idem)
    return f"Identificacao: {idem}"

@app.route('/medicoes')
def medicoes():

    cur.execute("SELECT id_medicao, Identificacao, Temperatura, Umidade FROM Medicao")
    retornoBD = []
    for id_medicao, Identificacao, Temperatura, Umidade in cur:
        retornoBD.append({'id': id_medicao, 'Identificação': Identificacao, 'Temperatura': Temperatura, 'Umidade': Umidade})
        print(f"Identificacao: {retornoBD}")
    print(retornoBD)

    return f"Identificacao: {retornoBD}"



app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
