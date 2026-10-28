CREATE TABLE tipo_pessoa (
    id_tipo_pessoa INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id_tipo_pessoa),
    UNIQUE KEY uk_tipo_pessoa_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE tipo_perfil (
    id_tipo_perfil INT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome VARCHAR(50) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id_tipo_perfil),
    UNIQUE KEY uk_tipo_perfil_nome (nome)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE pessoa (
    id_pessoa INT UNSIGNED NOT NULL AUTO_INCREMENT,
    chave CHAR(36) NOT NULL DEFAULT (UUID()),
    id_tipo_pessoa INT UNSIGNED NOT NULL,
    id_tipo_perfil INT UNSIGNED NULL DEFAULT NULL,
    senha VARCHAR(255) NOT NULL,
    nome_razao VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    cpf_cnpj VARCHAR(14) NOT NULL,
    ativo TINYINT(1) NOT NULL DEFAULT 1,
    PRIMARY KEY (id_pessoa),
    UNIQUE KEY uk_pessoa_chave (chave),
    UNIQUE KEY uk_pessoa_email (email),
    UNIQUE KEY uk_pessoa_cpf_cnpj (cpf_cnpj),
    KEY idx_pessoa_tipo_pessoa (id_tipo_pessoa),
    CONSTRAINT fk_pessoa_tipo_pessoa
        FOREIGN KEY (id_tipo_pessoa) REFERENCES tipo_pessoa (id_tipo_pessoa)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

INSERT INTO tipo_pessoa (nome) VALUES
    ('Pessoa Física'),
    ('Pessoa Jurídica');

INSERT INTO tipo_perfil (nome) VALUES
    ('Pessoa atípica'),
    ('Mãe'),
    ('Pai'),
    ('Responsável'),
    ('Familiar'),
    ('Profissional'),
    ('Educador'),
    ('Instituição');