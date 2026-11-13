-- =====================================================
-- REDE CUIDAR
-- Migração: divulgação e campanhas de profissionais
-- =====================================================

-- Tabela de divulgações dos profissionais
CREATE TABLE IF NOT EXISTS profissional_divulgacao (
    id_divulgacao INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_profissional INT UNSIGNED NOT NULL,
    titulo VARCHAR(150) NOT NULL,
    descricao TEXT NOT NULL,
    midia_url VARCHAR(500) DEFAULT NULL,
    midia_tipo VARCHAR(100) DEFAULT NULL,
    data_criacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_divulgacao_profissional
        FOREIGN KEY (id_profissional)
        REFERENCES profissional(id_profissional)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;


-- Tabela de campanhas dos profissionais
CREATE TABLE IF NOT EXISTS campanha_profissional (
    id_campanha INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    id_profissional INT UNSIGNED NOT NULL,
    plano_nome VARCHAR(100) NOT NULL,
    dias INT UNSIGNED NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    status ENUM('ATIVA','EXPIRADA','PENDENTE')
        NOT NULL DEFAULT 'PENDENTE',
    data_inicio DATETIME NOT NULL,
    data_fim DATETIME NOT NULL,

    CONSTRAINT fk_campanha_profissional
        FOREIGN KEY (id_profissional)
        REFERENCES profissional(id_profissional)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB
DEFAULT CHARSET=utf8mb4
COLLATE=utf8mb4_unicode_ci;