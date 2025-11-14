"""
Router de Pacientes - Sistema Clínica Saúde+
Implementa todos os casos de uso do módulo Paciente conforme CasosDeUso.txt
Atualizado para modelo conforme MER
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import datetime, timedelta, date
from app.database import get_db
from app.models.models import Paciente, Medico, Consulta, Especialidade, PlanoSaude, HorarioTrabalho
from app.schemas.schemas import (
    PacienteCreate, PacienteUpdate, PacienteAlterarSenha, PacienteResponse,
    ConsultaCreate, ConsultaResponse, ConsultaCancelar, ConsultaReagendar,
    MedicoResponse, EspecialidadeResponse, PlanoSaudeResponse,
    HorariosDisponiveisResponse
)
from app.utils.auth import get_password_hash, verify_password
from app.services.regras_negocio import (
    ValidadorAgendamento,
    RegraConsulta,
    RegraPaciente,
    RegraHorarioDisponivel
)

router = APIRouter(prefix="/pacientes", tags=["Pacientes"])


@router.post("/cadastro", response_model=PacienteResponse, status_code=status.HTTP_201_CREATED)
def cadastrar_paciente(paciente_data: PacienteCreate, db: Session = Depends(get_db)):
    """
    Caso de Uso: Cadastrar Paciente
    Cadastro com CPF, nome completo, telefone, e-mail e plano de saúde (opcional)
    """
    # Verificar se email já existe
    email_existe = db.query(Paciente).filter(Paciente.email == paciente_data.email).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado no sistema"
        )
    
    # Verificar se CPF já existe
    cpf_existe = db.query(Paciente).filter(Paciente.cpf == paciente_data.cpf).first()
    if cpf_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF já cadastrado no sistema"
        )
    
    # Verificar se plano de saúde existe (se informado)
    if paciente_data.id_plano_saude_fk:
        plano = db.query(PlanoSaude).filter(
            PlanoSaude.id_plano_saude == paciente_data.id_plano_saude_fk
        ).first()
        if not plano:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Plano de saúde não encontrado"
            )
    
    try:
        # Criar paciente
        novo_paciente = Paciente(
            nome=paciente_data.nome,
            cpf=paciente_data.cpf,
            email=paciente_data.email,
            senha_hash=get_password_hash(paciente_data.senha),
            telefone=paciente_data.telefone,
            data_nascimento=paciente_data.data_nascimento,
            esta_bloqueado=False,
            id_plano_saude_fk=paciente_data.id_plano_saude_fk
        )
        db.add(novo_paciente)
        db.commit()
        db.refresh(novo_paciente)
        
        return novo_paciente
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao cadastrar paciente: dados inválidos ou duplicados"
        )


@router.get("/planos-saude", response_model=List[PlanoSaudeResponse])
def listar_planos_saude(db: Session = Depends(get_db)):
    """
    Lista todos os planos de saúde disponíveis
    """
    planos = db.query(PlanoSaude).all()
    return planos


@router.get("/perfil/{paciente_id}", response_model=PacienteResponse)
def get_perfil(paciente_id: int, db: Session = Depends(get_db)):
    """
    Retorna perfil do paciente
    Deve ser chamado com o ID do paciente obtido do token JWT
    """
    paciente = db.query(Paciente).options(
        joinedload(Paciente.plano_saude)
    ).filter(Paciente.id_paciente == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    return paciente


@router.put("/perfil/{paciente_id}", response_model=PacienteResponse)
def atualizar_perfil(
    paciente_id: int,
    paciente_data: PacienteUpdate,
    db: Session = Depends(get_db)
):
    """
    Atualiza perfil do paciente
    Permite atualizar: nome, telefone, plano de saúde
    """
    paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Atualizar apenas campos fornecidos
    if paciente_data.nome is not None:
        paciente.nome = paciente_data.nome
    if paciente_data.telefone is not None:
        paciente.telefone = paciente_data.telefone
    if paciente_data.id_plano_saude_fk is not None:
        # Verificar se plano existe
        if paciente_data.id_plano_saude_fk > 0:
            plano = db.query(PlanoSaude).filter(
                PlanoSaude.id_plano_saude == paciente_data.id_plano_saude_fk
            ).first()
            if not plano:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Plano de saúde não encontrado"
                )
        paciente.id_plano_saude_fk = paciente_data.id_plano_saude_fk
    
    db.commit()
    db.refresh(paciente)
    return paciente


@router.put("/perfil/{paciente_id}/senha")
def alterar_senha(
    paciente_id: int,
    dados_senha: PacienteAlterarSenha,
    db: Session = Depends(get_db)
):
    """
    Altera a senha do paciente
    Requer senha atual para validação
    """
    paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Verificar senha atual
    if not verify_password(dados_senha.senha_atual, paciente.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Senha atual incorreta"
        )
    
    # Validar nova senha (8 a 20 caracteres alfanuméricos)
    if len(dados_senha.senha_nova) < 8 or len(dados_senha.senha_nova) > 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A senha deve ter entre 8 e 20 caracteres"
        )
    
    # Atualizar senha
    paciente.senha_hash = get_password_hash(dados_senha.senha_nova)
    db.commit()
    
    return {"message": "Senha alterada com sucesso"}


@router.post("/consultas", response_model=ConsultaResponse, status_code=status.HTTP_201_CREATED)
def agendar_consulta(
    paciente_id: int,
    consulta_data: ConsultaCreate,
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Agendar Consulta
    Permite agendar escolhendo médico e horário disponível
    
    Regras de Negócio aplicadas:
    - RN2: Máximo 2 consultas futuras por paciente
    - RN3: Bloqueio após 3 faltas consecutivas
    - RN4: Evitar conflitos de horário
    - RN: Validar horário de trabalho do médico
    """
    # Verificar se paciente existe
    paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Verificar se médico existe
    medico = db.query(Medico).filter(Medico.id_medico == consulta_data.id_medico).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Obter data_hora do schema (pode vir como data_hora ou data_hora_inicio)
    data_hora = getattr(consulta_data, 'data_hora', None) or getattr(consulta_data, 'data_hora_inicio', None)
    
    if not data_hora:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Data e hora da consulta são obrigatórias"
        )
    
    data_hora_fim = data_hora + timedelta(minutes=30)
    
    # Validar todas as regras de negócio
    pode_agendar, mensagem = ValidadorAgendamento.validar_novo_agendamento(
        db, paciente_id, consulta_data.id_medico,
        data_hora, data_hora_fim
    )
    
    if not pode_agendar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensagem
        )
    
    # Criar consulta
    nova_consulta = Consulta(
        data_hora_inicio=data_hora,
        data_hora_fim=data_hora_fim,
        status="agendada",
        id_paciente_fk=paciente_id,
        id_medico_fk=consulta_data.id_medico
    )
    
    db.add(nova_consulta)
    db.commit()
    db.refresh(nova_consulta)
    
    return nova_consulta


