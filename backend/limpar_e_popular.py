"""
Script para limpar e popular o banco de dados com dados de exemplo.
"""
import sys
from pathlib import Path
import logging
from datetime import date, time, datetime, timedelta

# Adicionar diretório raiz ao path
sys.path.append(str(Path(__file__).resolve().parent))

from sqlalchemy.orm import Session
from app.database import engine, SessionLocal, Base
from app.models.models import (
    Especialidade, PlanoSaude, Administrador, Medico, Paciente,
    HorarioTrabalho, Consulta, Observacao, BloqueioHorario, Relatorio
)
from app.utils.auth import get_password_hash

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def limpar_tabelas(db: Session):
    """Deleta todos os dados das tabelas na ordem correta para evitar problemas de FK."""
    tabelas_para_limpar = [
        Observacao, Consulta, HorarioTrabalho, BloqueioHorario, Relatorio,
        Paciente, Medico, Administrador, Especialidade, PlanoSaude
    ]
    
    logger.info("\n🗑️  Iniciando limpeza do banco de dados...")
    for tabela in tabelas_para_limpar:
        try:
            num_rows_deleted = db.query(tabela).delete()
            if num_rows_deleted > 0:
                logger.info(f"   - {num_rows_deleted} registros removidos de '{tabela.__tablename__}'")
        except Exception as e:
            logger.error(f"Erro ao limpar a tabela {tabela.__tablename__}: {e}")
            db.rollback()
            return

    db.commit()
    logger.info("✅ Limpeza concluída.")

def popular_especialidades(db: Session):
    """Popula a tabela de especialidades."""
    if db.query(Especialidade).first():
        logger.info("ℹ️  Especialidades já existem.")
        return

    especialidades = ["Cardiologia", "Dermatologia", "Ortopedia", "Pediatria", "Ginecologia"]
    logger.info("\n➕ Populando Especialidades...")
    for nome in especialidades:
        db.add(Especialidade(nome=nome))
        logger.info(f"   - {nome}")
    db.commit()

def popular_planos_saude(db: Session):
    """Popula a tabela de planos de saúde."""
    if db.query(PlanoSaude).first():
        logger.info("ℹ️  Planos de Saúde já existem.")
        return

    planos = [
        {"nome": "Unimed", "cobertura_info": "Cobertura completa nacional."},
        {"nome": "SulAmérica", "cobertura_info": "Plano executivo com ampla rede."},
        {"nome": "Bradesco Saúde", "cobertura_info": "Cobertura empresarial e individual."},
        {"nome": "Amil", "cobertura_info": "Planos com e sem coparticipação."},
    ]
    logger.info("\n➕ Populando Planos de Saúde...")
    for plano in planos:
        db.add(PlanoSaude(**plano))
        logger.info(f"   - {plano['nome']}")
    db.commit()

def popular_administradores(db: Session):
    """Popula a tabela de administradores."""
    if db.query(Administrador).first():
        logger.info("ℹ️  Administradores já existem.")
        return

    admin = Administrador(
        nome="Admin Padrão",
        email="admin@saude.com",
        senha_hash=get_password_hash("admin123"),
        papel="Gerente"
    )
    logger.info("\n➕ Populando Administradores...")
    db.add(admin)
    logger.info("   - Admin Padrão (admin@saude.com / admin123)")
    db.commit()

def popular_medicos(db: Session):
    """Popula a tabela de médicos."""
    if db.query(Medico).first():
        logger.info("ℹ️  Médicos já existem.")
        return

    especialidades = {e.nome: e.id_especialidade for e in db.query(Especialidade).all()}
    medicos = [
        {"nome": "Dr. Carlos Andrade", "cpf": "11122233344", "email": "carlos.med@saude.com", "senha": "medico123", "crm": "CRM/SP 12345", "id_especialidade_fk": especialidades["Cardiologia"]},
        {"nome": "Dra. Ana Oliveira", "cpf": "22233344455", "email": "ana.med@saude.com", "senha": "medico123", "crm": "CRM/SP 12346", "id_especialidade_fk": especialidades["Dermatologia"]},
        {"nome": "Dr. Pedro Santos", "cpf": "33344455566", "email": "pedro.med@saude.com", "senha": "medico123", "crm": "CRM/RJ 54321", "id_especialidade_fk": especialidades["Ortopedia"]},
    ]
    logger.info("\n➕ Populando Médicos...")
    for med in medicos:
        senha = med.pop("senha")
        db.add(Medico(**med, senha_hash=get_password_hash(senha)))
        logger.info(f"   - {med['nome']} ({med['email']} / medico123)")
    db.commit()

