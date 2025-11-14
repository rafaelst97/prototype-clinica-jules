"""
Router de Consultas - Sistema Clínica Saúde+
Implementa todas as operações de agendamento, cancelamento e reagendamento
Com validação completa das Regras de Negócio (RN1-RN4)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
from app.database import get_db
from app.models.models import Consulta, Paciente, Medico, HorarioTrabalho
from app.schemas.schemas import ConsultaResponse, ConsultaCreate, ConsultaUpdate
from app.utils.auth import get_current_user

router = APIRouter(prefix="/consultas", tags=["Consultas"])

# Mapeamento de dia da semana (0=Segunda, 6=Domingo)
DIAS_SEMANA = {
    0: "Segunda",
    1: "Terça",
    2: "Quarta",
    3: "Quinta",
    4: "Sexta",
    5: "Sábado",
    6: "Domingo"
}


def validar_paciente_bloqueado(paciente: Paciente):
    """RN1: Validar se paciente está bloqueado"""
    if paciente.esta_bloqueado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Paciente bloqueado por faltas consecutivas. Não é possível agendar consultas."
        )


def validar_horario_trabalho_medico(data_hora: datetime, medico_id: int, db: Session):
    """RN2: Validar se o horário está dentro do expediente do médico"""
    dia_semana = DIAS_SEMANA[data_hora.weekday()]
    
    # Buscar horário de trabalho do médico para o dia
    horario = db.query(HorarioTrabalho).filter(
        HorarioTrabalho.id_medico_fk == medico_id,
        HorarioTrabalho.dia_semana == dia_semana
    ).first()
    
    if not horario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Médico não trabalha às {dia_semana}s"
        )
    
    # Validar se hora está dentro do expediente
    hora_consulta = data_hora.time()
    if not (horario.hora_inicio <= hora_consulta <= horario.hora_fim):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Horário fora do expediente do médico. Horário disponível: {horario.hora_inicio} às {horario.hora_fim}"
        )


def validar_conflito_horario(data_hora: datetime, medico_id: int, db: Session, consulta_id: int = None):
    """RN3: Validar se já existe consulta no mesmo horário"""
    # Buscar consultas no mesmo horário (±30min para evitar sobreposição)
    inicio_janela = data_hora - timedelta(minutes=30)
    fim_janela = data_hora + timedelta(minutes=30)
    
    query = db.query(Consulta).filter(
        Consulta.id_medico_fk == medico_id,
        Consulta.data_hora >= inicio_janela,
        Consulta.data_hora <= fim_janela,
        Consulta.status.in_(["Agendada", "Confirmada"])
    )
    
    # Se for reagendamento, excluir a própria consulta
    if consulta_id:
        query = query.filter(Consulta.id_consulta != consulta_id)
    
    consulta_existente = query.first()
    
    if consulta_existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Horário já ocupado. Por favor, escolha outro horário."
        )


def validar_antecedencia_minima(data_hora: datetime):
    """RN4: Validar antecedência mínima de 24 horas"""
    agora = datetime.now()
    diferenca = data_hora - agora
    
    if diferenca.total_seconds() < 24 * 3600:  # 24 horas em segundos
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelamento/reagendamento requer antecedência mínima de 24 horas"
        )


@router.post("/agendar", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def agendar_consulta(
    consulta_data: ConsultaCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Agendar nova consulta
    
    Validações:
    - RN1: Paciente não pode estar bloqueado
    - RN2: Horário deve estar no expediente do médico
    - RN3: Não pode haver conflito de horários
    """
    # Validar que usuário logado é paciente
    if current_user["tipo"] != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas pacientes podem agendar consultas"
        )
    
    # Buscar paciente
    paciente = db.query(Paciente).filter(
        Paciente.id_paciente == current_user["id"]
    ).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # RN1: Validar se paciente está bloqueado
    validar_paciente_bloqueado(paciente)
    
    # Buscar médico
    medico = db.query(Medico).filter(
        Medico.id_medico == consulta_data.id_medico
    ).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # RN2: Validar horário de trabalho
    validar_horario_trabalho_medico(consulta_data.data_hora, consulta_data.id_medico, db)
    
    # RN3: Validar conflito de horários
    validar_conflito_horario(consulta_data.data_hora, consulta_data.id_medico, db)
    
    # Criar consulta
    nova_consulta = Consulta(
        id_paciente_fk=paciente.id_paciente,
        id_medico_fk=consulta_data.id_medico,
        data_hora=consulta_data.data_hora,
        tipo=consulta_data.tipo,
        status="Agendada"
    )
    
    db.add(nova_consulta)
    db.commit()
    db.refresh(nova_consulta)
    
    return nova_consulta


