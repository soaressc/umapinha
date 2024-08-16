CREATE SCHEMA umapinha;

USE umapinha;

CREATE TABLE Usuario (
    id_usuario INT NOT NULL AUTO_INCREMENT,
    senha VARCHAR(40) NOT NULL,
    email VARCHAR(245) NOT NULL,
    nome VARCHAR(300),
    PRIMARY KEY (id_usuario)
);

CREATE TABLE Andar (
    numero INT NOT NULL AUTO_INCREMENT,
    concluido TINYINT,
    id_usuario INT,
    PRIMARY KEY (numero),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Jogo (
    id_jogo INT NOT NULL AUTO_INCREMENT,
    vidas INT,
    feito TINYINT,
    id_usuario INT,
    PRIMARY KEY (id_jogo),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

CREATE TABLE Alternativa_Correta (
    id_alternativa_correta INT NOT NULL AUTO_INCREMENT,
    texto_alternativa TEXT,
    PRIMARY KEY (id_alternativa_correta)
);

CREATE TABLE Questao (
    id_questao INT NOT NULL AUTO_INCREMENT,
    texto_pergunta TEXT(500),
    respondida TINYINT DEFAULT 0,
    id_jogo INT,
    id_usuario INT,
    numero INT,
    id_alternativa_correta INT,
    PRIMARY KEY (id_questao),
    FOREIGN KEY (id_jogo) REFERENCES Jogo(id_jogo),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario),
    FOREIGN KEY (numero) REFERENCES Andar(numero),
    FOREIGN KEY (id_alternativa_correta) REFERENCES Alternativa_Correta(id_alternativa_correta)
);

CREATE TABLE Alternativa (
    id_alternativa INT NOT NULL AUTO_INCREMENT,
    texto_alternativa TEXT,
    id_questao INT,
    PRIMARY KEY (id_alternativa),
    FOREIGN KEY (id_questao) REFERENCES Questao(id_questao)
);

INSERT INTO Usuario (id_usuario, nome, email, senha) VALUES (1, 'Umapinha', 'umapinha@exemplo.com', 'senha123');

INSERT INTO Andar (numero, concluido, id_usuario) VALUES (1, 0, '1');
INSERT INTO Andar (numero, concluido, id_usuario) VALUES (2, 0, '1');
INSERT INTO Andar (numero, concluido, id_usuario) VALUES (3, 1, '1');
INSERT INTO Andar (numero, concluido, id_usuario) VALUES (4, 0, '1');
INSERT INTO Andar (numero, concluido, id_usuario) VALUES (5, 1, '1');

SELECT * FROM Andar WHERE numero = 4;


INSERT INTO Jogo (id_jogo, vidas, feito, id_usuario) VALUES (1, 3, 0, 1);

INSERT INTO Alternativa_Correta (id_alternativa_correta, texto_alternativa) VALUES (1, 'Verificar se é seguro e sair rapidamente');
INSERT INTO Questao (id_questao, texto_pergunta, id_jogo, id_usuario, numero, id_alternativa_correta) VALUES (1, 'Um alarme de incêndio soa. Como usar essa saída de emergência?', 1, 1, 1, 1);
INSERT INTO Alternativa (id_alternativa, texto_alternativa, id_questao) VALUES 
(1, 'Verificar se é seguro e sair rapidamente', 1),
(2, 'Esperar o alarme parar', 1),
(3, 'Chamar o número de emergência e esperar', 1),
(4, 'Ignorar a saída de emergência', 1);

INSERT INTO Alternativa_Correta (id_alternativa_correta, texto_alternativa) VALUES (6, 'Acionar o alarme de incêndio');
INSERT INTO Questao (id_questao, texto_pergunta, id_jogo, id_usuario, numero, id_alternativa_correta) VALUES (2, 'O que você deve fazer PRIMEIRO ao encontrar um pequeno incêndio e ver uma caixa de incêndio por perto?', 1, 1, 2, 6);
INSERT INTO Alternativa (id_alternativa, texto_alternativa, id_questao) VALUES 
(5, 'Tentar apagar o fogo com as mãos', 2),
(6, 'Acionar o alarme de incêndio', 2),
(7, 'Ignorar o incêndio', 2),
(8, 'Chamar os bombeiros', 2);

INSERT INTO Alternativa_Correta (id_alternativa_correta, texto_alternativa) VALUES (12, 'Puxar o pino de segurança, direcionar o bico para a base do fogo e pressionar a alavanca');
INSERT INTO Questao (id_questao, texto_pergunta, id_jogo, id_usuario, numero, id_alternativa_correta) VALUES (3, 'Qual é o procedimento correto para utilizar um extintor de pó químico seco?', 1, 1, 4, 12);
INSERT INTO Alternativa (id_alternativa, texto_alternativa, id_questao) VALUES 
(9, 'Apontar o bico para o topo do fogo e pressionar a alavanca', 3),
(10, 'Jogar água diretamente sobre o fogo', 3),
(11, 'Empurrar o botão de liberação do pó e esperar que o extintor se esvazie', 3),
(12, 'Puxar o pino de segurança, direcionar o bico para a base do fogo e pressionar a alavanca', 3);


-- A view Status_Jogo pode ser mantida como está ou ajustada conforme necessidade.

-- View que verifica se todos os andares forem concluídos
CREATE VIEW Status_Jogo AS
SELECT 
    u.id_usuario,
    j.id_jogo,
    CASE 
        WHEN COUNT(a.numero) = SUM(a.concluido) THEN 'Concluído'
        ELSE 'Incompleto'
    END AS status_jogo
FROM 
    Usuario u
JOIN 
    Jogo j ON u.id_usuario = j.id_usuario
LEFT JOIN 
    Andar a ON j.id_usuario = a.id_usuario
GROUP BY 
    u.id_usuario, j.id_jogo;

SELECT * FROM Status_Jogo WHERE id_usuario = 1 AND status_jogo = 'Concluído';


# Função de validação para email
DELIMITER //
CREATE FUNCTION EmailJaExiste(email_usuario VARCHAR(245))
RETURNS BOOLEAN
DETERMINISTIC
BEGIN
    DECLARE resultado BOOLEAN;
    SELECT COUNT(*) INTO resultado
    FROM Usuario
    WHERE email = email_usuario;
    RETURN resultado > 0;
END //
DELIMITER ;

# Transação para mudança de senha
DELIMITER //
CREATE PROCEDURE change_password(
    IN user_email_update VARCHAR(254), 
    IN user_password_old VARCHAR(45), 
    IN new_password VARCHAR(45), 
    IN confirm_new_password VARCHAR(45)
)  
BEGIN
    DECLARE old_password VARCHAR(45);

    -- Inicia a transação
    START TRANSACTION;

    -- 1. Obter a senha antiga do usuário
    SELECT senha INTO old_password
    FROM Usuario 
    WHERE email = user_email_update;

    -- 2. Verificar se a senha antiga confere
    IF old_password = user_password_old THEN
        
        -- 3. Verificar se a nova senha e a confirmação coincidem
        IF new_password = confirm_new_password THEN
            -- 4. Atualizar a senha
            UPDATE Usuario
            SET senha = new_password
            WHERE email = user_email_update;

            -- 5. Confirmar a transação
            COMMIT;
            SELECT 'Senha atualizada com sucesso!' AS status;
        ELSE
            -- Reverter a transação se as senhas não coincidirem
            ROLLBACK;
            SELECT 'Confirmação de senha não coincide com nova senha.' AS status;
        END IF;
    ELSE
        -- Reverter a transação se a senha antiga não confere
        ROLLBACK;
        SELECT 'Senha antiga não confere.' AS status;
    END IF;
END //
DELIMITER ;

SELECT * FROM Usuario;

# Atualizar a senha para 'novaSenha123' se a senha antiga for '123456' e se a confirmação da nova senha coincidir.
CALL change_password('teste@teste.com', '123456', 'novaSenha123', 'novaSenha123');

# Trigger log de cadastro (insert) ou update de usuário
# Criação de tabela para armazenamento do log
CREATE TABLE log_usuario (
    id_log INT NOT NULL AUTO_INCREMENT,
    id_usuario INT,
    acao VARCHAR(50),
    data_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id_log),
    FOREIGN KEY (id_usuario) REFERENCES Usuario(id_usuario)
);

# Trigger insert
DELIMITER //
CREATE TRIGGER insert_usuario
AFTER INSERT ON Usuario
FOR EACH ROW
BEGIN
    INSERT INTO log_usuario (id_usuario, acao)
    VALUES (NEW.id_usuario, 'Inserção');
END;
//
DELIMITER ;

# Trigger update
DELIMITER //
CREATE TRIGGER update_usuario
AFTER UPDATE ON Usuario
FOR EACH ROW
BEGIN
    INSERT INTO log_usuario (id_usuario, acao)
    VALUES (NEW.id_usuario, 'Atualização');
END;
//
DELIMITER ;