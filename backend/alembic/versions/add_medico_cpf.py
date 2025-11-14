"""Adicionar campo CPF para médicos

Revision ID: add_medico_cpf
Revises: 
Create Date: 2025-11-01

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_medico_cpf'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna CPF na tabela medicos
    op.add_column('medicos', sa.Column('cpf', sa.String(length=14), nullable=True))
    
    # Criar índice único para CPF
    op.create_unique_constraint('medico_cpf_key', 'medicos', ['cpf'])
    
    # Criar índice para melhor performance
    op.create_index('ix_medicos_cpf', 'medicos', ['cpf'])


def downgrade():
    # Remover índice
    op.drop_index('ix_medicos_cpf', table_name='medicos')
    
    # Remover constraint
    op.drop_constraint('medico_cpf_key', 'medicos', type_='unique')
    
    # Remover coluna
    op.drop_column('medicos', 'cpf')
