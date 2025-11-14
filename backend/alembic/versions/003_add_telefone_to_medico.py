"""add telefone to medico

Revision ID: 003
Revises: 002
Create Date: 2025-11-06 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna telefone na tabela medico
    op.add_column('medico', sa.Column('telefone', sa.String(length=20), nullable=True))


def downgrade():
    # Remover coluna telefone da tabela medico
    op.drop_column('medico', 'telefone')
