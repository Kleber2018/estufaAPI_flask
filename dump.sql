CREATE DATABASE estufa;
USE estufa;

CREATE TABLE Usuario (
id_usuario INTEGER NOT NULL AUTO_INCREMENT,
Login VARCHAR(8),
Senha VARCHAR(8),
Nome VARCHAR(150),
Telefone CHAR(15),
Email VARCHAR(150),
Privilegios VARCHAR(10),
PRIMARY KEY (id_usuario)
);

INSERT INTO Usuario(login, Senha, Nome, Telefone, Email, Privilegios) VALUES ('kleber', '1234', 'Kleber Santos', '988572209', 'klebers@alunos.utfpr.edu.br', 'admin' );


CREATE TABLE Medicao (
id_medicao INTEGER NOT NULL AUTO_INCREMENT,
Identificacao VARCHAR(15),
Temperatura DECIMAL(3,1),
Umidade DECIMAL(3,1),
Data DATETIME,
PRIMARY KEY (id_medicao)
);

INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 23.4, 62.0, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 20.4, 61.2, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 21.4, 62.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 22.4, 62.1, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 22.4, 60.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 23.4, 60.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 23.4, 60.2, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 22.4, 56.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 20.4, 56.3, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 20.2, 57.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 20.1, 60.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 19.3, 62.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 18.4, 62.5, now());
INSERT INTO Medicao(Identificacao, Temperatura, Umidade, Data) VALUES ('Sensor 1', 18.2, 63.7, now());


CREATE USER 'kleber'@'localhost'   IDENTIFIED BY '1234';

GRANT SELECT, INSERT, UPDATE, DELETE, DROP
   ON estufa.Medicao
   TO 'kleber'@'localhost';

GRANT SELECT, INSERT, UPDATE, DELETE, DROP
   ON estufa.Usuario
   TO 'kleber'@'localhost';
