from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.database import get_db
from app.models import (
    Usuario, Medico, Paciente, Admin, Consulta, Convenio, Especialidade,
    TipoUsuario, StatusConsulta, Relatorio as RelatorioModel, Observacao
)
from app.schemas import (
    MedicoCreate, MedicoUpdate, MedicoResponse,
    PacienteResponse,
    ConvenioCreate, ConvenioUpdate, ConvenioResponse,
    EspecialidadeCreate, EspecialidadeResponse,
    AdminCreate, AdminResponse,
    EstatisticasDashboard,
    ConsultaDetalhada,
    RelatorioResponse,
    RelatorioConsultasPorMedico,
    RelatorioConsultasPorEspecialidade,
    RelatorioCancelamentos,
    RelatorioPacientesFrequentes,
    ObservacaoResponse
)
from app.utils.auth import get_password_hash
from app.utils.dependencies import get_current_admin
from app.utils.relatorios import (
    gerar_relatorio_consultas_por_medico,
    gerar_relatorio_consultas_por_especialidade,
    gerar_relatorio_cancelamentos,
    gerar_relatorio_pacientes_frequentes,
    criar_pdf_relatorio
)
import json

router = APIRouter(prefix="/admin", tags=["Administração"])

# ============ Estatísticas ============
@router.get("/dashboard", response_model=EstatisticasDashboard)
def get_dashboard(
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retorna estatísticas do dashboard"""
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = date(hoje.year, hoje.month, 1)
    
    total_pacientes = db.query(Paciente).count()
    total_medicos = db.query(Medico).count()
    total_consultas = db.query(Consulta).count()
    
    consultas_hoje = db.query(Consulta).filter(Consulta.data == hoje).count()
    
    consultas_semana = db.query(Consulta).filter(
        Consulta.data >= inicio_semana,
        Consulta.data <= hoje
    ).count()
    
    consultas_mes = db.query(Consulta).filter(
        Consulta.data >= inicio_mes,
        Consulta.data <= hoje
    ).count()
    
    consultas_agendadas = db.query(Consulta).filter(
        Consulta.status == StatusConsulta.AGENDADA
    ).count()
    
    consultas_realizadas = db.query(Consulta).filter(
        Consulta.status == StatusConsulta.REALIZADA
    ).count()
    
    return {
        "total_pacientes": total_pacientes,
        "total_medicos": total_medicos,
        "total_consultas": total_consultas,
        "consultas_hoje": consultas_hoje,
        "consultas_semana": consultas_semana,
        "consultas_mes": consultas_mes,
        "consultas_agendadas": consultas_agendadas,
        "consultas_realizadas": consultas_realizadas
    }

# ============ Médicos ============
@router.get("/medicos", response_model=List[MedicoResponse])
def listar_medicos(
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os médicos"""
    medicos = db.query(Medico).offset(skip).limit(limit).all()
    return medicos

@router.get("/medicos/{medico_id}", response_model=MedicoResponse)
def get_medico(
    medico_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retorna dados de um médico específico"""
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    return medico

@router.post("/medicos", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def criar_medico(
    medico_data: MedicoCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cadastra novo médico"""
    # Verificar se email já existe
    if db.query(Usuario).filter(Usuario.email == medico_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado no sistema"
        )
    
    # Verificar se CPF já existe
    if medico_data.cpf:
        cpf_limpo = medico_data.cpf.replace('.', '').replace('-', '').replace(' ', '')
        if db.query(Medico).filter(Medico.cpf == cpf_limpo).first():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF já cadastrado no sistema"
            )
    
    # Verificar se CRM já existe
    if db.query(Medico).filter(Medico.crm == medico_data.crm).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CRM já cadastrado no sistema"
        )
    
    # Verificar se especialidade existe
    especialidade = db.query(Especialidade).filter(Especialidade.id == medico_data.especialidade_id).first()
    if not especialidade:
        raise HTTPException(status_code=404, detail="Especialidade não encontrada")
    
    try:
        # Criar usuário
        novo_usuario = Usuario(
            email=medico_data.email,
            senha_hash=get_password_hash(medico_data.senha),
            nome=medico_data.nome,
            tipo=TipoUsuario.MEDICO
        )
        db.add(novo_usuario)
        db.flush()
        
        # Limpar CPF
        cpf_limpo = medico_data.cpf.replace('.', '').replace('-', '').replace(' ', '') if medico_data.cpf else None
        
        # Criar médico
        novo_medico = Medico(
            usuario_id=novo_usuario.id,
            cpf=cpf_limpo,
            crm=medico_data.crm,
            especialidade_id=medico_data.especialidade_id,
            telefone=medico_data.telefone,
            valor_consulta=medico_data.valor_consulta,
            tempo_consulta=medico_data.tempo_consulta
        )
        db.add(novo_medico)
        db.commit()
        db.refresh(novo_medico)
        
        return novo_medico
    
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'email' in error_msg or 'usuario_email_key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado no sistema"
            )
        elif 'crm' in error_msg or 'medico_crm_key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CRM já cadastrado no sistema"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao cadastrar médico: dados inválidos ou duplicados"
            )

