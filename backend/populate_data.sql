-- Popular banco com dados iniciais

-- Limpar dados existentes
TRUNCATE TABLE consulta CASCADE;
TRUNCATE TABLE horario_trabalho CASCADE;
TRUNCATE TABLE paciente CASCADE;
TRUNCATE TABLE medico CASCADE;
TRUNCATE TABLE administrador CASCADE;
TRUNCATE TABLE plano_saude CASCADE;
TRUNCATE TABLE especialidade CASCADE;

-- Resetar sequences
ALTER SEQUENCE especialidade_id_especialidade_seq RESTART WITH 1;
ALTER SEQUENCE plano_saude_id_plano_saude_seq RESTART WITH 1;
ALTER SEQUENCE administrador_id_administrador_seq RESTART WITH 1;
ALTER SEQUENCE medico_id_medico_seq RESTART WITH 1;
ALTER SEQUENCE paciente_id_paciente_seq RESTART WITH 1;
ALTER SEQUENCE horario_trabalho_id_horario_trabalho_seq RESTART WITH 1;
ALTER SEQUENCE consulta_id_consulta_seq RESTART WITH 1;

-- Inserir especialidades
INSERT INTO especialidade (nome) VALUES
('Cardiologia'),
('Ortopedia'),
('Pediatria');

-- Inserir planos de saúde
INSERT INTO plano_saude (nome, cobertura_info) VALUES
('Unimed', 'Cobertura completa nacional'),
('SulAmérica', 'Plano nacional com cobertura internacional'),
('Bradesco Saúde', 'Cobertura nacional'),
('Amil', 'Rede credenciada nacional'),
('NotreDame Intermédica', 'Cobertura regional Sul'),
('Particular', 'Atendimento particular sem convênio');

-- Inserir administrador (senha: admin123)
INSERT INTO administrador (nome, email, senha_hash, papel) VALUES
('Administrador Sistema', 'admin@clinica.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFq8qGPuW', 'Gerente Geral');

-- Inserir médicos (senha: medico123)
INSERT INTO medico (nome, cpf, email, senha_hash, crm, id_especialidade_fk) VALUES
('Dr. João Silva', '11111111111', 'joao@clinica.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFq8qGPuW', 'CRM-12345', 1),
('Dra. Maria Santos', '22222222222', 'maria@clinica.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFq8qGPuW', 'CRM-67890', 2);

-- Inserir horários de trabalho (Segunda a Sexta, 8h-12h e 14h-18h)
INSERT INTO horario_trabalho (id_medico_fk, dia_semana, hora_inicio, hora_fim) VALUES
-- Dr. João (id_medico = 1)
(1, 0, '08:00:00', '12:00:00'),
(1, 0, '14:00:00', '18:00:00'),
(1, 1, '08:00:00', '12:00:00'),
(1, 1, '14:00:00', '18:00:00'),
(1, 2, '08:00:00', '12:00:00'),
(1, 2, '14:00:00', '18:00:00'),
(1, 3, '08:00:00', '12:00:00'),
(1, 3, '14:00:00', '18:00:00'),
(1, 4, '08:00:00', '12:00:00'),
(1, 4, '14:00:00', '18:00:00'),
-- Dra. Maria (id_medico = 2)
(2, 0, '08:00:00', '12:00:00'),
(2, 0, '14:00:00', '18:00:00'),
(2, 1, '08:00:00', '12:00:00'),
(2, 1, '14:00:00', '18:00:00'),
(2, 2, '08:00:00', '12:00:00'),
(2, 2, '14:00:00', '18:00:00'),
(2, 3, '08:00:00', '12:00:00'),
(2, 3, '14:00:00', '18:00:00'),
(2, 4, '08:00:00', '12:00:00'),
(2, 4, '14:00:00', '18:00:00');

-- Inserir pacientes de teste (senha: paciente123)
INSERT INTO paciente (nome, cpf, email, senha_hash, telefone, data_nascimento, esta_bloqueado, id_plano_saude_fk) VALUES
('Carlos Souza', '33333333333', 'carlos@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFq8qGPuW', '47999999999', '1990-05-15', false, 1),
('Ana Costa', '44444444444', 'ana@email.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYIFq8qGPuW', '47988888888', '1985-08-20', false, NULL);

-- Confirmar
SELECT 'Especialidades:', COUNT(*) FROM especialidade;
SELECT 'Planos de Saúde:', COUNT(*) FROM plano_saude;
SELECT 'Administradores:', COUNT(*) FROM administrador;
SELECT 'Médicos:', COUNT(*) FROM medico;
SELECT 'Horários:', COUNT(*) FROM horario_trabalho;
SELECT 'Pacientes:', COUNT(*) FROM paciente;
