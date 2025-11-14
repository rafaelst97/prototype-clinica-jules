"""
Script para popular o banco com dados de teste: horários e consultas
"""
import sys
import os
from datetime import datetime, timedelta, time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Adicionar o diretório app ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.models.models import Medico, Paciente, HorarioDisponivel, Consulta, StatusConsulta
from app.config import settings

# Usar a configuração do settings que já tem a URL correta
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def popular_horarios(db):
    """Criar horários disponíveis para os médicos (padrão semanal)"""
    print("\n📅 Criando horários disponíveis...")
    
    medicos = db.query(Medico).all()
    if not medicos:
        print("❌ Nenhum médico encontrado!")
        return 0
    
    print(f"   ℹ️  {len(medicos)} médicos encontrados")
    
    horarios_criados = 0
    
    for medico in medicos:
        print(f"   → Criando horários para médico ID {medico.id}")
        
        # Criar horários de segunda a sexta (0-4)
        for dia_semana in range(5):  # 0=Segunda, 4=Sexta
            # Horários das 8h às 17h (intervalo de 30min)
            hora_inicio = time(8, 0)
            
            for hora_offset in range(0, 9 * 60, 30):  # 9 horas, intervalo de 30min
                minutos_total = hora_offset
                horas = minutos_total // 60
                minutos = minutos_total % 60
                
                hora_inicio_slot = time(8 + horas, minutos)
                hora_fim_slot = time(8 + horas, minutos + 30) if minutos + 30 < 60 else time(8 + horas + 1, 0)
                
                # Verificar se já existe
                existe = db.query(HorarioDisponivel).filter(
                    HorarioDisponivel.medico_id == medico.id,
                    HorarioDisponivel.dia_semana == dia_semana,
                    HorarioDisponivel.hora_inicio == hora_inicio_slot
                ).first()
                
                if not existe:
                    horario = HorarioDisponivel(
                        medico_id=medico.id,
                        dia_semana=dia_semana,
                        hora_inicio=hora_inicio_slot,
                        hora_fim=hora_fim_slot,
                        ativo=True
                    )
                    db.add(horario)
                    horarios_criados += 1
        
        db.commit()
    
    print(f"   ✅ {horarios_criados} horários criados!")
    return horarios_criados


def popular_consultas(db):
    """Criar consultas de teste"""
    print("\n👥 Criando consultas de teste...")
    
    # Buscar médicos e pacientes
    medicos = db.query(Medico).all()
    pacientes = db.query(Paciente).limit(20).all()  # Pegar 20 pacientes
    
    if not medicos or not pacientes:
        print("❌ Médicos ou pacientes não encontrados!")
        return 0
    
    print(f"   ℹ️  {len(medicos)} médicos e {len(pacientes)} pacientes encontrados")
    
    consultas_criadas = 0
    
    # Criar consultas para os últimos 60 dias (para ter histórico)
    data_inicio = datetime.now().date() - timedelta(days=60)
    
    # Distribuir pacientes entre os médicos
    paciente_idx = 0
    
    for dia in range(60):  # 60 dias de histórico
        data = data_inicio + timedelta(days=dia)
        
        # Pular finais de semana
        if data.weekday() >= 5:
            continue
        
        # Criar 3-5 consultas por dia
        consultas_dia = min(5, len(pacientes))
        
        for i in range(consultas_dia):
            if paciente_idx >= len(pacientes):
                paciente_idx = 0  # Recomeçar
            
            medico = medicos[paciente_idx % len(medicos)]
            paciente = pacientes[paciente_idx]
            
            # Horário aleatório entre 8h e 16h
            hora = time(8 + (i * 2), 0)  # 8h, 10h, 12h, 14h, 16h
            
            # Determinar status baseado na data
            hoje = datetime.now().date()
            if data < hoje - timedelta(days=7):
                status = StatusConsulta.REALIZADA
            elif data < hoje:
                # 80% realizadas, 10% canceladas, 10% faltou
                status_random = paciente_idx % 10
                if status_random < 8:
                    status = StatusConsulta.REALIZADA
                elif status_random == 8:
                    status = StatusConsulta.CANCELADA
                else:
                    status = StatusConsulta.FALTOU
            else:
                status = StatusConsulta.AGENDADA
            
            # Criar consulta
            consulta = Consulta(
                paciente_id=paciente.id,
                medico_id=medico.id,
                data=data,
                hora=hora,
                status=status,
                motivo_consulta=f"Consulta de rotina - teste",
                criado_em=datetime.now()
            )
            db.add(consulta)
            consultas_criadas += 1
            paciente_idx += 1
            
            if consultas_criadas % 20 == 0:
                db.commit()
                print(f"   → {consultas_criadas} consultas criadas...")
    
    db.commit()
    print(f"   ✅ {consultas_criadas} consultas criadas!")
    return consultas_criadas


def main():
    print("=" * 80)
    print("🔧 POPULANDO BANCO COM DADOS DE TESTE")
    print("=" * 80)
    
    db = SessionLocal()
    
    try:
        # 1. Criar horários
        total_horarios = popular_horarios(db)
        
        # 2. Criar consultas
        total_consultas = popular_consultas(db)
        
        print("\n" + "=" * 80)
        print("✅ DADOS POPULADOS COM SUCESSO!")
        print("=" * 80)
        print(f"📊 Resumo:")
        print(f"   - Horários: {total_horarios}")
        print(f"   - Consultas: {total_consultas}")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
