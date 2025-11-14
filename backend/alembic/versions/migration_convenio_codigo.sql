-- Migração: Renomear coluna cnpj para codigo na tabela convenios
-- Data: 2025-10-26

-- Adicionar nova coluna codigo
ALTER TABLE convenios ADD COLUMN IF NOT EXISTS codigo VARCHAR(20);

-- Copiar dados de cnpj para codigo (se houver dados)
UPDATE convenios SET codigo = cnpj WHERE cnpj IS NOT NULL;

-- Se não houver dados em cnpj, gerar códigos automáticos
UPDATE convenios SET codigo = 'CONV-' || LPAD(id::text, 3, '0') WHERE codigo IS NULL;

-- Adicionar constraint de NOT NULL e UNIQUE
ALTER TABLE convenios ALTER COLUMN codigo SET NOT NULL;
ALTER TABLE convenios ADD CONSTRAINT convenios_codigo_key UNIQUE (codigo);

-- Remover coluna cnpj antiga
ALTER TABLE convenios DROP COLUMN IF EXISTS cnpj;

-- Verificar resultado
SELECT id, nome, codigo, telefone, email, ativo FROM convenios;
