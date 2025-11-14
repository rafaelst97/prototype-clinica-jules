"""Add Observacao and Relatorio tables and update Paciente

Revision ID: 002
Revises: 001
Create Date: 2025-10-26

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar coluna faltas_consecutivas na tabela pacientes
    op.add_column('pacientes', sa.Column('faltas_consecutivas', sa.Integer(), nullable=False, server_default='0'))
    
    # Criar tabela observacoes
    op.create_table('observacoes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('consulta_id', sa.Integer(), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=False),
        sa.Column('data_criacao', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['consulta_id'], ['consultas.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('consulta_id')
    )
    op.create_index(op.f('ix_observacoes_id'), 'observacoes', ['id'], unique=False)
    
    # Criar tabela relatorios
    op.create_table('relatorios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('tipo', sa.String(length=100), nullable=False),
        sa.Column('data_geracao', sa.DateTime(), nullable=True),
        sa.Column('dados_resultado', sa.Text(), nullable=True),
        sa.Column('parametros', sa.Text(), nullable=True),
        sa.Column('arquivo_path', sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(['admin_id'], ['admins.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_relatorios_id'), 'relatorios', ['id'], unique=False)
    
    # Remover colunas antigas de observacoes da tabela consultas (se existirem)
    # Nota: As colunas observacoes e observacoes_medico não serão removidas para manter compatibilidade
    # mas a nova estrutura usa a tabela observacoes separada


def downgrade():
    # Remover tabelas
    op.drop_index(op.f('ix_relatorios_id'), table_name='relatorios')
    op.drop_table('relatorios')
    
    op.drop_index(op.f('ix_observacoes_id'), table_name='observacoes')
    op.drop_table('observacoes')
    
    # Remover coluna faltas_consecutivas
    op.drop_column('pacientes', 'faltas_consecutivas')