@router.put("/medicos/{medico_id}", response_model=MedicoResponse)
def atualizar_medico(
    medico_id: int,
    medico_data: MedicoUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atualiza dados do médico"""
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Atualizar usuário
    if medico_data.nome:
        medico.usuario.nome = medico_data.nome
    
    # Atualizar médico
    for field, value in medico_data.dict(exclude_unset=True).items():
        if field != "nome" and value is not None:
            setattr(medico, field, value)
    
    db.commit()
    db.refresh(medico)
    return medico

@router.delete("/medicos/{medico_id}")
def deletar_medico(
    medico_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Desativa um médico"""
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    # Verificar se tem consultas futuras
    consultas_futuras = db.query(Consulta).filter(
        Consulta.medico_id == medico_id,
        Consulta.data >= date.today(),
        Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.CONFIRMADA])
    ).count()
    
    if consultas_futuras > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Médico possui {consultas_futuras} consultas futuras agendadas"
        )
    
    medico.usuario.ativo = False
    db.commit()
    
    return {"message": "Médico desativado com sucesso"}

@router.put("/medicos/{medico_id}/ativar")
def ativar_medico(
    medico_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reativa um médico"""
    medico = db.query(Medico).filter(Medico.id == medico_id).first()
    if not medico:
        raise HTTPException(status_code=404, detail="Médico não encontrado")
    
    medico.usuario.ativo = True
    db.commit()
    
    return {"message": "Médico reativado com sucesso"}

# ============ Pacientes ============
@router.get("/pacientes")
def listar_pacientes(
    skip: int = 0,
    limit: int = 100,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os pacientes com informações adicionais"""
    pacientes = db.query(Paciente).offset(skip).limit(limit).all()
    
    # Enriquecer dados com total de consultas e faltas
    resultado = []
    for paciente in pacientes:
        # Contar total de consultas
        total_consultas = db.query(Consulta).filter(
            Consulta.paciente_id == paciente.id
        ).count()
        
        # Contar faltas (status FALTOU)
        faltas = db.query(Consulta).filter(
            Consulta.paciente_id == paciente.id,
            Consulta.status == StatusConsulta.FALTOU
        ).count()
        
        # Serializar paciente
        paciente_dict = {
            "id": paciente.id,
            "usuario_id": paciente.usuario_id,
            "cpf": paciente.cpf,
            "data_nascimento": paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
            "convenio_id": paciente.convenio_id,
            "numero_carteirinha": paciente.numero_carteirinha,
            "faltas_consecutivas": paciente.faltas_consecutivas,
            "total_consultas": total_consultas,
            "faltas": faltas,
            "bloqueado": paciente.usuario.bloqueado if paciente.usuario else False,
            "usuario": {
                "id": paciente.usuario.id,
                "nome": paciente.usuario.nome,
                "email": paciente.usuario.email,
                "telefone": paciente.telefone,  # telefone está em Paciente
                "endereco": paciente.endereco,  # endereco está em Paciente
                "cidade": paciente.cidade,      # cidade está em Paciente
                "estado": paciente.estado,      # estado está em Paciente
                "cep": paciente.cep,            # cep está em Paciente
                "ativo": paciente.usuario.ativo,
                "bloqueado": paciente.usuario.bloqueado,
                "tipo": paciente.usuario.tipo.value,
            } if paciente.usuario else None,
            "convenio": {
                "id": paciente.convenio.id,
                "nome": paciente.convenio.nome,
                "ativo": paciente.convenio.ativo,
            } if paciente.convenio else None
        }
        resultado.append(paciente_dict)
    
    return resultado

@router.get("/pacientes/{paciente_id}")
def get_paciente(
    paciente_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Retorna dados detalhados de um paciente específico"""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Contar total de consultas
    total_consultas = db.query(Consulta).filter(
        Consulta.paciente_id == paciente.id
    ).count()
    
    # Contar faltas
    faltas = db.query(Consulta).filter(
        Consulta.paciente_id == paciente.id,
        Consulta.status == StatusConsulta.FALTOU
    ).count()
    
    # Serializar paciente com dados adicionais
    paciente_dict = {
        "id": paciente.id,
        "usuario_id": paciente.usuario_id,
        "cpf": paciente.cpf,
        "data_nascimento": paciente.data_nascimento.isoformat() if paciente.data_nascimento else None,
        "convenio_id": paciente.convenio_id,
        "numero_carteirinha": paciente.numero_carteirinha,
        "faltas_consecutivas": paciente.faltas_consecutivas,
        "total_consultas": total_consultas,
        "faltas": faltas,
        "bloqueado": paciente.usuario.bloqueado if paciente.usuario else False,
        "usuario": {
            "id": paciente.usuario.id,
            "nome": paciente.usuario.nome,
            "email": paciente.usuario.email,
            "telefone": paciente.telefone,  # telefone está em Paciente
            "endereco": paciente.endereco,  # endereco está em Paciente
            "cidade": paciente.cidade,      # cidade está em Paciente
            "estado": paciente.estado,      # estado está em Paciente
            "cep": paciente.cep,            # cep está em Paciente
            "ativo": paciente.usuario.ativo,
            "bloqueado": paciente.usuario.bloqueado,
            "tipo": paciente.usuario.tipo.value,
        } if paciente.usuario else None,
        "convenio": {
            "id": paciente.convenio.id,
            "nome": paciente.convenio.nome,
            "ativo": paciente.convenio.ativo,
        } if paciente.convenio else None
    }
    
    return paciente_dict

@router.put("/pacientes/{paciente_id}/bloquear")
def bloquear_paciente(
    paciente_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Bloqueia um paciente"""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    paciente.usuario.bloqueado = True
    db.commit()
    
    return {"message": "Paciente bloqueado com sucesso"}

@router.put("/pacientes/{paciente_id}/desbloquear")
def desbloquear_paciente(
    paciente_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Desbloqueia um paciente
    Caso de Uso: Desbloquear Contas de Pacientes
    Regra de Negócio: Se o paciente faltar a 3 consultas seguidas sem aviso, 
    o sistema deve bloquear novos agendamentos até liberação pela administração
    """
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    # Desbloquear usuário
    usuario = db.query(Usuario).filter(Usuario.id == paciente.usuario_id).first()
    if usuario:
        usuario.bloqueado = False
    
    # Zerar contador de faltas consecutivas
    paciente.faltas_consecutivas = 0
    
    db.commit()
    
    return {"message": "Paciente desbloqueado com sucesso"}
    """Desbloqueia um paciente"""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")
    
    paciente.usuario.bloqueado = False
    db.commit()
    
    return {"message": "Paciente desbloqueado com sucesso"}

# ============ Convênios ============
@router.get("/convenios", response_model=List[ConvenioResponse])
def listar_convenios(
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todos os convênios"""
    convenios = db.query(Convenio).all()
    return convenios

@router.post("/convenios", response_model=ConvenioResponse, status_code=status.HTTP_201_CREATED)
def criar_convenio(
    convenio_data: ConvenioCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cadastra novo convênio"""
    # Verificar se nome já existe
    if db.query(Convenio).filter(Convenio.nome == convenio_data.nome).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Convênio com este nome já cadastrado no sistema"
        )
    
    # Verificar se código já existe
    if db.query(Convenio).filter(Convenio.codigo == convenio_data.codigo).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Convênio com este código já cadastrado no sistema"
        )
    
    try:
        novo_convenio = Convenio(**convenio_data.dict())
        db.add(novo_convenio)
        db.commit()
        db.refresh(novo_convenio)
        
        return novo_convenio
    
    except IntegrityError as e:
        db.rollback()
        error_msg = str(e.orig).lower()
        
        if 'nome' in error_msg or 'convenio_nome_key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Convênio com este nome já cadastrado no sistema"
            )
        elif 'codigo' in error_msg or 'convenio_codigo_key' in error_msg:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Convênio com este código já cadastrado no sistema"
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Erro ao cadastrar convênio: dados inválidos ou duplicados"
            )

@router.put("/convenios/{convenio_id}", response_model=ConvenioResponse)
def atualizar_convenio(
    convenio_id: int,
    convenio_data: ConvenioUpdate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Atualiza convênio"""
    convenio = db.query(Convenio).filter(Convenio.id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convênio não encontrado")
    
    for field, value in convenio_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(convenio, field, value)
    
    db.commit()
    db.refresh(convenio)
    return convenio

@router.delete("/convenios/{convenio_id}")
def deletar_convenio(
    convenio_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Desativa um convênio"""
    convenio = db.query(Convenio).filter(Convenio.id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convênio não encontrado")
    
    convenio.ativo = False
    db.commit()
    
    return {"message": "Convênio desativado com sucesso"}

@router.put("/convenios/{convenio_id}/ativar")
def ativar_convenio(
    convenio_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Reativa um convênio"""
    convenio = db.query(Convenio).filter(Convenio.id == convenio_id).first()
    if not convenio:
        raise HTTPException(status_code=404, detail="Convênio não encontrado")
    
    convenio.ativo = True
    db.commit()
    
    return {"message": "Convênio reativado com sucesso"}

# ============ Especialidades ============
@router.get("/especialidades", response_model=List[EspecialidadeResponse])
def listar_especialidades(
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todas as especialidades"""
    especialidades = db.query(Especialidade).all()
    return especialidades

@router.post("/especialidades", response_model=EspecialidadeResponse, status_code=status.HTTP_201_CREATED)
def criar_especialidade(
    especialidade_data: EspecialidadeCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cadastra nova especialidade"""
    if db.query(Especialidade).filter(Especialidade.nome == especialidade_data.nome).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Especialidade já cadastrada"
        )
    
    nova_especialidade = Especialidade(**especialidade_data.dict())
    db.add(nova_especialidade)
    db.commit()
    db.refresh(nova_especialidade)
    
    return nova_especialidade

# ============ Consultas ============
@router.get("/consultas", response_model=List[ConsultaDetalhada])
def listar_consultas(
    data_inicio: date = None,
    data_fim: date = None,
    status_filtro: StatusConsulta = None,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista todas as consultas com filtros"""
    query = db.query(Consulta)
    
    if data_inicio:
        query = query.filter(Consulta.data >= data_inicio)
    if data_fim:
        query = query.filter(Consulta.data <= data_fim)
    if status_filtro:
        query = query.filter(Consulta.status == status_filtro)
    
    consultas = query.order_by(Consulta.data.desc(), Consulta.hora.desc()).limit(100).all()
    return consultas

# ============ Administradores ============
@router.post("/admins", response_model=AdminResponse, status_code=status.HTTP_201_CREATED)
def criar_admin(
    admin_data: AdminCreate,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cadastra novo administrador"""
    # Verificar se email já existe
    if db.query(Usuario).filter(Usuario.email == admin_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Criar usuário
    novo_usuario = Usuario(
        email=admin_data.email,
        senha_hash=get_password_hash(admin_data.senha),
        nome=admin_data.nome,
        tipo=TipoUsuario.ADMIN
    )
    db.add(novo_usuario)
    db.flush()
    
    # Criar admin
    novo_admin = Admin(
        usuario_id=novo_usuario.id,
        cargo=admin_data.cargo
    )
    db.add(novo_admin)
    db.commit()
    db.refresh(novo_admin)
    
    return novo_admin

# ============ Relatórios em PDF ============

@router.get("/relatorios/consultas-por-medico")
def relatorio_consultas_medico(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    formato: str = "json",
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de consultas por médico
    Caso de Uso: Gerar Relatórios em PDF - Quantidade de consultas por médico
    """
    admin = db.query(Admin).filter(Admin.usuario_id == current_user.id).first()
    
    dados_relatorio = gerar_relatorio_consultas_por_medico(db, data_inicio, data_fim)
    
    # Salvar no banco de dados
    novo_relatorio = RelatorioModel(
        admin_id=admin.id,
        tipo='consultas_por_medico',
        parametros=json.dumps({
            'data_inicio': data_inicio.isoformat() if data_inicio else None,
            'data_fim': data_fim.isoformat() if data_fim else None
        }),
        dados_resultado=json.dumps(dados_relatorio)
    )
    db.add(novo_relatorio)
    db.commit()
    
    if formato == "pdf":
        pdf_buffer = criar_pdf_relatorio(dados_relatorio)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_consultas_medico_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )
    
    return dados_relatorio

@router.get("/relatorios/consultas-por-especialidade")
def relatorio_consultas_especialidade(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    formato: str = "json",
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de consultas por especialidade
    Caso de Uso: Gerar Relatórios em PDF - Quantidade de consultas por especialidade
    """
    admin = db.query(Admin).filter(Admin.usuario_id == current_user.id).first()
    
    dados_relatorio = gerar_relatorio_consultas_por_especialidade(db, data_inicio, data_fim)
    
    # Salvar no banco de dados
    novo_relatorio = RelatorioModel(
        admin_id=admin.id,
        tipo='consultas_por_especialidade',
        parametros=json.dumps({
            'data_inicio': data_inicio.isoformat() if data_inicio else None,
            'data_fim': data_fim.isoformat() if data_fim else None
        }),
        dados_resultado=json.dumps(dados_relatorio)
    )
    db.add(novo_relatorio)
    db.commit()
    
    if formato == "pdf":
        pdf_buffer = criar_pdf_relatorio(dados_relatorio)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_consultas_especialidade_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )
    
    return dados_relatorio

@router.get("/relatorios/cancelamentos")
def relatorio_cancelamentos(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    formato: str = "json",
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de cancelamentos e remarcações
    Caso de Uso: Gerar Relatórios em PDF - Taxa de cancelamentos e remarcações
    """
    admin = db.query(Admin).filter(Admin.usuario_id == current_user.id).first()
    
    dados_relatorio = gerar_relatorio_cancelamentos(db, data_inicio, data_fim)
    
    # Salvar no banco de dados
    novo_relatorio = RelatorioModel(
        admin_id=admin.id,
        tipo='cancelamentos_remarcacoes',
        parametros=json.dumps({
            'data_inicio': data_inicio.isoformat() if data_inicio else None,
            'data_fim': data_fim.isoformat() if data_fim else None
        }),
        dados_resultado=json.dumps(dados_relatorio)
    )
    db.add(novo_relatorio)
    db.commit()
    
    if formato == "pdf":
        pdf_buffer = criar_pdf_relatorio(dados_relatorio)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_cancelamentos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )
    
    return dados_relatorio

@router.get("/relatorios/pacientes-frequentes")
def relatorio_pacientes_frequentes(
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    limite: int = 20,
    formato: str = "json",
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Gera relatório de pacientes que mais consultaram
    Caso de Uso: Gerar Relatórios em PDF - Pacientes que mais consultaram no período
    """
    admin = db.query(Admin).filter(Admin.usuario_id == current_user.id).first()
    
    dados_relatorio = gerar_relatorio_pacientes_frequentes(db, data_inicio, data_fim, limite)
    
    # Salvar no banco de dados
    novo_relatorio = RelatorioModel(
        admin_id=admin.id,
        tipo='pacientes_frequentes',
        parametros=json.dumps({
            'data_inicio': data_inicio.isoformat() if data_inicio else None,
            'data_fim': data_fim.isoformat() if data_fim else None,
            'limite': limite
        }),
        dados_resultado=json.dumps(dados_relatorio)
    )
    db.add(novo_relatorio)
    db.commit()
    
    if formato == "pdf":
        pdf_buffer = criar_pdf_relatorio(dados_relatorio)
        return StreamingResponse(
            pdf_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=relatorio_pacientes_frequentes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"}
        )
    
    return dados_relatorio

@router.get("/relatorios/historico", response_model=List[RelatorioResponse])
def historico_relatorios(
    skip: int = 0,
    limit: int = 50,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Lista histórico de relatórios gerados"""
    relatorios = db.query(RelatorioModel).order_by(
        RelatorioModel.data_geracao.desc()
    ).offset(skip).limit(limit).all()
    
    return relatorios

# ============ Observações (Acesso Admin) ============

@router.get("/observacoes/{consulta_id}", response_model=ObservacaoResponse)
def get_observacao_consulta(
    consulta_id: int,
    current_user: Usuario = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Visualiza observação de uma consulta
    Caso de Uso: Visualizar Observações da Consulta (Admin tem acesso)
    """
    consulta = db.query(Consulta).filter(Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    
    observacao = db.query(Observacao).filter(
        Observacao.consulta_id == consulta_id
    ).first()
    
    if not observacao:
        raise HTTPException(status_code=404, detail="Observação não encontrada")
    
    return observacao
