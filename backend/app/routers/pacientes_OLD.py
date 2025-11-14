from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime, date
from app.database import get_db
from app.models import Usuario, Paciente, Consulta, Medico, TipoUsuario, StatusConsulta, Convenio, Especialidade
from app.schemas import (
    PacienteCreate, PacienteUpdate, PacienteResponse,
    ConsultaCreate, ConsultaResponse, ConsultaDetalhada, ConsultaCancelar, ConsultaReagendar,
    HorarioDisponivel, MedicoResponse, ConvenioResponse, EspecialidadeResponse
)
from app.utils.auth import get_password_hash
from app.utils.dependencies import get_current_paciente, get_current_user
from app.utils.validators import (
    validar_limite_consultas,
    validar_cancelamento_24h,
    verificar_conflito_horario,
    verificar_horario_bloqueado,
    verificar_horario_disponivel,
    gerar_horarios_disponiveis,
    verificar_paciente_bloqueado
)

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])

@router.post("/cadastro", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_paciente(paciente_data: PacienteCreate, db: Session = Depends(get_db)):
    """Cadastro de novo paciente"""
    # Verificar se email já existe
    if db.query(Usuario).filter(Usuario.email == paciente_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado no sistema"
        )
    
    # Verificar se CPF já existe
    if db.query(Paciente).filter(Paciente.cpf == paciente_data.cpf).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF já cadastrado no sistema"
        )
    
    try:
        # Criar usuário
        novo_usuario = Usuario(
            email=paciente_data.email,
            senha_hash=get_password_hash(paciente_data.senha),
            nome=paciente_data.nome,
            tipo=TipoUsuario.PACIENTE
        )
        db.add(novo_usuario)
        db.flush()
        
        # Criar paciente
        novo_paciente = Paciente(
            usuario_id=novo_usuario.id,
            cpf=paciente_data.cpf,
            data_nascimento=paciente_data.data_nascimento,
            telefone=paciente_data.telefone,
            endereco=paciente_data.endereco,
            cidade=paciente_data.cidade,
            estado=paciente_data.estado,
            cep=paciente_data.cep,
            convenio_id=paciente_data.convenio_id,
            numero_carteirinha=paciente_data.numero_carteirinha
        )
        db.add(novo_paciente)
        db.commit()
        db.refresh(novo_paciente)
        
        return novo_paciente
    
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'email' in error_msg or 'usuario_email_key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado no sistema"
            )
        elif 'cpf' in error_msg or 'paciente_cpf_key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF já cadastrado no sistema"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao cadastrar paciente: dados inválidos ou duplicados"
            )

@router.get("/perfil", response_model=PacienteResponse)
def get_perfil(
    current_user: Usuario = Depends(get_current_paciente),
    db: Session = Depends(get_db)
):
    """Retorna perfil do paciente logado"""
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    return paciente

@router.put("/perfil", response_model=PacienteResponse)
def atualizar_perfil(
    paciente_data: PacienteUpdate,
    current_user: Usuario = Depends(get_current_paciente),
    db: Session = Depends(get_db)
):
    """Atualiza perfil do paciente"""
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Atualizar dados do usuário
    if paciente_data.nome:
        current_user.nome = paciente_data.nome
    
    # Atualizar dados do paciente
    for field, value in paciente_data.dict(exclude_unset=True).items():
        if field != "nome" and value is not None:
            setattr(paciente, field, value)
    
    db.commit()
    db.refresh(paciente)
    return paciente

