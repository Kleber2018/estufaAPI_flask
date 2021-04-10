# estufaTabaco flaskAPI

Script para inicializar API para acessar os dados do MariaDB

## Atualizar repositórios




instalar flask-cors
pip3 install -U flask-cors

conector Maria Db
pip3 install mariadb

outros 
pip install -U mariadb
pip3 install Flask_Cors

## configuração

app.run(host='0.0.0.0', port=8080)

para acessar por outro computador conectado na mesma rede: ip:/rota
ex: 192.168.0.101:8080/teste


##Configurar flask server
https://www.youtube.com/watch?v=yThiYsPBphA

sudo su

Instalar dependencias:
apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools

Criar ambiente virtual:(para separar dos outros projetos)
apt install python3-venv

Criar diretório:
mkdir /flesk
cd /flesk

criar ambiente virtual: python3.7 -m venv esflesk

ativar: source esflesk/bin/activate

Instalar dependencia: pip install wheel
Instalar dependencia:pip install gunicorn flask

copiando para diretório:
cp -r  /home/estufaAPI_flask/* /flesk/

testando: python3 app.py

criar o arquivo de produção, ponto de entrada:
nano wsgi.py

from flesk import app.py

if __name__ == '__main__':
        app.run()


executar o gunicorn(servidor rodando):
gunicorn --bind 0.0.0.0:5000 wsgi:app

sair do ambiente virtual: deactivate



iniciar automáticamente
criar arquivo de serviço

nano /etc/systemd/es.service

[Unit]
Description=Iniciando API Estufa
After=network.target

[Service]
User=pi
Group=www-data

WorkingDirectory=/flesk
Environment="PATH=/flesk/esflesk/bin"
ExecStart=/flesk/esflesk/bin/gunicorn --workers 3 --bind unix:esflesk.sock -m 007 wsgi:app


[Install]
WantedBy=multi-user.target



Hbilitar: sudo systemctl enable es.service

## MariaDB

iniciar: sudo /etc/init.d/mysql start
Finalizar: sudo /etc/init.d/mysql stop
Acessar: sudo mysql -u root -p
SQL:
Consultando

    SHOW databases;
    SHOW tables;
    
SELECT * FROM estufa.Medicao;

SELECT * FROM estufa.Usuario;

DROP TABLE nome_tabela;


## Autostart no Raspbian

Para autoexecutar colar o arquivo autorunAPI.desktop da pasta autostart na pasta /home/pi/.config/autostart

## Criar access point

https://www.techtudo.com.br/dicas-e-tutoriais/2017/05/aprenda-como-criar-um-access-point-com-o-raspberry-pi.ghtml

## Inicialização 

Para inicializar automaticamente inserir com editor Vim o trecho abaixo

Abrir editor vim com o comando: vim /etc/rc.local


(sleep 120; python3 /home/pi/PycharmProjects/estufaAPI_flask/app.py) &


##documentações


Datas no MARIADB:
https://mariadb.com/kb/en/date_format/


gráfico:
https://www.chartjs.org/docs/latest/charts/line.html


Template com flask:
https://imasters.com.br/desenvolvimento/conhecendo-o-jinja2-um-mecanismo-para-templates-no-flask