@router.get("/minhas", response_model=List[ConsultaResponse])
def listar_minhas_consultas(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Listar consultas do paciente ou médico logado"""
    
    if current_user["tipo"] == "paciente":
        consultas = db.query(Consulta).filter(
            Consulta.id_paciente_fk == current_user["id"]
        ).order_by(Consulta.data_hora.desc()).all()
    
    elif current_user["tipo"] == "medico":
        consultas = db.query(Consulta).filter(
            Consulta.id_medico_fk == current_user["id"]
        ).order_by(Consulta.data_hora).all()
    
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    return consultas


@router.get("/{consulta_id}", response_model=ConsultaResponse)
def buscar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Buscar consulta específica"""
    consulta = db.query(Consulta).filter(
        Consulta.id_consulta == consulta_id
    ).first()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Validar acesso
    if current_user["tipo"] == "paciente":
        if consulta.id_paciente_fk != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    elif current_user["tipo"] == "medico":
        if consulta.id_medico_fk != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    
    return consulta


@router.put("/{consulta_id}/cancelar", response_model=ConsultaResponse)
def cancelar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Cancelar consulta
    
    Validação:
    - RN4: Requer antecedência mínima de 24 horas
    """
    consulta = db.query(Consulta).filter(
        Consulta.id_consulta == consulta_id
    ).first()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Validar acesso
    if current_user["tipo"] == "paciente":
        if consulta.id_paciente_fk != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    elif current_user["tipo"] == "medico":
        if consulta.id_medico_fk != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado"
            )
    
    # Validar status
    if consulta.status == "Cancelada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consulta já está cancelada"
        )
    
    # RN4: Validar antecedência mínima
    validar_antecedencia_minima(consulta.data_hora)
    
    # Cancelar
    consulta.status = "Cancelada"
    db.commit()
    db.refresh(consulta)
    
    return consulta


@router.put("/{consulta_id}/reagendar", response_model=ConsultaResponse)
def reagendar_consulta(
    consulta_id: int,
    consulta_update: ConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    Reagendar consulta
    
    Validações:
    - RN4: Requer antecedência mínima de 24 horas da data original
    - RN2: Nova data deve estar no expediente do médico
    - RN3: Não pode haver conflito no novo horário
    """
    consulta = db.query(Consulta).filter(
        Consulta.id_consulta == consulta_id
    ).first()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Validar acesso (apenas paciente pode reagendar)
    if current_user["tipo"] != "paciente":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas pacientes podem reagendar consultas"
        )
    
    if consulta.id_paciente_fk != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado"
        )
    
    # Validar status
    if consulta.status != "Agendada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Apenas consultas agendadas podem ser reagendadas"
        )
    
    # RN4: Validar antecedência mínima da data ORIGINAL
    validar_antecedencia_minima(consulta.data_hora)
    
    # RN2: Validar novo horário no expediente
    validar_horario_trabalho_medico(
        consulta_update.nova_data_hora,
        consulta.id_medico_fk,
        db
    )
    
    # RN3: Validar conflito no novo horário
    validar_conflito_horario(
        consulta_update.nova_data_hora,
        consulta.id_medico_fk,
        db,
        consulta_id=consulta_id
    )
    
    # Reagendar
    consulta.data_hora = consulta_update.nova_data_hora
    db.commit()
    db.refresh(consulta)
    
    return consulta


@router.get("/horarios-disponiveis/{medico_id}")
def buscar_horarios_disponiveis(
    medico_id: int,
    data: str,  # Formato: YYYY-MM-DD
    db: Session = Depends(get_db)
):
    """
    Buscar horários disponíveis de um médico em uma data específica
    
    Retorna lista de horários livres no formato HH:MM
    """
    # Validar médico
    medico = db.query(Medico).filter(Medico.id_medico == medico_id).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Converter data
    try:
        data_consulta = datetime.strptime(data, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    
    # Buscar horário de trabalho do dia
    dia_semana = DIAS_SEMANA[data_consulta.weekday()]
    horario = db.query(HorarioTrabalho).filter(
        HorarioTrabalho.id_medico_fk == medico_id,
        HorarioTrabalho.dia_semana == dia_semana
    ).first()
    
    if not horario:
        return []
    
    # Buscar consultas agendadas
    consultas = db.query(Consulta).filter(
        Consulta.id_medico_fk == medico_id,
        Consulta.status.in_(["Agendada", "Confirmada"]),
        Consulta.data_hora >= datetime.combine(data_consulta, horario.hora_inicio),
        Consulta.data_hora <= datetime.combine(data_consulta, horario.hora_fim)
    ).all()
    
    horarios_ocupados = [c.data_hora.time() for c in consultas]
    
    # Gerar horários disponíveis (intervalos de 30 min)
    horarios_disponiveis = []
    hora_atual = horario.hora_inicio
    hora_fim = horario.hora_fim
    
    while hora_atual < hora_fim:
        if hora_atual not in horarios_ocupados:
            horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
        
        # Próximo slot (30 minutos depois)
        hora_datetime = datetime.combine(data_consulta, hora_atual)
        hora_datetime += timedelta(minutes=30)
        hora_atual = hora_datetime.time()
    
    return horarios_disponiveis
