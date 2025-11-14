-- Script SQL para configurar PostgreSQL
-- Execute com: psql -U postgres -f setup_postgres.sql

-- Criar usuário
CREATE USER clinica_user WITH PASSWORD 'clinica_pass';

-- Criar banco
CREATE DATABASE clinica_saude OWNER clinica_user;

-- Conceder permissões
GRANT ALL PRIVILEGES ON DATABASE clinica_saude TO clinica_user;

-- Conectar ao banco e conceder permissões no schema public
\c clinica_saude
GRANT ALL ON SCHEMA public TO clinica_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO clinica_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO clinica_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO clinica_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO clinica_user;
