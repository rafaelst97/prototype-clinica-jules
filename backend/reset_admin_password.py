"""
Script para resetar senha do administrador
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.utils.auth import get_password_hash
from app.config import settings

# Criar engine
engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def reset_admin_password():
    db = SessionLocal()
    try:
        # Gerar novo hash
        new_hash = get_password_hash('admin123')
        print(f"Novo hash gerado: {new_hash}")
        
        # Atualizar no banco
        result = db.execute(
            text("UPDATE administrador SET senha_hash = :hash WHERE email = 'admin@clinica.com'"),
            {"hash": new_hash}
        )
        db.commit()
        
        print(f"✅ Senha do administrador atualizada com sucesso!")
        print(f"   Email: admin@clinica.com")
        print(f"   Senha: admin123")
        
        # Verificar
        admin = db.execute(text("SELECT email, senha_hash FROM administrador WHERE email = 'admin@clinica.com'")).first()
        print(f"\n   Hash no banco: {admin[1][:50]}...")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_admin_password()
