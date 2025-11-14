"""
Script para criar banco PostgreSQL e popular com dados iniciais
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import create_engine, text
from app.config import settings
from app.models.models import Base
from app.database import SessionLocal
from app.utils.auth import get_password_hash
from app.models.models import (
    Especialidade, PlanoSaude, Administrador, Medico, Paciente,
    HorarioTrabalho, Consulta
)
from datetime import datetime, time, timedelta

def criar_banco_postgres():
    """Cria o banco de dados PostgreSQL se não existir"""
    print("🔧 Verificando banco PostgreSQL...")
    
    # Tentar conectar diretamente ao banco (pode já existir via Docker)
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Banco '{settings.POSTGRES_DB}' já existe e está acessível!")
        return
    except Exception as e:
        print(f"⚠️  Banco não acessível: {e}")
    
    # Se não conseguiu conectar, tentar criar
    print("🔧 Tentando criar banco PostgreSQL...")
    postgres_url = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/postgres"
    engine = create_engine(postgres_url, isolation_level="AUTOCOMMIT")
    
    try:
        with engine.connect() as conn:
            # Verificar se banco existe
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{settings.POSTGRES_DB}'"))
            exists = result.fetchone()
            
            if not exists:
                conn.execute(text(f"CREATE DATABASE {settings.POSTGRES_DB}"))
                print(f"✅ Banco '{settings.POSTGRES_DB}' criado!")
            else:
                print(f"ℹ️  Banco '{settings.POSTGRES_DB}' já existe")
    except Exception as e:
        print(f"❌ Erro ao criar banco: {e}")
        print("\n⚠️  Continuando mesmo assim (banco pode já existir via Docker)...")
    finally:
        engine.dispose()

def criar_tabelas():
    """Cria todas as tabelas"""
    print("\n📦 Criando tabelas...")
    from app.database import engine
    Base.metadata.drop_all(bind=engine)  # Limpar tabelas existentes
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas!")

def popular_dados():
    """Popula o banco com dados iniciais"""
    print("\n🌱 Populando dados...")
    db = SessionLocal()
    
    try:
        # Especialidades
        especialidades = [
            Especialidade(nome="Cardiologia"),
            Especialidade(nome="Ortopedia"),
            Especialidade(nome="Pediatria")
        ]
        for esp in especialidades:
            db.add(esp)
        db.commit()
        print(f"✅ {len(especialidades)} especialidades")
        
        # Planos de Saúde
        planos = [
            PlanoSaude(nome="Unimed", cobertura_info="Cobertura completa"),
            PlanoSaude(nome="SulAmérica", cobertura_info="Plano nacional")
        ]
        for plano in planos:
            db.add(plano)
        db.commit()
        print(f"✅ {len(planos)} planos")
        
        # Administrador
        admin = Administrador(
            nome="Administrador Sistema",
            email="admin@clinica.com",
            senha_hash=get_password_hash("admin123"),
            papel="Gerente Geral"
        )
        db.add(admin)
        db.commit()
        print("✅ Admin: admin@clinica.com / admin123")
        
        # Médicos
        medico1 = Medico(
            nome="Dr. João Silva",
            cpf="11111111111",
            email="joao@clinica.com",
            senha_hash=get_password_hash("medico123"),
            crm="CRM-12345",
            id_especialidade_fk=1
        )
        medico2 = Medico(
            nome="Dra. Maria Santos",
            cpf="22222222222",
            email="maria@clinica.com",
            senha_hash=get_password_hash("medico123"),
            crm="CRM-67890",
            id_especialidade_fk=2
        )
        db.add(medico1)
        db.add(medico2)
        db.commit()
        print("✅ 2 médicos / senha: medico123")
        
        # Horários de trabalho
        dias_semana = [0, 1, 2, 3, 4]  # Segunda a sexta
        for dia in dias_semana:
            horario1 = HorarioTrabalho(
                id_medico_fk=medico1.id_medico,
                dia_semana=dia,
                hora_inicio=time(8, 0),
                hora_fim=time(12, 0)
            )
            horario2 = HorarioTrabalho(
                id_medico_fk=medico1.id_medico,
                dia_semana=dia,
                hora_inicio=time(14, 0),
                hora_fim=time(18, 0)
            )
            db.add(horario1)
            db.add(horario2)
        db.commit()
        print("✅ 10 horários de trabalho")
        
        # Pacientes
        paciente1 = Paciente(
            nome="Carlos Souza",
            cpf="33333333333",
            email="carlos@email.com",
            senha_hash=get_password_hash("paciente123"),
            telefone="47999999999",
            data_nascimento=datetime(1990, 5, 15).date(),
            esta_bloqueado=False,
            id_plano_saude_fk=1
        )
        paciente2 = Paciente(
            nome="Ana Costa",
            cpf="44444444444",
            email="ana@email.com",
            senha_hash=get_password_hash("paciente123"),
            telefone="47988888888",
            data_nascimento=datetime(1985, 8, 20).date(),
            esta_bloqueado=False,
            id_plano_saude_fk=None
        )
        db.add(paciente1)
        db.add(paciente2)
        db.commit()
        print("✅ 2 pacientes / senha: paciente123")
        
        # Consultas
        amanha = datetime.now() + timedelta(days=1)
        amanha = amanha.replace(hour=10, minute=0, second=0, microsecond=0)
        
        consulta1 = Consulta(
            id_paciente_fk=paciente1.id_paciente,
            id_medico_fk=medico1.id_medico,
            data_hora=amanha,
            status="Agendada",
            tipo="Consulta"
        )
        db.add(consulta1)
        db.commit()
        print("✅ 1 consulta agendada")
        
        print("\n✅ BANCO POSTGRES POPULADO!")
        print("\n📝 CREDENCIAIS:")
        print("   Admin: admin@clinica.com / admin123")
        print("   Médico: joao@clinica.com / medico123")
        print("   Paciente: carlos@email.com / paciente123")
        
    except Exception as e:
        print(f"❌ Erro ao popular dados: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    print("=" * 60)
    print("🐘 MIGRAÇÃO PARA POSTGRESQL")
    print("=" * 60)
    
    try:
        criar_banco_postgres()
        criar_tabelas()
        popular_dados()
        
        print("\n" + "=" * 60)
        print("✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("=" * 60)
        print("\n💡 Iniciar servidor: uvicorn app.main:app --reload")
        print("💡 API Docs: http://localhost:8000/docs\n")
        
    except Exception as e:
        print(f"\n❌ Erro na migração: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