def popular_pacientes(db: Session):
    """Popula a tabela de pacientes."""
    if db.query(Paciente).first():
        logger.info("ℹ️  Pacientes já existem.")
        return

    planos = {p.nome: p.id_plano_saude for p in db.query(PlanoSaude).all()}
    pacientes = [
        {"nome": "Maria Silva", "cpf": "44455566677", "email": "maria.paciente@email.com", "senha": "paciente123", "telefone": "11987654321", "data_nascimento": date(1990, 5, 15), "id_plano_saude_fk": planos["Unimed"]},
        {"nome": "João Pereira", "cpf": "55566677788", "email": "joao.paciente@email.com", "senha": "paciente123", "telefone": "21912345678", "data_nascimento": date(1985, 10, 20), "id_plano_saude_fk": None},
        {"nome": "Beatriz Costa", "cpf": "66677788899", "email": "beatriz.paciente@email.com", "senha": "paciente123", "telefone": "48988776655", "data_nascimento": date(2000, 1, 30), "id_plano_saude_fk": planos["Amil"]},
    ]
    logger.info("\n➕ Populando Pacientes...")
    for pac in pacientes:
        senha = pac.pop("senha")
        db.add(Paciente(**pac, senha_hash=get_password_hash(senha)))
        logger.info(f"   - {pac['nome']} ({pac['email']} / paciente123)")
    db.commit()
    
def popular_horarios_trabalho(db: Session):
    """Popula horários de trabalho para os médicos."""
    if db.query(HorarioTrabalho).first():
        logger.info("ℹ️  Horários de Trabalho já existem.")
        return

    medicos = db.query(Medico).all()
    logger.info("\n➕ Populando Horários de Trabalho...")
    for medico in medicos:
        # Segunda a Sexta, das 09:00 às 18:00
        for dia in range(5):
            ht = HorarioTrabalho(
                dia_semana=dia,
                hora_inicio=time(9, 0),
                hora_fim=time(18, 0),
                id_medico_fk=medico.id_medico
            )
            db.add(ht)
        logger.info(f"   - Horários para {medico.nome} (Seg-Sex, 09:00-18:00)")
    db.commit()

def popular_consultas(db: Session):
    """Popula algumas consultas de exemplo."""
    if db.query(Consulta).first():
        logger.info("ℹ️  Consultas já existem.")
        return

    pacientes = db.query(Paciente).all()
    medicos = db.query(Medico).all()

    if not pacientes or not medicos:
        logger.warning("⚠️ Não foi possível popular consultas pois não há pacientes ou médicos.")
        return

    consultas = [
        # Consulta passada
        {"id_paciente_fk": pacientes[0].id_paciente, "id_medico_fk": medicos[0].id_medico, "data_hora_inicio": datetime.now() - timedelta(days=7, hours=3), "status": "realizada"},
        # Consulta futura
        {"id_paciente_fk": pacientes[1].id_paciente, "id_medico_fk": medicos[1].id_medico, "data_hora_inicio": datetime.now() + timedelta(days=3, hours=2), "status": "agendada"},
        # Consulta futura para o mesmo paciente
        {"id_paciente_fk": pacientes[0].id_paciente, "id_medico_fk": medicos[2].id_medico, "data_hora_inicio": datetime.now() + timedelta(days=10, hours=4), "status": "agendada"},
    ]
    logger.info("\n➕ Populando Consultas de Exemplo...")
    for c in consultas:
        c["data_hora_fim"] = c["data_hora_inicio"] + timedelta(minutes=30)
        db.add(Consulta(**c))
        logger.info(f"   - Consulta para Paciente ID {c['id_paciente_fk']} com Médico ID {c['id_medico_fk']} em {c['data_hora_inicio'].strftime('%d/%m/%Y %H:%M')}")
    db.commit()


def main():
    logger.info("=" * 60)
    logger.info("🔧 Script de Limpeza e Povoamento do Banco de Dados")
    logger.info("=" * 60)
    
    db = SessionLocal()
    
    try:
        # 1. Limpar tabelas
        limpar_tabelas(db)
        
        # 2. Popular tabelas
        popular_especialidades(db)
        popular_planos_saude(db)
        popular_administradores(db)
        popular_medicos(db)
        popular_pacientes(db)
        popular_horarios_trabalho(db)
        popular_consultas(db)
        
        logger.info("\n" + "=" * 60)
        logger.info("✅ Processo concluído com sucesso!")
        logger.info("=" * 60 + "\n")
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante o processo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine) # Garante que as tabelas existem
    main()
