CREATE DATABASE IF NOT EXISTS sistema_chaves CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sistema_chaves;

CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    login VARCHAR(50) NOT NULL UNIQUE,
    senha_hash VARCHAR(255) NOT NULL,
    nome VARCHAR(100) NOT NULL,
    perfil ENUM('admin', 'operador') NOT NULL DEFAULT 'operador',
    ativo BOOLEAN NOT NULL DEFAULT TRUE,
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pessoas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    tipo ENUM('militar', 'civil') NOT NULL,
    nip VARCHAR(20) UNIQUE,
    cpf VARCHAR(14) UNIQUE,
    quartel VARCHAR(100),
    status ENUM('ativo', 'inativo') NOT NULL DEFAULT 'ativo',
    criado_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chaves (
    id INT AUTO_INCREMENT PRIMARY KEY,
    andar VARCHAR(20) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    descricao VARCHAR(100),
    status ENUM('disponivel', 'retirada') NOT NULL DEFAULT 'disponivel',
    criada_em DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_chave (andar, numero)
);

CREATE TABLE IF NOT EXISTS movimentacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    chave_id INT NOT NULL,
    pessoa_id INT NOT NULL,
    tipo ENUM('checkin', 'checkout') NOT NULL,
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operador_id INT NOT NULL,
    observacao TEXT,
    FOREIGN KEY (chave_id) REFERENCES chaves(id),
    FOREIGN KEY (pessoa_id) REFERENCES pessoas(id),
    FOREIGN KEY (operador_id) REFERENCES usuarios(id)
);

CREATE TABLE IF NOT EXISTS logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    acao VARCHAR(100) NOT NULL,
    ip VARCHAR(45),
    data_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    detalhes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Dados de exemplo
INSERT INTO usuarios (login, senha_hash, nome, perfil) VALUES
('admin', '$2b$12$placeholder_will_be_set_by_seed', 'Administrador', 'admin');

INSERT INTO chaves (andar, numero, descricao) VALUES
('1', '101', 'Sala de reuniões'),
('1', '102', 'Almoxarifado'),
('2', '201', 'Secretaria'),
('2', '202', 'Sala do comandante');

INSERT INTO pessoas (nome, tipo, nip, quartel) VALUES
('João Silva', 'militar', '1234567', '1º DN'),
('Carlos Souza', 'militar', '7654321', '1º DN');

INSERT INTO pessoas (nome, tipo, cpf) VALUES
('Maria Oliveira', 'civil', '123.456.789-00'),
('Pedro Santos',  'civil', '987.654.321-00');
