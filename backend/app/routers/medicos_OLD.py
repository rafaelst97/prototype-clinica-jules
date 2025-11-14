from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import List, Union
from datetime import date, datetime, time
from app.database import get_db
from app.models import (
    Usuario, Medico, Consulta, HorarioDisponivel as HorarioDisponivelModel,
    BloqueioHorario as BloqueioHorarioModel, StatusConsulta, Especialidade,
    Observacao as ObservacaoModel, Paciente
)
from app.schemas import (
    MedicoResponse, MedicoUpdate,
    ConsultaDetalhada, ConsultaUpdate,
    HorarioDisponivelCreate, HorarioDisponivelResponse, HorariosMultiplosCreate,
    BloqueioHorarioCreate, BloqueioHorarioResponse,
    EspecialidadeResponse,
    ObservacaoCreate, ObservacaoUpdate, ObservacaoResponse
)
from app.utils.dependencies import get_current_medico

router = APIRouter(prefix="/medicos", tags=["Médicos"])

@router.get("/perfil", response_model=MedicoResponse)
def get_perfil(
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Retorna perfil do médico logado"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico

@router.put("/perfil", response_model=MedicoResponse)
def atualizar_perfil(
    medico_update: MedicoUpdate,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Atualiza perfil do médico logado"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Atualizar campos fornecidos
    update_data = medico_update.model_dump(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(medico, field, value)
    
    # Se nome foi atualizado, atualizar também no usuário
    if "nome" in update_data:
        usuario = db.query(Usuario).filter(Usuario.id == current_user.id).first()
        if usuario:
            usuario.nome = update_data["nome"]
    
    db.commit()
    db.refresh(medico)
    return medico

@router.get("/consultas", response_model=List[ConsultaDetalhada])
def listar_consultas(
    data_inicio: date = None,
    data_fim: date = None,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Lista consultas do médico"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    query = db.query(Consulta).filter(Consulta.medico_id == medico.id)
    
    if data_inicio:
        query = query.filter(Consulta.data >= data_inicio)
    if data_fim:
        query = query.filter(Consulta.data <= data_fim)
    
    consultas = query.order_by(Consulta.data, Consulta.hora).all()
    return consultas

@router.get("/consultas/hoje", response_model=List[ConsultaDetalhada])
def consultas_hoje(
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Lista consultas do dia atual"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    hoje = date.today()
    
    consultas = db.query(Consulta).filter(
        Consulta.medico_id == medico.id,
        Consulta.data == hoje,
        Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.CONFIRMADA])
    ).order_by(Consulta.hora).all()
    
    return consultas

@router.get("/consultas/{consulta_id}", response_model=ConsultaDetalhada)
def get_consulta(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Retorna detalhes de uma consulta específica"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    return consulta

@router.put("/consultas/{consulta_id}", response_model=ConsultaDetalhada)
def atualizar_consulta(
    consulta_id: int,
    consulta_data: ConsultaUpdate,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Atualiza observações ou status da consulta"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    if consulta_data.status is not None:
        old_status = consulta.status
        consulta.status = consulta_data.status
        
        # Regra de negócio: zerar faltas quando consulta é realizada
        if consulta_data.status == StatusConsulta.REALIZADA and old_status != StatusConsulta.REALIZADA:
            paciente = db.query(Paciente).filter(Paciente.id == consulta.paciente_id).first()
            if paciente:
                paciente.faltas_consecutivas = 0
        
        # Regra de negócio: incrementar faltas quando paciente falta
        if consulta_data.status == StatusConsulta.FALTOU and old_status != StatusConsulta.FALTOU:
            paciente = db.query(Paciente).filter(Paciente.id == consulta.paciente_id).first()
            if paciente:
                paciente.faltas_consecutivas += 1
                # Bloquear após 3 faltas consecutivas
                if paciente.faltas_consecutivas >= 3:
                    usuario = db.query(Usuario).filter(Usuario.id == paciente.usuario_id).first()
                    if usuario:
                        usuario.bloqueado = True
    
    db.commit()
    db.refresh(consulta)
    
    return consulta

@router.get("/horarios", response_model=List[HorarioDisponivelResponse])
def listar_horarios(
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Lista grade de horários do médico"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    horarios = db.query(HorarioDisponivelModel).filter(
        HorarioDisponivelModel.medico_id == medico.id,
        HorarioDisponivelModel.ativo == True
    ).order_by(HorarioDisponivelModel.dia_semana, HorarioDisponivelModel.hora_inicio).all()
    
    return horarios

@router.post("/horarios", status_code=status.HTTP_201_CREATED)
def criar_horario(
    horario_data: Union[HorarioDisponivelCreate, HorariosMultiplosCreate],
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Adiciona horário(s) disponível(is) na agenda - aceita um horário ou múltiplos"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    # Verificar se é múltiplos horários ou único
    if isinstance(horario_data, HorariosMultiplosCreate) or hasattr(horario_data, 'horarios'):
        # Múltiplos horários
        horarios_criados = []
        
        for horario in horario_data.horarios:
            # Validar se hora_fim > hora_inicio
            if horario.hora_fim <= horario.hora_inicio:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Hora fim deve ser maior que hora início (dia {horario.dia_semana})"
                )
            
            novo_horario = HorarioDisponivelModel(
                medico_id=medico.id,
                dia_semana=horario.dia_semana,
                hora_inicio=horario.hora_inicio,
                hora_fim=horario.hora_fim
            )
            
            db.add(novo_horario)
            horarios_criados.append(novo_horario)
        
        db.commit()
        
        # Refresh todos os horários criados
        for h in horarios_criados:
            db.refresh(h)
        
        return {
            "message": f"{len(horarios_criados)} horários criados com sucesso",
            "horarios": [
                {
                    "id": h.id,
                    "dia_semana": h.dia_semana,
                    "hora_inicio": str(h.hora_inicio),
                    "hora_fim": str(h.hora_fim),
                    "medico_id": h.medico_id,
                    "ativo": h.ativo
                } for h in horarios_criados
            ]
        }
    else:
        # Horário único
        # Validar se hora_fim > hora_inicio
        if horario_data.hora_fim <= horario_data.hora_inicio:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hora fim deve ser maior que hora início"
            )
        
        novo_horario = HorarioDisponivelModel(
            medico_id=medico.id,
            dia_semana=horario_data.dia_semana,
            hora_inicio=horario_data.hora_inicio,
            hora_fim=horario_data.hora_fim
        )
        
        db.add(novo_horario)
        db.commit()
        db.refresh(novo_horario)
        
        return {
            "id": novo_horario.id,
            "dia_semana": novo_horario.dia_semana,
            "hora_inicio": str(novo_horario.hora_inicio),
            "hora_fim": str(novo_horario.hora_fim),
            "medico_id": novo_horario.medico_id,
            "ativo": novo_horario.ativo
        }

@router.delete("/horarios/{horario_id}")
def remover_horario(
    horario_id: int,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Remove horário disponível"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    horario = db.query(HorarioDisponivelModel).filter(
        HorarioDisponivelModel.id == horario_id,
        HorarioDisponivelModel.medico_id == medico.id
    ).first()
    
    if not horario:
        raise HTTPException(status_code=404, detail="Horário não encontrado")
    
    horario.ativo = False
    db.commit()
    
    return {"message": "Horário removido com sucesso"}

@router.delete("/horarios")
def limpar_todos_horarios(
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Remove todos os horários disponíveis do médico"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    # Desativar todos os horários do médico
    db.query(HorarioDisponivelModel).filter(
        HorarioDisponivelModel.medico_id == medico.id
    ).update({"ativo": False})
    
    db.commit()
    
    return {"message": "Todos os horários foram removidos"}

@router.get("/bloqueios", response_model=List[BloqueioHorarioResponse])
def listar_bloqueios(
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Lista bloqueios de horários"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    bloqueios = db.query(BloqueioHorarioModel).filter(
        BloqueioHorarioModel.medico_id == medico.id,
        BloqueioHorarioModel.data >= date.today()
    ).order_by(BloqueioHorarioModel.data, BloqueioHorarioModel.hora_inicio).all()
    
    return bloqueios

@router.post("/bloqueios", response_model=BloqueioHorarioResponse, status_code=status.HTTP_201_CREATED)
def criar_bloqueio(
    bloqueio_data: BloqueioHorarioCreate,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Bloqueia horário específico"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    # Validar data futura
    if bloqueio_data.data < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível bloquear datas passadas"
        )
    
    # Validar hora_fim > hora_inicio
    if bloqueio_data.hora_fim <= bloqueio_data.hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hora fim deve ser maior que hora início"
        )
    
    novo_bloqueio = BloqueioHorarioModel(
        medico_id=medico.id,
        data=bloqueio_data.data,
        hora_inicio=bloqueio_data.hora_inicio,
        hora_fim=bloqueio_data.hora_fim,
        motivo=bloqueio_data.motivo
    )
    
    db.add(novo_bloqueio)
    db.commit()
    db.refresh(novo_bloqueio)
    
    return novo_bloqueio

@router.delete("/bloqueios/{bloqueio_id}")
def remover_bloqueio(
    bloqueio_id: int,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Remove bloqueio de horário"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    bloqueio = db.query(BloqueioHorarioModel).filter(
        BloqueioHorarioModel.id == bloqueio_id,
        BloqueioHorarioModel.medico_id == medico.id
    ).first()
    
    if not bloqueio:
        raise HTTPException(status_code=404, detail="Bloqueio não encontrado")
    
    db.delete(bloqueio)
    db.commit()
    
    return {"message": "Bloqueio removido com sucesso"}

@router.get("/especialidades", response_model=List[EspecialidadeResponse])
def listar_especialidades(db: Session = Depends(get_db)):
    """Lista todas as especialidades médicas"""
    especialidades = db.query(Especialidade).filter(Especialidade.ativo == True).all()
    return especialidades

# ============ Endpoints de Observações ============

@router.post("/observacoes", response_model=ObservacaoResponse, status_code=status.HTTP_201_CREATED)
def criar_observacao(
    observacao_data: ObservacaoCreate,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Registra observação após a consulta (Caso de Uso: Registrar Observações da Consulta)"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    # Verificar se a consulta existe e pertence ao médico
    consulta = db.query(Consulta).filter(
        Consulta.id == observacao_data.consulta_id,
        Consulta.medico_id == medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    # Verificar se já existe observação para esta consulta
    observacao_existente = db.query(ObservacaoModel).filter(
        ObservacaoModel.consulta_id == observacao_data.consulta_id
    ).first()
    
    if observacao_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Já existe uma observação para esta consulta"
        )
    
    nova_observacao = ObservacaoModel(
        consulta_id=observacao_data.consulta_id,
        descricao=observacao_data.descricao
    )
    
    db.add(nova_observacao)
    db.commit()
    db.refresh(nova_observacao)
    
    return nova_observacao

@router.get("/observacoes/{consulta_id}", response_model=ObservacaoResponse)
def get_observacao(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Visualiza observação de uma consulta (Caso de Uso: Visualizar Observações da Consulta)"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    # Verificar se a consulta pertence ao médico
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    observacao = db.query(ObservacaoModel).filter(
        ObservacaoModel.consulta_id == consulta_id
    ).first()
    
    if not observacao:
        raise HTTPException(status_code=404, detail="Observação não encontrada")
    
    return observacao

@router.put("/observacoes/{consulta_id}", response_model=ObservacaoResponse)
def atualizar_observacao(
    consulta_id: int,
    observacao_data: ObservacaoUpdate,
    current_user: Usuario = Depends(get_current_medico),
    db: Session = Depends(get_db)
):
    """Atualiza observação de uma consulta"""
    medico = db.query(Medico).filter(Medico.usuario_id == current_user.id).first()
    
    # Verificar se a consulta pertence ao médico
    consulta = db.query(Consulta).filter(
        Consulta.id == consulta_id,
        Consulta.medico_id == medico.id
    ).first()
    
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    observacao = db.query(ObservacaoModel).filter(
        ObservacaoModel.consulta_id == consulta_id
    ).first()
    
    if not observacao:
        raise HTTPException(status_code=404, detail="Observação não encontrada")
    
    observacao.descricao = observacao_data.descricao
    db.commit()
    db.refresh(observacao)
    
    return observacao
