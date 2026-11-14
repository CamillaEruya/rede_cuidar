-- --------------------------------------------------------
-- Servidor:                     127.0.0.1
-- Versão do servidor:           10.4.32-MariaDB - mariadb.org binary distribution
-- OS do Servidor:               Win64
-- HeidiSQL Versão:              12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Copiando estrutura do banco de dados para rede_cuidar
CREATE DATABASE IF NOT EXISTS `rede_cuidar` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */;
USE `rede_cuidar`;

-- Copiando estrutura para tabela rede_cuidar.agenda
CREATE TABLE IF NOT EXISTS `agenda` (
  `id_agenda` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_pessoa` int(10) unsigned NOT NULL,
  `titulo` varchar(150) NOT NULL,
  `descricao` text NOT NULL,
  `tipo_evento` varchar(30) NOT NULL,
  `status` enum('ATIVO','CANCELADO','CONCLUIDO') NOT NULL DEFAULT 'ATIVO',
  `data_evento` datetime NOT NULL,
  `data_criacao` timestamp NOT NULL DEFAULT current_timestamp(),
  `data_cadastro` timestamp NOT NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id_agenda`),
  KEY `fk_agenda_pessoa` (`id_pessoa`),
  CONSTRAINT `fk_agenda_pessoa` FOREIGN KEY (`id_pessoa`) REFERENCES `pessoa` (`id_pessoa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copiando dados para a tabela rede_cuidar.agenda: ~5 rows (aproximadamente)
INSERT INTO `agenda` (`id_agenda`, `id_pessoa`, `titulo`, `descricao`, `tipo_evento`, `status`, `data_evento`, `data_criacao`, `data_cadastro`) VALUES
	(1, 41, ' Psicologa', 'dra Maria ', 'consulta', 'ATIVO', '2026-10-29 18:15:01', '2026-10-29 21:15:10', '2026-10-29 21:15:10'),
	(6, 37, 'Roda de conversa para mães', 'Encontro para compartilhar experiências.', 'CONVERSA', 'ATIVO', '2026-11-10 19:00:00', '2026-10-29 21:16:57', '2026-10-29 21:16:57'),
	(7, 38, 'Palestra sobre inclusão', 'Atividade informativa sobre inclusão.', 'PALESTRA', 'ATIVO', '2026-11-15 14:00:00', '2026-10-29 21:16:57', '2026-10-29 21:16:57'),
	(8, 39, 'Encontro de famílias', 'Momento de integração entre familiares.', 'ENCONTRO', 'ATIVO', '2026-11-20 10:00:00', '2026-10-29 21:16:57', '2026-10-29 21:16:57'),
	(9, 40, 'Oficina de atividades inclusivas', 'Oficina comunitária inclusiva.', 'ATIVIDADE', 'CANCELADO', '2026-11-25 15:00:00', '2026-10-29 21:16:57', '2026-10-29 21:16:57');

-- Copiando estrutura para tabela rede_cuidar.pessoa
CREATE TABLE IF NOT EXISTS `pessoa` (
  `id_pessoa` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `chave` char(36) NOT NULL DEFAULT uuid(),
  `id_tipo_pessoa` int(10) unsigned NOT NULL,
  `id_tipo_perfil` int(10) unsigned DEFAULT NULL,
  `senha` varchar(255) NOT NULL,
  `nome_razao` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `cpf_cnpj` varchar(14) NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_pessoa`),
  UNIQUE KEY `uk_pessoa_email` (`email`),
  UNIQUE KEY `uk_pessoa_cpf_cnpj` (`cpf_cnpj`),
  UNIQUE KEY `uk_pessoa_chave` (`chave`),
  KEY `idx_pessoa_tipo_pessoa` (`id_tipo_pessoa`),
  CONSTRAINT `fk_pessoa_tipo_pessoa` FOREIGN KEY (`id_tipo_pessoa`) REFERENCES `tipo_pessoa` (`id_tipo_pessoa`)
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copiando dados para a tabela rede_cuidar.pessoa: ~18 rows (aproximadamente)
INSERT INTO `pessoa` (`id_pessoa`, `chave`, `id_tipo_pessoa`, `id_tipo_perfil`, `senha`, `nome_razao`, `email`, `cpf_cnpj`, `ativo`) VALUES
	(20, '6c44938b-bf68-11f1-9c71-506508f7c0dd', 1, 2, '$argon2id$v=19$m=65536,t=3,p=4$TTMeTIcPwCVhNQECl+r6Gw$h9Z9u43+GRBeE9Z3b3A3RtliJRHWmCiTEfgrcJlFRJo', 'jose joaoa da silva1', 'jose_joaoa@gmail.com', '29152859851', 1),
	(21, '6c44c155-bf68-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$DrZNOFPJdg0GuPBlILVf/g$qBsuN+TrBS9oyK/FdoGulIbANdiLfL21vRqIdzYGkdg', 'miguel  da silva', 'miguel.silva@example.com', '64531612060', 1),
	(22, '6c44c5b8-bf68-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$3NA1Aupv6ZzKWVgw5zd91A$dTEuZ08W5aLmLPXMWXsGzqEyr9mQ070SbpnS+wEncMc', 'miguel24da silva', 'miguel24.silva@example.com', '06411919011', 1),
	(24, '6c44c865-bf68-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$+xbHF1/OrOWziTBNf+Pklw$wKKVi+YEWLZA+Wi9EzZMl7XQOna85uanTFn86udIcvI', 'miguel3  da silva', 'miguel3.silva@example.com', '23487134039', 1),
	(25, 'c2cbb7dd-bf68-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$ieI3/LYVJ5UBeDLDgGTurA$yiWXG2DYUGbBI2u2+eo4Phh1dqvnyZSUDLSO7cZiW2Q', 'miguel camilo', 'migue20.silva@example.com', '90092325068', 1),
	(27, '15f91f91-c01b-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$m7McEPPnPXjoWy5f/ebkeg$WVIUH07teGvyzX61A5S29WSdl3HKAHwZakVEzzLDU8Q', 'camilla teste50', 'camillateste50@gmail.com', '27630262060', 1),
	(28, 'a2acd991-c01b-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$bB+Eev9IL8c5mqM/mRv/ow$LSQhZbR/TVhRjNDjAhJcvSTSWlAqceV89pq3DUn6C3s', 'camilateste2', 'camilateste2@gmail.com', '57211609001', 1),
	(29, '03a300dd-c01c-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$SrzS7VWOrrxP2hlmB6n8qA$MgQoCN4eWG2IczpddGBmt4KKQ/GuVdU5uwhc/hLWCpY', 'teste34', 'teste34@gmail.com', '09724333094', 1),
	(30, '5ee4b96c-c01c-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$Z2vUG3L8iq4Pn0+SDpYlVw$uICH1WbxrCJkdjJ3OJnWj5iVOgTbtMxtOXDmT4dzZ4k', 'camilateste', 'camillateste5@gmail.com', '89129311055', 1),
	(31, '011251dc-c01d-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$C1kL3D+j3TpQre/eM1B+OQ$jRNnT2ykfJYvOJVvP5eWJTP0e28t0878Tfk1Q4PKgPk', 'camilateste6', 'camilateste6@gmail.com', '93710194091', 1),
	(32, 'f3d3d5a2-c10c-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$/RzL12Yhul9fgelFlRksnA$tsRCNL4iL04gTPO9C+m7g8RASHAnIT9TmcBn0mAxAsU', 'teste80', 'teste80@gmail.com', '74180821001', 1),
	(35, '418379f0-c252-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$q+dHhyAK6fvwZwhCHJreGw$UqYKyvq02CjumgvPJ+45cYD0uME/RIiDH9q+9VrHf94', 'teste8', 'teste8@gmail.com', '95351423057', 1),
	(37, '0c8ec050-c592-11f1-9c71-506508f7c0dd', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$X+CaN++tParYkZSSqyvSMw$o01iqC/HLiRKpKzDMPgQL6/BlXOGtyVosbK51/ix+3U', 'fabio', 'fabio@gmail.com', '29165669029', 1),
	(38, '9e5cf93a-c98a-11f1-9e5d-2c9c5870e66e', 1, 0, '$argon2id$v=19$m=65536,t=3,p=4$Ea2AgdF6Pjd850/tssuakw$omHQzVqaPl7JHMaSPk59BMVoCcZoHWfczCOEW57rY1g', 'camilateste3', 'camilateste3@gmail.com', '55722086045', 1),
	(39, '9c04600e-c9d1-11f1-9e5d-2c9c5870e66e', 1, 4, '$argon2id$v=19$m=65536,t=3,p=4$TDbl1yj6M68lgi1JDlSd9g$NaZq1KWy6szBsr1WCnAqBPM3YqPpTN9Vzw8/Im7fy5s', 'Manoel4', 'manoek@teste.com', '37146961052', 1),
	(40, 'e1968510-cee5-11f1-9e5d-2c9c5870e66e', 1, 1, '$argon2id$v=19$m=65536,t=3,p=4$4dmqrUKw+syFSrOL2n2I6A$Bc+6b+LiTN2yFqa9lK1A7OvHj06Sy7vRtL3e3FcD4Sk', 'camilaT10', 'camila10@gmail.com', '72013895054', 1),
	(41, 'c9464c74-cf17-11f1-9e5d-2c9c5870e66e', 1, 7, '$argon2id$v=19$m=65536,t=3,p=4$/Gh2WO+soGewUHa5Dmb7Ng$KpAtgc66cFAn4L5lGQoJFiLbybx9UAB3hiHXQv065b8', 'camila10', 'camilat10@gmail.com', '63764458020', 1),
	(42, '479c7c83-dc58-11f1-9b17-4d54bebc7208', 1, 4, '$argon2id$v=19$m=65536,t=3,p=4$aeGa4V31gfKpbrCb7H7fCQ$aTz/Zr1xWla9jBJM4DkQ7i6qHtjBJ3J2u0F8PFJ3okI', 'rede_teste', 'rede_teste@teste.com', '36182197099', 1);

-- Copiando estrutura para tabela rede_cuidar.profissional
CREATE TABLE IF NOT EXISTS `profissional` (
  `id_profissional` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `id_pessoa` int(10) unsigned NOT NULL,
  `endereco` varchar(200) NOT NULL,
  `numero` varchar(20) NOT NULL,
  `cidade` varchar(100) NOT NULL,
  `estado` char(2) NOT NULL,
  `cep` char(8) NOT NULL,
  `telefone` varchar(20) NOT NULL,
  `descricao` text NOT NULL,
  `inscricao_conselho` varchar(50) DEFAULT NULL,
  `status_verificacao` enum('PENDENTE','APROVADO','REJEITADO') NOT NULL DEFAULT 'PENDENTE',
  PRIMARY KEY (`id_profissional`),
  UNIQUE KEY `id_pessoa` (`id_pessoa`),
  CONSTRAINT `fk_profissional_pessoa` FOREIGN KEY (`id_pessoa`) REFERENCES `pessoa` (`id_pessoa`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copiando dados para a tabela rede_cuidar.profissional: ~0 rows (aproximadamente)
INSERT INTO `profissional` (`id_profissional`, `id_pessoa`, `endereco`, `numero`, `cidade`, `estado`, `cep`, `telefone`, `descricao`, `inscricao_conselho`, `status_verificacao`) VALUES
	(3, 41, 'rua Olivia', '22', 'Cajamar', 'SP', '00000222', '11987654321', 'Psicologa', '123456', 'PENDENTE');

-- Copiando estrutura para tabela rede_cuidar.rate_limit
CREATE TABLE IF NOT EXISTS `rate_limit` (
  `id_rate_limit` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(255) NOT NULL DEFAULT '',
  `tipo` varchar(20) NOT NULL,
  `data` datetime NOT NULL,
  PRIMARY KEY (`id_rate_limit`)
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Copiando dados para a tabela rede_cuidar.rate_limit: ~25 rows (aproximadamente)
INSERT INTO `rate_limit` (`id_rate_limit`, `email`, `tipo`, `data`) VALUES
	(1, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:11:35'),
	(2, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:11:46'),
	(3, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:11:51'),
	(4, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:12:26'),
	(5, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:12:31'),
	(6, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:12:35'),
	(7, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:20:19'),
	(8, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:20:53'),
	(9, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:37:21'),
	(10, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:37:26'),
	(11, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:37:29'),
	(12, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:37:31'),
	(13, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:37:33'),
	(14, 'jj.silva@example.com', 'LOGIN', '2026-10-02 20:37:35'),
	(15, 'ertwer@gmail.com', 'LOGIN', '2026-10-03 19:14:59'),
	(16, 'ertwer@gmail.com', 'LOGIN', '2026-10-03 19:15:01'),
	(17, 'ertwer@gmail.com', 'LOGIN', '2026-10-03 19:15:01'),
	(18, '234234@gmail.com', 'LOGIN', '2026-10-03 19:17:33'),
	(19, 'fabio@gmail.com', 'LOGIN', '2026-10-03 19:19:53'),
	(20, 'erwerw@gmail.com', 'LOGIN', '2026-10-03 19:25:25'),
	(21, '234234@gmail.com', 'LOGIN', '2026-10-03 19:28:10'),
	(22, '2342342@gmail.com', 'LOGIN', '2026-10-03 19:30:18'),
	(23, 'asdasda@gmail.com', 'LOGIN', '2026-10-03 19:38:21'),
	(24, 'joana@example.com', 'LOGIN', '2026-10-03 23:26:19'),
	(25, 'jj.silva@example.com', 'LOGIN', '2026-10-03 23:57:01'),
	(26, 'camilateste@gmail.com', 'LOGIN', '2026-10-04 14:41:55'),
	(27, 'camillateste4@gmail.com', 'LOGIN', '2026-10-04 14:52:25');

-- Copiando estrutura para tabela rede_cuidar.tipo_perfil
CREATE TABLE IF NOT EXISTS `tipo_perfil` (
  `id_tipo_perfil` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_tipo_perfil`),
  UNIQUE KEY `uk_tipo_perfil_nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copiando dados para a tabela rede_cuidar.tipo_perfil: ~8 rows (aproximadamente)
INSERT INTO `tipo_perfil` (`id_tipo_perfil`, `nome`, `ativo`) VALUES
	(1, 'Pessoa atípica', 1),
	(2, 'Mãe', 1),
	(3, 'Pai', 1),
	(4, 'Responsável', 1),
	(5, 'Familiar', 1),
	(6, 'Profissional', 1),
	(7, 'Educador', 1),
	(8, 'Instituição', 1);

-- Copiando estrutura para tabela rede_cuidar.tipo_pessoa
CREATE TABLE IF NOT EXISTS `tipo_pessoa` (
  `id_tipo_pessoa` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `nome` varchar(50) NOT NULL,
  `ativo` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id_tipo_pessoa`),
  UNIQUE KEY `uk_tipo_pessoa_nome` (`nome`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Copiando dados para a tabela rede_cuidar.tipo_pessoa: ~2 rows (aproximadamente)
INSERT INTO `tipo_pessoa` (`id_tipo_pessoa`, `nome`, `ativo`) VALUES
	(1, 'Pessoa Física', 1),
	(2, 'Pessoa Jurídica', 1);

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
