"""
Script para criar todas as tabelas no banco de dados
Execute: docker exec -it clinica_backend python create_tables.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
from app.models import *

def create_all_tables():
    print("🔨 Dropando e recriando todas as tabelas no banco de dados...")
    try:
        # Drop all tables first
        print("⚠️  Dropando todas as tabelas existentes...")
        Base.metadata.drop_all(bind=engine)
        print("✓ Tabelas dropadas")
        
        # Create all tables
        print("🔨 Criando tabelas...")
        Base.metadata.create_all(bind=engine)
        print("✅ Tabelas criadas com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        raise

if __name__ == "__main__":
    create_all_tables()
