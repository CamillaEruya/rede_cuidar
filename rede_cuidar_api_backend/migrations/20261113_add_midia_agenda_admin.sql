-- Rede Cuidar: campos de mídia da agenda e perfil Administrador
-- Compatível com MariaDB

ALTER TABLE agenda
    ADD COLUMN IF NOT EXISTS midia_url VARCHAR(500) NULL,
    ADD COLUMN IF NOT EXISTS midia_tipo VARCHAR(100) NULL;

INSERT INTO tipo_perfil (id_tipo_perfil, nome, ativo)
VALUES (9, 'Administrador', 1)
ON DUPLICATE KEY UPDATE id_tipo_perfil = id_tipo_perfil;
