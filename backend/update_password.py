#!/usr/bin/env python3
"""Script para atualizar senha de um paciente"""
import bcrypt
from app.database import SessionLocal
from app.models.models import Paciente

def update_password(email: str, new_password: str):
    db = SessionLocal()
    try:
        # Buscar paciente
        paciente = db.query(Paciente).filter(Paciente.email == email).first()
        if not paciente:
            print(f"❌ Paciente com email '{email}' não encontrado!")
            return
        
        # Gerar hash da nova senha
        hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
        
        # Atualizar senha
        paciente.senha_hash = hashed.decode('utf-8')
        db.commit()
        
        print(f"✅ Senha atualizada com sucesso para '{email}'!")
        print(f"   Nova senha: {new_password}")
        print(f"   Hash: {hashed.decode('utf-8')}")
        
    except Exception as e:
        print(f"❌ Erro ao atualizar senha: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_password("testeum@gmail.com", "Teste1234")