@router.post("/consultas", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def agendar_consulta(
    consulta_data: ConsultaCreate,
    current_user: Usuario = Depends(get_current_paciente),
    db: Session = Depends(get_db)
):
    """
    Agendar nova consulta
    Caso de Uso: Agendar Consulta
    Regra de Negócio: Máximo 2 consultas futuras por paciente
    """
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    
    # Verificar se paciente está bloqueado (Regra: 3 faltas consecutivas)
    if verificar_paciente_bloqueado(db, paciente.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sua conta está bloqueada. Entre em contato com a administração."
        )
    
    # Validar limite de 2 consultas (Regra de Negócio)
    if not validar_limite_consultas(db, paciente.id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Você já possui 2 consultas agendadas. Cancele uma para agendar outra."
        )
    
    # Verificar se médico existe
    medico = db.query(Medico).filter(Medico.id == consulta_data.medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Validar se é data futura
    if consulta_data.data < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível agendar consultas em datas passadas"
        )
    
    # Validar horário disponível
    if not verificar_horario_disponivel(db, consulta_data.medico_id, consulta_data.data, consulta_data.hora):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Horário não está disponível na agenda do médico"
        )
    
    # Verificar bloqueio
    if verificar_horario_bloqueado(db, consulta_data.medico_id, consulta_data.data, consulta_data.hora):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Horário bloqueado pelo médico"
        )
    
    # Verificar conflito
    if verificar_conflito_horario(db, consulta_data.medico_id, consulta_data.data, consulta_data.hora):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Horário já possui uma consulta agendada"
        )
    
    # Criar consulta
    nova_consulta = Consulta(
        paciente_id=paciente.id,
        medico_id=consulta_data.medico_id,
        data=consulta_data.data,
        hora=consulta_data.hora,
        motivo_consulta=consulta_data.motivo_consulta,
        status=StatusConsulta.AGENDADA
    )
    db.add(nova_consulta)
    db.commit()
    db.refresh(nova_consulta)
    
    return nova_consulta

@router.get("/consultas", response_model=List[ConsultaDetalhada])
def listar_consultas(
    current_user: Usuario = Depends(get_current_paciente),
    db: Session = Depends(get_db)
):
    """Lista todas as consultas do paciente"""
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    
    consultas = db.query(Consulta).options(
        joinedload(Consulta.paciente).joinedload(Paciente.usuario),
        joinedload(Consulta.medico).joinedload(Medico.usuario),
        joinedload(Consulta.medico).joinedload(Medico.especialidade)
    ).filter(
        Consulta.paciente_id == paciente.id
    ).order_by(Consulta.data.desc(), Consulta.hora.desc()).all()
    
    return consultas

@router.delete("/consultas/{consulta_id}")
def cancelar_consulta(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_paciente),
    db: Session = Depends(get_db),
    motivo_cancelamento: str = None
):
    """
    Cancelar consulta
    Caso de Uso: Cancelar Consulta
    Regra de Negócio: Cancelamento apenas até 24h antes do horário agendado
    """
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.paciente_id == paciente.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta.status == StatusConsulta.CANCELADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consulta já está cancelada"
        )
    
    if consulta.status == StatusConsulta.REALIZADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar uma consulta já realizada"
        )
    
    # Validar regra de 24h (Regra de Negócio)
    if not validar_cancelamento_24h(consulta):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelamento deve ser feito com pelo menos 24h de antecedência"
        )
    
    consulta.status = StatusConsulta.CANCELADA
    consulta.cancelado_em = datetime.now()
    consulta.motivo_cancelamento = motivo_cancelamento
    
    db.commit()
    
    return {"message": "Consulta cancelada com sucesso"}

