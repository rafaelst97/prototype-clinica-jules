"""
Script de Setup com SQLite (Temporário para Desenvolvimento)
Para produção, usar PostgreSQL conforme SETUP_POSTGRESQL.md
"""
import sys
import os

# Adicionar o diretório pai ao path para imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Forçar uso de SQLite temporariamente
os.environ['APP_ENV'] = 'test'

from app.database import engine, SessionLocal
from app.models.models import (
    Base, Especialidade, PlanoSaude, Administrador,
    Medico, Paciente, HorarioTrabalho, Consulta, Observacao
)
from datetime import datetime, date, timedelta
from passlib.context import CryptContext

# Configurar hash de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def criar_tabelas():
    """Cria todas as tabelas no banco de dados"""
    print("📦 Criando tabelas no banco de dados SQLite...")
    print(f"   📍 Arquivo: {engine.url}")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

def popular_dados_iniciais():
    """Popula o banco com dados de teste"""
    db = SessionLocal()
    
    try:
        print("\n🌱 Populando dados iniciais...")
        
        # 1. ESPECIALIDADES
        print("  → Criando especialidades...")
        especialidades = [
            Especialidade(nome="Cardiologia"),
            Especialidade(nome="Dermatologia"),
            Especialidade(nome="Ortopedia"),
            Especialidade(nome="Pediatria"),
            Especialidade(nome="Ginecologia"),
        ]
        db.add_all(especialidades)
        db.commit()
        print(f"  ✅ {len(especialidades)} especialidades")
        
        # 2. PLANOS DE SAÚDE
        print("  → Criando planos de saúde...")
        planos = [
            PlanoSaude(nome="Unimed", cobertura_info="Cobertura empresarial completa"),
            PlanoSaude(nome="Bradesco Saúde", cobertura_info="Cobertura individual"),
            PlanoSaude(nome="Particular", cobertura_info="Atendimento particular sem plano")
        ]
        db.add_all(planos)
        db.commit()
        print(f"  ✅ {len(planos)} planos de saúde")
        
        # 3. ADMINISTRADOR
        print("  → Criando administrador...")
        admin = Administrador(
            nome="Admin Sistema",
            cpf="00000000000",
            telefone="47-99999-0000",
            email="admin@clinica.com",
            senha=pwd_context.hash("admin123"),
            cargo="Administrador"
        )
        db.add(admin)
        db.commit()
        print("  ✅ Admin: admin@clinica.com / admin123")
        
        # 4. MÉDICOS
        print("  → Criando médicos...")
        medicos = [
            Medico(
                nome="Dr. João Silva",
                crm="12345-SC",
                cpf="11111111111",
                telefone="47-98888-0001",
                email="joao.silva@clinica.com",
                senha=pwd_context.hash("medico123"),
                id_especialidade_fk=1
            ),
            Medico(
                nome="Dra. Maria Santos",
                crm="23456-SC",
                cpf="22222222222",
                telefone="47-98888-0002",
                email="maria.santos@clinica.com",
                senha=pwd_context.hash("medico123"),
                id_especialidade_fk=2
            )
        ]
        db.add_all(medicos)
        db.commit()
        print(f"  ✅ {len(medicos)} médicos / senha: medico123")
        
        # 5. HORÁRIOS
        print("  → Criando horários...")
        horarios = []
        for medico in medicos:
            for dia in range(1, 6):  # Segunda a Sexta
                horarios.append(HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia,
                    hora_inicio="08:00:00",
                    hora_fim="12:00:00",
                    duracao_consulta=30
                ))
                horarios.append(HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia,
                    hora_inicio="14:00:00",
                    hora_fim="18:00:00",
                    duracao_consulta=30
                ))
        db.add_all(horarios)
        db.commit()
        print(f"  ✅ {len(horarios)} horários")
        
        # 6. PACIENTES
        print("  → Criando pacientes...")
        pacientes = [
            Paciente(
                nome="Carlos Souza",
                cpf="12345678901",
                data_nascimento=date(1985, 5, 15),
                telefone="47-97777-0001",
                email="carlos@email.com",
                senha=pwd_context.hash("paciente123"),
                endereco="Rua A, 100",
                id_plano_saude_fk=1,
                esta_bloqueado=False,
                faltas_consecutivas=0
            ),
            Paciente(
                nome="Juliana Alves",
                cpf="23456789012",
                data_nascimento=date(1990, 8, 20),
                telefone="47-97777-0002",
                email="juliana@email.com",
                senha=pwd_context.hash("paciente123"),
                endereco="Rua B, 200",
                id_plano_saude_fk=2,
                esta_bloqueado=False,
                faltas_consecutivas=0
            ),
            Paciente(
                nome="Paciente Bloqueado",
                cpf="99999999999",
                data_nascimento=date(1988, 3, 10),
                telefone="47-97777-9999",
                email="bloqueado@email.com",
                senha=pwd_context.hash("paciente123"),
                endereco="Rua C, 300",
                id_plano_saude_fk=3,
                esta_bloqueado=True,
                faltas_consecutivas=3
            )
        ]
        db.add_all(pacientes)
        db.commit()
        print(f"  ✅ {len(pacientes)} pacientes / senha: paciente123")
        
        # 7. CONSULTAS
        print("  → Criando consultas...")
        hoje = datetime.now()
        consultas = []
        
        # Consulta passada (realizada)
        consultas.append(Consulta(
            id_paciente_fk=1,
            id_medico_fk=1,
            data_hora_inicio=hoje - timedelta(days=7),
            data_hora_fim=hoje - timedelta(days=7) + timedelta(minutes=30),
            status="realizada"
        ))
        
        # Consultas futuras
        for i in range(3):
            consultas.append(Consulta(
                id_paciente_fk=(i % 2) + 1,
                id_medico_fk=(i % 2) + 1,
                data_hora_inicio=hoje + timedelta(days=i+1, hours=10),
                data_hora_fim=hoje + timedelta(days=i+1, hours=10, minutes=30),
                status="agendada"
            ))
        
        db.add_all(consultas)
        db.commit()
        print(f"  ✅ {len(consultas)} consultas")
        
        print("\n✅ Banco SQLite populado com sucesso!")
        print("\n📝 CREDENCIAIS:")
        print("   Admin: admin@clinica.com / admin123")
        print("   Médico: joao.silva@clinica.com / medico123")
        print("   Paciente: carlos@email.com / paciente123")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def main():
    print("=" * 60)
    print("🏥 SETUP RÁPIDO - SQLite (Desenvolvimento)")
    print("=" * 60)
    print("⚠️  Para produção, use PostgreSQL (veja SETUP_POSTGRESQL.md)")
    print()
    
    try:
        criar_tabelas()
        popular_dados_iniciais()
        
        print("\n" + "=" * 60)
        print("✅ PRONTO!")
        print("=" * 60)
        print("\n💡 Iniciar servidor:")
        print("   uvicorn app.main:app --reload")
        print("\n💡 Testar API:")
        print("   http://localhost:8000/docs")
        print()
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
