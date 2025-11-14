"""
Script de Setup Simplificado - SQLite (Desenvolvimento Rápido)
Conforme estrutura MER exata
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['APP_ENV'] = 'test'

from app.database import engine, SessionLocal
from app.models.models import Base, Especialidade, PlanoSaude, Administrador, Medico, Paciente, HorarioTrabalho, Consulta
from datetime import datetime, timedelta
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_tabelas():
    print("📦 Criando tabelas...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")

def popular_dados():
    db = SessionLocal()
    try:
        print("\n🌱 Populando dados...")
        
        # Especialidades
        esp = [
            Especialidade(nome="Cardiologia"),
            Especialidade(nome="Dermatologia"),
            Especialidade(nome="Ortopedia"),
        ]
        db.add_all(esp)
        db.commit()
        print(f"✅ {len(esp)} especialidades")
        
        # Planos
        planos = [
            PlanoSaude(nome="Unimed", cobertura_info="Cobertura completa"),
            PlanoSaude(nome="Particular", cobertura_info="Sem plano")
        ]
        db.add_all(planos)
        db.commit()
        print(f"✅ {len(planos)} planos")
        
        # Admin (campos corretos: nome, email, senha_hash, papel)
        admin = Administrador(
            nome="Admin Sistema",
            email="admin@clinica.com",
            senha_hash=pwd_context.hash("admin123"),
            papel="Administrador Geral"
        )
        db.add(admin)
        db.commit()
        print("✅ Admin: admin@clinica.com / admin123")
        
        # Médicos (campos corretos conforme MER)
        medicos = [
            Medico(
                nome="Dr. João Silva",
                cpf="11111111111",
                email="joao@clinica.com",
                senha_hash=pwd_context.hash("medico123"),
                crm="12345-SC",
                id_especialidade_fk=1
            ),
            Medico(
                nome="Dra. Maria Santos",
                cpf="22222222222",
                email="maria@clinica.com",
                senha_hash=pwd_context.hash("medico123"),
                crm="23456-SC",
                id_especialidade_fk=2
            )
        ]
        db.add_all(medicos)
        db.commit()
        print(f"✅ {len(medicos)} médicos / senha: medico123")
        
        # Horários
        from datetime import time
        horarios = []
        for med in medicos:
            for dia in range(1, 6):  # Seg-Sex
                horarios.append(HorarioTrabalho(
                    id_medico_fk=med.id_medico,
                    dia_semana=dia,
                    hora_inicio=time(9, 0),  # Objeto time do Python
                    hora_fim=time(17, 0)
                ))
        db.add_all(horarios)
        db.commit()
        print(f"✅ {len(horarios)} horários")
        
        # Pacientes (campos corretos: nome, cpf, data_nascimento, telefone, email, senha_hash, id_plano_saude_fk, esta_bloqueado)
        from datetime import date
        pacientes = [
            Paciente(
                nome="Carlos Souza",
                cpf="12345678901",
                data_nascimento=date(1985, 5, 15),
                telefone="47-97777-0001",
                email="carlos@email.com",
                senha_hash=pwd_context.hash("paciente123"),
                id_plano_saude_fk=1,
                esta_bloqueado=False
            ),
            Paciente(
                nome="Juliana Alves",
                cpf="23456789012",
                data_nascimento=date(1990, 8, 20),
                telefone="47-97777-0002",
                email="juliana@email.com",
                senha_hash=pwd_context.hash("paciente123"),
                id_plano_saude_fk=2,
                esta_bloqueado=False
            )
        ]
        db.add_all(pacientes)
        db.commit()
        print(f"✅ {len(pacientes)} pacientes / senha: paciente123")
        
        # Consultas
        hoje = datetime.now()
        consultas = [
            # Passada
            Consulta(
                id_paciente_fk=1,
                id_medico_fk=1,
                data_hora=hoje - timedelta(days=7),
                tipo="Consulta",
                status="Realizada"
            ),
            # Futuras
            Consulta(
                id_paciente_fk=1,
                id_medico_fk=1,
                data_hora=hoje + timedelta(days=1, hours=10),
                tipo="Consulta",
                status="Agendada"
            ),
            Consulta(
                id_paciente_fk=2,
                id_medico_fk=2,
                data_hora=hoje + timedelta(days=2, hours=14),
                tipo="Consulta",
                status="Agendada"
            )
        ]
        db.add_all(consultas)
        db.commit()
        print(f"✅ {len(consultas)} consultas")
        
        print("\n✅ BANCO POPULADO!")
        print("\n📝 CREDENCIAIS:")
        print("   Admin: admin@clinica.com / admin123")
        print("   Médico: joao@clinica.com / medico123")
        print("   Paciente: carlos@email.com / paciente123")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 50)
    print("🏥 SETUP SQLite (Dev Rápido)")
    print("=" * 50)
    criar_tabelas()
    popular_dados()
    print("\n💡 Iniciar: uvicorn app.main:app --reload")
    print("💡 API Docs: http://localhost:8000/docs\n")