@router.get("/consultas/{paciente_id}", response_model=List[ConsultaResponse])
def listar_consultas(paciente_id: int, db: Session = Depends(get_db)):
    """
    Caso de Uso: Visualizar Consultas
    Lista todas as consultas do paciente (futuras e passadas)
    """
    # Verificar se paciente existe
    paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    # Buscar consultas com informações de médico e paciente
    consultas = db.query(Consulta).options(
        joinedload(Consulta.medico).joinedload(Medico.especialidade),
        joinedload(Consulta.paciente)
    ).filter(
        Consulta.id_paciente_fk == paciente_id
    ).order_by(Consulta.data_hora_inicio.desc()).all()
    
    return consultas


@router.delete("/consultas/{consulta_id}", status_code=status.HTTP_200_OK)
def cancelar_consulta(
    consulta_id: int,
    paciente_id: int,
    cancelamento_data: ConsultaCancelar,
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Cancelar Consulta
    RN1: Cancelamento apenas até 24h antes do horário agendado
    """
    # Buscar consulta
    consulta = db.query(Consulta).filter(
        Consulta.id_consulta == consulta_id,
        Consulta.id_paciente_fk == paciente_id
    ).first()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Verificar se já está cancelada
    if consulta.status == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consulta já está cancelada"
        )
    
    # Verificar se já foi realizada
    if consulta.status == "realizada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar uma consulta já realizada"
        )
    
    # Validar regra de 24h (RN1)
    pode_cancelar, mensagem = RegraConsulta.validar_cancelamento_24h(consulta)
    if not pode_cancelar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensagem
        )
    
    # Cancelar consulta
    consulta.status = "cancelada"
    db.commit()
    
    return {
        "sucesso": True,
        "mensagem": "Consulta cancelada com sucesso"
    }


@router.put("/consultas/{consulta_id}/reagendar", response_model=ConsultaResponse)
def reagendar_consulta(
    consulta_id: int,
    paciente_id: int,
    reagendamento_data: ConsultaReagendar,
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Reagendar Consulta
    RN1: Reagendamento apenas até 24h antes do horário atual
    RN4: Validar conflitos de horário
    """
    # Buscar consulta
    consulta = db.query(Consulta).filter(
        Consulta.id_consulta == consulta_id,
        Consulta.id_paciente_fk == paciente_id
    ).first()
    
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Verificar status
    if consulta.status == "cancelada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível reagendar uma consulta cancelada"
        )
    
    if consulta.status == "realizada":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível reagendar uma consulta já realizada"
        )
    
    # Validar regra de 24h (RN1)
    pode_reagendar, mensagem = RegraConsulta.validar_reagendamento_24h(consulta)
    if not pode_reagendar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=mensagem
        )
    
    # Nova data/hora (suporta ambos os nomes de campo)
    nova_data_hora = getattr(reagendamento_data, 'nova_data_hora', None) or getattr(reagendamento_data, 'nova_data_hora_inicio', None) or getattr(reagendamento_data, 'data_hora_inicio', None)
    
    if not nova_data_hora:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nova data e hora são obrigatórias"
        )
    
    nova_data_hora_fim = nova_data_hora + timedelta(minutes=30)
    
    # Validar horário de trabalho
    no_horario, msg_horario = RegraConsulta.validar_horario_trabalho_medico(
        db, consulta.id_medico_fk, nova_data_hora
    )
    if not no_horario:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg_horario
        )
    
    # Validar conflito (ignorando a própria consulta)
    sem_conflito, msg_conflito = RegraConsulta.validar_conflito_horario_medico(
        db, consulta.id_medico_fk, nova_data_hora, nova_data_hora_fim,
        consulta_id_ignorar=consulta_id
    )
    if not sem_conflito:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=msg_conflito
        )
    
    # Reagendar consulta
    consulta.data_hora_inicio = nova_data_hora
    consulta.data_hora_fim = nova_data_hora_fim
    db.commit()
    db.refresh(consulta)
    
    return consulta


