#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script para corrigir encoding dos médicos"""
from app.database import SessionLocal
from app.models.models import Medico

def fix_encoding():
    db = SessionLocal()
    try:
        # Buscar o médico ID 1
        medico = db.query(Medico).filter(Medico.id_medico == 1).first()
        if medico:
            # Corrigir o nome com encoding correto (usando unicode escape)
            medico.nome = "Dr. Jo\u00e3o Silva"  # \u00e3 = ã
            db.commit()
            print(f"✅ Nome atualizado: {medico.nome}")
        else:
            print("❌ Médico não encontrado")
            
        # Verificar
        medico = db.query(Medico).filter(Medico.id_medico == 1).first()
        print(f"📋 Verificação: {medico.nome}")
        print(f"📋 Bytes: {medico.nome.encode('utf-8')}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    fix_encoding()