@router.put("/consultas/{consulta_id}/reagendar", response_model=ConsultaResponse)
def reagendar_consulta(
    consulta_id: int,
    reagendamento_data: ConsultaReagendar,
    current_user: Usuario = Depends(get_current_paciente),
    db: Session = Depends(get_db)
):
    """
    Reagendar consulta existente
    Caso de Uso: Reagendar Consulta
    Regra de Negócio: 
    - Reagendamento apenas até 24h antes do horário atual
    - Nova data deve respeitar horários disponíveis do médico
    - Limite de 2 consultas futuras continua valendo
    """
    paciente = db.query(Paciente).filter(Paciente.usuario_id == current_user.id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Buscar consulta
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.paciente_id == paciente.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    # Validações de status
    if consulta.status == StatusConsulta.CANCELADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível reagendar uma consulta cancelada"
        )
    
    if consulta.status == StatusConsulta.REALIZADA:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível reagendar uma consulta já realizada"
        )
    
    # Validar regra de 24h para reagendamento (Regra de Negócio)
    if not validar_cancelamento_24h(consulta):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reagendamento deve ser feito com pelo menos 24h de antecedência"
        )
    
    # Validar se nova data/hora está disponível
    if not verificar_horario_disponivel(
        db, consulta.medico_id, reagendamento_data.nova_data, reagendamento_data.nova_hora
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Horário não está disponível na agenda do médico"
        )
    
    # Verificar conflito de horário com outras consultas do médico
    conflito = verificar_conflito_horario(
        db, consulta.medico_id, reagendamento_data.nova_data, 
        reagendamento_data.nova_hora, consulta_id  # Excluir a própria consulta
    )
    if conflito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma consulta agendada para este horário"
        )
    
    # Verificar se horário não está bloqueado
    if verificar_horario_bloqueado(
        db, consulta.medico_id, reagendamento_data.nova_data, reagendamento_data.nova_hora
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este horário está bloqueado pelo médico"
        )
    
    # Atualizar consulta
    consulta.data = reagendamento_data.nova_data
    consulta.hora = reagendamento_data.nova_hora
    
    db.commit()
    db.refresh(consulta)
    
    return consulta

@router.get("/medicos", response_model=List[MedicoResponse])
def buscar_medicos(
    especialidade_id: int = None,
    db: Session = Depends(get_db)
):
    """Busca médicos, opcionalmente filtrados por especialidade"""
    from app.models import Medico as MedicoModel
    
    query = db.query(MedicoModel)
    
    if especialidade_id:
        query = query.filter(MedicoModel.especialidade_id == especialidade_id)
    
    medicos = query.all()
    return medicos

@router.get("/medicos/{medico_id}/horarios", response_model=dict)
def listar_horarios_medico(
    medico_id: int,
    db: Session = Depends(get_db)
):
    """Lista todos os horários disponíveis configurados para um médico"""
    from app.models import HorarioDisponivel as HorarioDisponivelModel
    
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    horarios = db.query(HorarioDisponivelModel).filter(
        HorarioDisponivelModel.medico_id == medico_id,
        HorarioDisponivelModel.ativo == True
    ).all()
    
    # Converter para formato serializável
    horarios_dict = [
        {
            "id": h.id,
            "dia_semana": h.dia_semana,
            "hora_inicio": h.hora_inicio.strftime("%H:%M"),
            "hora_fim": h.hora_fim.strftime("%H:%M"),
            "ativo": h.ativo
        }
        for h in horarios
    ]
    
    return {"medico_id": medico_id, "horarios": horarios_dict}

@router.get("/medicos/{medico_id}/horarios-disponiveis", response_model=HorarioDisponivel)
def get_horarios_disponiveis(
    medico_id: int,
    data: date,
    db: Session = Depends(get_db)
):
    """Retorna horários disponíveis de um médico para uma data específica"""
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    horarios = gerar_horarios_disponiveis(db, medico_id, data, medico.tempo_consulta)
    
    return {"data": data, "horarios": horarios}

@router.get("/convenios", response_model=List[ConvenioResponse])
def listar_convenios_publico(db: Session = Depends(get_db)):
    """Lista todos os convênios ativos (endpoint público para cadastro)"""
    convenios = db.query(Convenio).filter(Convenio.ativo == True).all()
    return convenios

@router.get("/especialidades", response_model=List[EspecialidadeResponse])
def listar_especialidades_publico(db: Session = Depends(get_db)):
    """Lista todas as especialidades ativas (endpoint público)"""
    especialidades = db.query(Especialidade).filter(Especialidade.ativo == True).all()
    return especialidades
