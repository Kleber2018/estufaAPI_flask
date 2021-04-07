# estufaTabaco flaskAPI

Script para inicializar API para acessar os dados do MariaDB

## Atualizar repositórios


pip install -U mariadb
pip3 install Flask_Cors
pip3 install -U flask-cors

## configuração

app.run(host='0.0.0.0', port=8080)

para acessar por outro computador conectado na mesma rede: ip:/rota
ex: 192.168.0.101:8080/teste

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