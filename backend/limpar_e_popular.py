"""
Script para limpar pacientes de teste e popular planos de saúde
"""
import sys
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal
from app.models.models import Paciente, PlanoSaude, Base

def limpar_pacientes_teste(db: Session):
    """Remove todos os pacientes com email contendo 'teste@'"""
    pacientes_teste = db.query(Paciente).filter(
        Paciente.email.like('%teste@%')
    ).all()
    
    if pacientes_teste:
        print(f"\n🗑️  Removendo {len(pacientes_teste)} paciente(s) de teste:")
        for paciente in pacientes_teste:
            print(f"   - {paciente.nome} ({paciente.email})")
            db.delete(paciente)
        
        db.commit()
        print(f"✅ {len(pacientes_teste)} paciente(s) de teste removido(s)")
    else:
        print("ℹ️  Nenhum paciente de teste encontrado")

def popular_planos_saude(db: Session):
    """Cria planos de saúde se não existirem"""
    planos_existentes = db.query(PlanoSaude).count()
    
    if planos_existentes > 0:
        print(f"\nℹ️  Já existem {planos_existentes} plano(s) de saúde cadastrado(s)")
        return
    
    planos = [
        PlanoSaude(
            nome="Unimed",
            cobertura_info="Cobertura completa incluindo consultas, exames e internações"
        ),
        PlanoSaude(
            nome="SulAmérica",
            cobertura_info="Plano completo com rede credenciada nacional"
        ),
        PlanoSaude(
            nome="Bradesco Saúde",
            cobertura_info="Plano com cobertura regional e nacional"
        ),
        PlanoSaude(
            nome="Amil",
            cobertura_info="Plano com ampla rede de hospitais e clínicas"
        ),
        PlanoSaude(
            nome="NotreDame Intermédica",
            cobertura_info="Cobertura completa com hospitais próprios"
        )
    ]
    
    print(f"\n➕ Adicionando {len(planos)} planos de saúde:")
    for plano in planos:
        db.add(plano)
        print(f"   - {plano.nome}")
    
    db.commit()
    print(f"✅ {len(planos)} planos de saúde adicionados com sucesso")

def main():
    print("=" * 60)
    print("🔧 Manutenção do Banco de Dados")
    print("=" * 60)
    
    db = SessionLocal()
    
    try:
        # Limpar pacientes de teste
        limpar_pacientes_teste(db)
        
        # Popular planos de saúde
        popular_planos_saude(db)
        
        print("\n" + "=" * 60)
        print("✅ Manutenção concluída com sucesso!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Erro durante manutenção: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()
