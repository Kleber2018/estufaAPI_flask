from flask import Flask

app = Flask(__name__)


@app.route('/teste')
def hello_world():
    return 'Hello World!'


@app.route('/r')
def teste():
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