@router.get("/medicos", response_model=List[MedicoResponse])
def buscar_medicos(
    especialidade_id: int = None,
    db: Session = Depends(get_db)
):
    """
    Busca médicos para agendamento
    Pode filtrar por especialidade
    """
    query = db.query(Medico).options(joinedload(Medico.especialidade))
    
    if especialidade_id:
        query = query.filter(Medico.id_especialidade_fk == especialidade_id)
    
    medicos = query.all()
    return medicos


@router.get("/medicos/{medico_id}/horarios-disponiveis")
def get_horarios_disponiveis(
    medico_id: int,
    data: date,
    db: Session = Depends(get_db)
):
    """
    Retorna horários disponíveis de um médico para uma data específica
    Considera horários de trabalho e consultas já agendadas
    """
    # Verificar se médico existe
    medico = db.query(Medico).filter(Medico.id_medico == medico_id).first()
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Listar horários disponíveis usando serviço de regras de negócio
    horarios = RegraHorarioDisponivel.listar_horarios_disponiveis(
        db, medico_id, data, duracao_consulta_minutos=30
    )
    
    return {
        "data": data.isoformat(),
        "horarios_disponiveis": horarios
    }


@router.get("/especialidades", response_model=List[EspecialidadeResponse])
def listar_especialidades(db: Session = Depends(get_db)):
    """Lista todas as especialidades médicas disponíveis"""
    especialidades = db.query(Especialidade).all()
    return especialidades


@router.get("/planos-saude", response_model=List[PlanoSaudeResponse])
def listar_planos_saude(db: Session = Depends(get_db)):
    """Lista todos os planos de saúde disponíveis (para cadastro)"""
    planos = db.query(PlanoSaude).all()
    return planos
