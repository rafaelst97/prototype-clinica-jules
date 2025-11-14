"""
Router de Administração - Sistema Clínica Saúde+
Implementa todos os casos de uso do módulo Administrativo conforme CasosDeUso.txt
Atualizado para modelo conforme MER
REFATORADO PARA JWT AUTHENTICATION
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func, and_, desc, case
from sqlalchemy.exc import IntegrityError
from typing import List
from datetime import date, datetime, timedelta
from app.database import get_db
from app.utils.auth import get_current_user, get_password_hash
from app.models.models import (
    Administrador, Medico, Paciente, Consulta, PlanoSaude, Especialidade,
    Relatorio, Observacao
)
from app.schemas.schemas import (
    AdministradorCreate, AdministradorResponse,
    MedicoCreate, MedicoUpdate, MedicoResponse,
    PacienteResponse,
    PlanoSaudeCreate, PlanoSaudeUpdate, PlanoSaudeResponse,
    EspecialidadeCreate, EspecialidadeResponse,
    EstatisticasDashboard,
    ConsultaResponse,
    RelatorioResponse,
    RelatorioConsultasPorMedico,
    RelatorioConsultasPorEspecialidade,
    RelatorioCancelamentos,
    RelatorioPacientesFrequentes,
    ObservacaoResponse
)
from app.services.regras_negocio import RegraPaciente

router = APIRouter(prefix="/admin", tags=["Administração"])


def verificar_admin(current_user: dict):
    """Helper para verificar se usuário é administrador"""
    if current_user["tipo"] != "administrador":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso."
        )


# ============ Dashboard e Estatísticas ============

@router.get("/dashboard", response_model=EstatisticasDashboard)
def get_dashboard(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais para o dashboard administrativo
    """
    verificar_admin(current_user)
    
    hoje = date.today()
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    inicio_mes = date(hoje.year, hoje.month, 1)
    
    # Estatísticas gerais
    total_pacientes = db.query(Paciente).count()
    total_medicos = db.query(Medico).count()
    total_consultas = db.query(Consulta).count()
    
    # Consultas por período
    consultas_hoje = db.query(Consulta).filter(
        func.date(Consulta.data_hora_inicio) == hoje
    ).count()
    
    consultas_semana = db.query(Consulta).filter(
        func.date(Consulta.data_hora_inicio) >= inicio_semana,
        func.date(Consulta.data_hora_inicio) <= hoje
    ).count()
    
    consultas_mes = db.query(Consulta).filter(
        func.extract('year', Consulta.data_hora_inicio) == hoje.year,
        func.extract('month', Consulta.data_hora_inicio) == hoje.month
    ).count()
    
    # Consultas por status
    consultas_agendadas = db.query(Consulta).filter(
        Consulta.status == "agendada"
    ).count()
    
    consultas_realizadas = db.query(Consulta).filter(
        Consulta.status == "realizada"
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


# ============ Gerenciamento de Médicos ============

@router.get("/medicos", response_model=List[MedicoResponse])
def listar_medicos(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Cadastro de Médicos (listar)
    Lista todos os médicos cadastrados
    """
    verificar_admin(current_user)
    
    medicos = db.query(Medico).options(
        joinedload(Medico.especialidade)
    ).all()
    
    return medicos


@router.get("/medicos/{medico_id}", response_model=MedicoResponse)
def get_medico(
    medico_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dados detalhados de um médico específico
    """
    verificar_admin(current_user)
    
    medico = db.query(Medico).options(
        joinedload(Medico.especialidade)
    ).filter(Medico.id_medico == medico_id).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    return medico


@router.post("/medicos", response_model=MedicoResponse, status_code=status.HTTP_201_CREATED)
def criar_medico(
    medico_data: MedicoCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Cadastro de Médicos (criar)
    Cadastra novo médico (nome, CRM, especialidade)
    """
    verificar_admin(current_user)
    
    # Verificar se email já existe
    email_existe = db.query(Medico).filter(Medico.email == medico_data.email).first()
    if email_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email já cadastrado no sistema"
        )
    
    # Verificar se CPF já existe
    cpf_existe = db.query(Medico).filter(Medico.cpf == medico_data.cpf).first()
    if cpf_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CPF já cadastrado no sistema"
        )
    
    # Verificar se CRM já existe
    crm_existe = db.query(Medico).filter(Medico.crm == medico_data.crm).first()
    if crm_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="CRM já cadastrado no sistema"
        )
    
    # Verificar se especialidade existe
    especialidade = db.query(Especialidade).filter(
        Especialidade.id_especialidade == medico_data.id_especialidade_fk
    ).first()
    if not especialidade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Especialidade não encontrada"
        )
    
    try:
        # Criar médico
        novo_medico = Medico(
            nome=medico_data.nome,
            cpf=medico_data.cpf,
            email=medico_data.email,
            senha_hash=get_password_hash(medico_data.senha),
            crm=medico_data.crm,
            telefone=medico_data.telefone,
            id_especialidade_fk=medico_data.id_especialidade_fk
        )
        
        db.add(novo_medico)
        db.commit()
        db.refresh(novo_medico)
        
        return novo_medico
    
    except IntegrityError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao cadastrar médico: dados inválidos ou duplicados"
        )


@router.put("/medicos/{medico_id}", response_model=MedicoResponse)
def atualizar_medico(
    medico_id: int,
    medico_data: MedicoUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Cadastro de Médicos (editar)
    Atualiza dados do médico
    """
    verificar_admin(current_user)
    
    # Debug: Log dos dados recebidos
    print(f"DEBUG: Dados recebidos para atualização: {medico_data.dict(exclude_unset=True)}")
    
    medico = db.query(Medico).filter(Medico.id_medico == medico_id).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Atualizar nome
    if medico_data.nome is not None:
        medico.nome = medico_data.nome
    
    # Atualizar CPF (verificar se já existe)
    if medico_data.cpf is not None:
        cpf_existe = db.query(Medico).filter(
            Medico.cpf == medico_data.cpf,
            Medico.id_medico != medico_id
        ).first()
        if cpf_existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CPF já cadastrado para outro médico"
            )
        medico.cpf = medico_data.cpf
    
    # Atualizar Email (verificar se já existe)
    if medico_data.email is not None:
        email_existe = db.query(Medico).filter(
            Medico.email == medico_data.email,
            Medico.id_medico != medico_id
        ).first()
        if email_existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email já cadastrado para outro médico"
            )
        medico.email = medico_data.email
    
    # Atualizar CRM (verificar se já existe)
    if medico_data.crm is not None:
        crm_existe = db.query(Medico).filter(
            Medico.crm == medico_data.crm,
            Medico.id_medico != medico_id
        ).first()
        if crm_existe:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="CRM já cadastrado para outro médico"
            )
        medico.crm = medico_data.crm
    
    # Atualizar senha
    if medico_data.senha is not None:
        medico.senha_hash = get_password_hash(medico_data.senha)
    
    # Atualizar telefone
    if medico_data.telefone is not None:
        medico.telefone = medico_data.telefone
    
    # Atualizar especialidade
    if medico_data.id_especialidade_fk is not None:
        # Verificar se especialidade existe
        especialidade = db.query(Especialidade).filter(
            Especialidade.id_especialidade == medico_data.id_especialidade_fk
        ).first()
        if not especialidade:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Especialidade não encontrada"
            )
        medico.id_especialidade_fk = medico_data.id_especialidade_fk
    
    try:
        db.commit()
        db.refresh(medico)
        return medico
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Erro ao atualizar médico: dados duplicados"
        )


@router.delete("/medicos/{medico_id}", status_code=status.HTTP_200_OK)
def excluir_medico(
    medico_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exclui médico do sistema
    Caso de Uso: Gerenciar Cadastro de Médicos (excluir)
    """
    verificar_admin(current_user)
    
    medico = db.query(Medico).filter(Medico.id_medico == medico_id).first()
    
    if not medico:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Médico não encontrado"
        )
    
    # Verificar se médico tem consultas
    tem_consultas = db.query(Consulta).filter(Consulta.id_medico_fk == medico_id).first()
    if tem_consultas:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível excluir médico com consultas cadastradas"
        )
    
    db.delete(medico)
    db.commit()
    
    return {
        "sucesso": True,
        "mensagem": "Médico excluído com sucesso"
    }


# ============ Gerenciamento de Pacientes ============

@router.get("/pacientes", response_model=List[dict])
def listar_pacientes(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todos os pacientes cadastrados com estatísticas de consultas
    """
    verificar_admin(current_user)
    
    pacientes = db.query(Paciente).options(
        joinedload(Paciente.plano_saude)
    ).all()
    
    # Adicionar estatísticas de consultas para cada paciente
    resultado = []
    for paciente in pacientes:
        # Contar total de consultas realizadas
        total_consultas = db.query(Consulta).filter(
            Consulta.id_paciente_fk == paciente.id_paciente,
            Consulta.status == 'realizada'
        ).count()
        
        # Contar consultas agendadas (futuras)
        consultas_agendadas = db.query(Consulta).filter(
            Consulta.id_paciente_fk == paciente.id_paciente,
            Consulta.status == 'agendada'
        ).count()
        
        # Serializar plano_saude se existir
        plano_saude_dict = None
        if paciente.plano_saude:
            plano_saude_dict = {
                'id_plano_saude': paciente.plano_saude.id_plano_saude,
                'nome': paciente.plano_saude.nome,
                'cobertura_info': paciente.plano_saude.cobertura_info
            }
        
        paciente_dict = {
            'id_paciente': paciente.id_paciente,
            'nome': paciente.nome,
            'cpf': paciente.cpf,
            'email': paciente.email,
            'telefone': paciente.telefone,
            'data_nascimento': paciente.data_nascimento.isoformat(),
            'esta_bloqueado': paciente.esta_bloqueado,
            'id_plano_saude_fk': paciente.id_plano_saude_fk,
            'plano_saude': plano_saude_dict,
            'total_consultas': total_consultas,
            'consultas_agendadas': consultas_agendadas
        }
        resultado.append(paciente_dict)
    
    return resultado


@router.get("/pacientes/{paciente_id}", response_model=PacienteResponse)
def get_paciente(
    paciente_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna dados detalhados de um paciente
    """
    verificar_admin(current_user)
    
    paciente = db.query(Paciente).options(
        joinedload(Paciente.plano_saude)
    ).filter(Paciente.id_paciente == paciente_id).first()
    
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    return paciente


@router.post("/pacientes/{paciente_id}/bloquear", response_model=PacienteResponse)
def bloquear_paciente(
    paciente_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Bloqueia um paciente
    """
    verificar_admin(current_user)
    
    paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    paciente.esta_bloqueado = True
    db.commit()
    db.refresh(paciente)
    
    return paciente


@router.post("/pacientes/{paciente_id}/desbloquear", response_model=PacienteResponse)
def desbloquear_paciente(
    paciente_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Desbloquear Contas de Pacientes
    RN3: Administrador pode desbloquear pacientes bloqueados por 3 faltas consecutivas
    """
    verificar_admin(current_user)
    
    paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
    if not paciente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paciente não encontrado"
        )
    
    paciente.esta_bloqueado = False
    paciente.faltas_consecutivas = 0
    db.commit()
    db.refresh(paciente)
    
    return paciente


# ============ Gerenciamento de Consultas ============

@router.get("/consultas", response_model=List[ConsultaResponse])
def listar_consultas(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Lista todas as consultas do sistema
    """
    verificar_admin(current_user)
    
    consultas = db.query(Consulta).options(
        joinedload(Consulta.paciente),
        joinedload(Consulta.medico).joinedload(Medico.especialidade)
    ).all()
    
    return consultas


# ============ Gerenciamento de Planos de Saúde ============

@router.get("/planos-saude", response_model=List[PlanoSaudeResponse])
def listar_planos_saude(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Planos de Saúde (listar)
    Lista todos os planos de saúde cadastrados
    """
    verificar_admin(current_user)
    
    planos = db.query(PlanoSaude).all()
    return planos


@router.get("/planos-saude/estatisticas")
def listar_planos_saude_com_estatisticas(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Planos de Saúde (listar com estatísticas)
    Lista todos os planos de saúde com estatísticas de pacientes e consultas
    """
    verificar_admin(current_user)
    
    planos = db.query(PlanoSaude).all()
    
    resultado = []
    total_pacientes = db.query(Paciente).count()
    
    for plano in planos:
        # Contar pacientes cadastrados neste plano
        qtd_pacientes = db.query(Paciente).filter(
            Paciente.id_plano_saude_fk == plano.id_plano_saude
        ).count()
        
        # Contar consultas do mês atual para pacientes deste plano
        from datetime import datetime
        primeiro_dia_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        consultas_mes = db.query(Consulta).join(
            Paciente, Paciente.id_paciente == Consulta.id_paciente_fk
        ).filter(
            Paciente.id_plano_saude_fk == plano.id_plano_saude,
            Consulta.data_hora_inicio >= primeiro_dia_mes
        ).count()
        
        # Calcular percentual de pacientes
        percentual = (qtd_pacientes / total_pacientes * 100) if total_pacientes > 0 else 0
        
        resultado.append({
            "id_plano_saude": plano.id_plano_saude,
            "nome": plano.nome,
            "cobertura_info": plano.cobertura_info,
            "qtd_pacientes": qtd_pacientes,
            "percentual_pacientes": round(percentual, 1),
            "consultas_mes": consultas_mes
        })
    
    return resultado


@router.post("/planos-saude", response_model=PlanoSaudeResponse, status_code=status.HTTP_201_CREATED)
def criar_plano_saude(
    plano_data: PlanoSaudeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Planos de Saúde (criar)
    Cadastra novo plano de saúde
    """
    verificar_admin(current_user)
    
    # Verificar se já existe plano com este nome
    plano_existe = db.query(PlanoSaude).filter(PlanoSaude.nome == plano_data.nome).first()
    if plano_existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe um plano de saúde com este nome"
        )
    
    novo_plano = PlanoSaude(
        nome=plano_data.nome,
        cobertura_info=plano_data.cobertura_info
    )
    
    db.add(novo_plano)
    db.commit()
    db.refresh(novo_plano)
    
    return novo_plano


@router.put("/planos-saude/{plano_id}", response_model=PlanoSaudeResponse)
def atualizar_plano_saude(
    plano_id: int,
    plano_data: PlanoSaudeUpdate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerenciar Planos de Saúde (editar)
    Atualiza dados do plano de saúde
    """
    verificar_admin(current_user)
    
    plano = db.query(PlanoSaude).filter(PlanoSaude.id_plano_saude == plano_id).first()
    
    if not plano:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de saúde não encontrado"
        )
    
    if plano_data.nome is not None:
        plano.nome = plano_data.nome
    if plano_data.cobertura_info is not None:
        plano.cobertura_info = plano_data.cobertura_info
    
    db.commit()
    db.refresh(plano)
    
    return plano


@router.delete("/planos-saude/{plano_id}", status_code=status.HTTP_200_OK)
def excluir_plano_saude(
    plano_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Exclui plano de saúde
    """
    verificar_admin(current_user)
    
    plano = db.query(PlanoSaude).filter(PlanoSaude.id_plano_saude == plano_id).first()
    
    if not plano:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Plano de saúde não encontrado"
        )
    
    # Verificar se há pacientes vinculados
    pacientes_com_plano = db.query(Paciente).filter(
        Paciente.id_plano_saude_fk == plano_id
    ).count()
    
    if pacientes_com_plano > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Não é possível excluir plano com {pacientes_com_plano} paciente(s) vinculado(s)"
        )
    
    db.delete(plano)
    db.commit()
    
    return {
        "sucesso": True,
        "mensagem": "Plano de saúde excluído com sucesso"
    }


# ============ Gerenciamento de Especialidades ============

@router.get("/especialidades", response_model=List[EspecialidadeResponse])
def listar_especialidades(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Lista todas as especialidades"""
    verificar_admin(current_user)
    
    especialidades = db.query(Especialidade).all()
    return especialidades


@router.post("/especialidades", response_model=EspecialidadeResponse, status_code=status.HTTP_201_CREATED)
def criar_especialidade(
    especialidade_data: EspecialidadeCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cadastra nova especialidade médica"""
    verificar_admin(current_user)
    
    # Verificar se já existe
    existe = db.query(Especialidade).filter(
        Especialidade.nome == especialidade_data.nome
    ).first()
    
    if existe:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Especialidade já cadastrada"
        )
    
    nova_especialidade = Especialidade(nome=especialidade_data.nome)
    db.add(nova_especialidade)
    db.commit()
    db.refresh(nova_especialidade)
    
    return nova_especialidade


# ============ Visualização de Observações ============

@router.get("/observacoes/{consulta_id}", response_model=ObservacaoResponse)
def visualizar_observacao(
    consulta_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Visualizar Observações da Consulta
    Administrador pode visualizar observações de qualquer consulta
    """
    verificar_admin(current_user)
    
    # Verificar se consulta existe
    consulta = db.query(Consulta).filter(Consulta.id_consulta == consulta_id).first()
    if not consulta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consulta não encontrada"
        )
    
    # Buscar observação
    observacao = db.query(Observacao).filter(
        Observacao.id_consulta_fk == consulta_id
    ).first()
    
    if not observacao:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Nenhuma observação encontrada para esta consulta"
        )
    
    return observacao


# ============ Relatórios ============

@router.get("/relatorios/consultas-por-medico")
def relatorio_consultas_por_medico(
    medico_id: int = None,
    data_inicio: date = None,
    data_fim: date = None,
    formato: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerar Relatórios em PDF
    Relatório: Quantidade de consultas por médico
    """
    verificar_admin(current_user)
    
    query = db.query(
        Medico.nome.label("medico_nome"),
        Especialidade.nome.label("especialidade"),
        func.count(Consulta.id_consulta).label("total_consultas"),
        func.sum(case((Consulta.status == "realizada", 1), else_=0)).label("consultas_realizadas"),
        func.sum(case((Consulta.status == "cancelada", 1), else_=0)).label("consultas_canceladas")
    ).join(
        Consulta, Consulta.id_medico_fk == Medico.id_medico
    ).join(
        Especialidade, Especialidade.id_especialidade == Medico.id_especialidade_fk
    )
    
    # Filtro por médico específico
    if medico_id:
        query = query.filter(Medico.id_medico == medico_id)
    
    if data_inicio:
        query = query.filter(func.date(Consulta.data_hora_inicio) >= data_inicio)
    if data_fim:
        query = query.filter(func.date(Consulta.data_hora_inicio) <= data_fim)
    
    resultados = query.group_by(
        Medico.id_medico, Medico.nome, Especialidade.nome
    ).all()
    
    dados = [
        {
            "medico_nome": r.medico_nome,
            "especialidade": r.especialidade,
            "total_consultas": r.total_consultas,
            "consultas_realizadas": r.consultas_realizadas or 0,
            "consultas_canceladas": r.consultas_canceladas or 0
        }
        for r in resultados
    ]
    
    # Se solicitado PDF, gera e retorna
    if formato == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph("<b>Relatório de Consultas por Médico</b>", styles['Title'])
        elements.append(titulo)
        elements.append(Spacer(1, 0.5*cm))
        
        # Período
        periodo_texto = "Período: "
        if data_inicio and data_fim:
            periodo_texto += f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elif data_inicio:
            periodo_texto += f"A partir de {data_inicio.strftime('%d/%m/%Y')}"
        elif data_fim:
            periodo_texto += f"Até {data_fim.strftime('%d/%m/%Y')}"
        else:
            periodo_texto += "Todos os registros"
        
        elements.append(Paragraph(periodo_texto, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabela
        table_data = [['Médico', 'Especialidade', 'Total', 'Realizadas', 'Canceladas']]
        for d in dados:
            table_data.append([
                d['medico_nome'],
                d['especialidade'],
                str(d['total_consultas']),
                str(d['consultas_realizadas']),
                str(d['consultas_canceladas'])
            ])
        
        table = Table(table_data, colWidths=[6*cm, 4*cm, 2*cm, 2*cm, 2*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=relatorio_consultas_medico.pdf"}
        )
    
    return dados


@router.get("/relatorios/consultas-por-especialidade")
def relatorio_consultas_por_especialidade(
    especialidade_id: int = None,
    data_inicio: date = None,
    data_fim: date = None,
    formato: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerar Relatórios em PDF
    Relatório: Quantidade de consultas por especialidade
    """
    verificar_admin(current_user)
    
    query = db.query(
        Especialidade.nome.label("especialidade"),
        func.count(Consulta.id_consulta).label("total_consultas"),
        func.count(func.distinct(Medico.id_medico)).label("total_medicos")
    ).join(
        Medico, Medico.id_especialidade_fk == Especialidade.id_especialidade
    ).join(
        Consulta, Consulta.id_medico_fk == Medico.id_medico
    )
    
    # Filtro por especialidade específica
    if especialidade_id:
        query = query.filter(Especialidade.id_especialidade == especialidade_id)
    
    if data_inicio:
        query = query.filter(func.date(Consulta.data_hora_inicio) >= data_inicio)
    if data_fim:
        query = query.filter(func.date(Consulta.data_hora_inicio) <= data_fim)
    
    resultados = query.group_by(Especialidade.id_especialidade, Especialidade.nome).all()
    
    dados = [
        {
            "especialidade": r.especialidade,
            "total_consultas": r.total_consultas,
            "total_medicos": r.total_medicos
        }
        for r in resultados
    ]
    
    # Se solicitado PDF, gera e retorna
    if formato == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph("<b>Relatório de Consultas por Especialidade</b>", styles['Title'])
        elements.append(titulo)
        elements.append(Spacer(1, 0.5*cm))
        
        # Período
        periodo_texto = "Período: "
        if data_inicio and data_fim:
            periodo_texto += f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elif data_inicio:
            periodo_texto += f"A partir de {data_inicio.strftime('%d/%m/%Y')}"
        elif data_fim:
            periodo_texto += f"Até {data_fim.strftime('%d/%m/%Y')}"
        else:
            periodo_texto += "Todos os registros"
        
        elements.append(Paragraph(periodo_texto, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabela
        table_data = [['Especialidade', 'Total de Consultas', 'Médicos Atuantes']]
        for d in dados:
            table_data.append([
                d['especialidade'],
                str(d['total_consultas']),
                str(d['total_medicos'])
            ])
        
        table = Table(table_data, colWidths=[8*cm, 4*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=relatorio_consultas_especialidade.pdf"}
        )
    
    return dados


@router.get("/relatorios/cancelamentos")
def relatorio_cancelamentos(
    data_inicio: date = None,
    data_fim: date = None,
    formato: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerar Relatórios em PDF
    Relatório: Taxa de cancelamentos e remarcações
    """
    verificar_admin(current_user)
    
    query = db.query(Consulta)
    
    if data_inicio:
        query = query.filter(func.date(Consulta.data_hora_inicio) >= data_inicio)
    if data_fim:
        query = query.filter(func.date(Consulta.data_hora_inicio) <= data_fim)
    
    total_consultas = query.count()
    total_cancelamentos = query.filter(Consulta.status == "cancelada").count()
    
    taxa_cancelamento = (total_cancelamentos / total_consultas * 100) if total_consultas > 0 else 0
    
    dados = {
        "total_consultas": total_consultas,
        "total_cancelamentos": total_cancelamentos,
        "taxa_cancelamento": round(taxa_cancelamento, 2)
    }
    
    # Se solicitado PDF, gera e retorna
    if formato == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph("<b>Relatório de Taxa de Cancelamentos</b>", styles['Title'])
        elements.append(titulo)
        elements.append(Spacer(1, 0.5*cm))
        
        # Período
        periodo_texto = "Período: "
        if data_inicio and data_fim:
            periodo_texto += f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elif data_inicio:
            periodo_texto += f"A partir de {data_inicio.strftime('%d/%m/%Y')}"
        elif data_fim:
            periodo_texto += f"Até {data_fim.strftime('%d/%m/%Y')}"
        else:
            periodo_texto += "Todos os registros"
        
        elements.append(Paragraph(periodo_texto, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabela
        table_data = [
            ['Métrica', 'Valor'],
            ['Total de Consultas', str(dados['total_consultas'])],
            ['Total de Cancelamentos', str(dados['total_cancelamentos'])],
            ['Taxa de Cancelamento', f"{dados['taxa_cancelamento']}%"]
        ]
        
        table = Table(table_data, colWidths=[8*cm, 4*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=relatorio_cancelamentos.pdf"}
        )
    
    return dados


@router.get("/relatorios/pacientes-frequentes")
def relatorio_pacientes_frequentes(
    data_inicio: date = None,
    data_fim: date = None,
    limite: int = 10,
    formato: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Caso de Uso: Gerar Relatórios em PDF
    Relatório: Pacientes que mais consultaram no período
    """
    verificar_admin(current_user)
    
    query = db.query(
        Paciente.nome.label("paciente_nome"),
        Paciente.cpf,
        func.count(Consulta.id_consulta).label("total_consultas"),
        func.max(Consulta.data_hora_inicio).label("ultima_consulta")
    ).join(
        Consulta, Consulta.id_paciente_fk == Paciente.id_paciente
    )
    
    if data_inicio:
        query = query.filter(func.date(Consulta.data_hora_inicio) >= data_inicio)
    if data_fim:
        query = query.filter(func.date(Consulta.data_hora_inicio) <= data_fim)
    
    resultados = query.group_by(
        Paciente.id_paciente, Paciente.nome, Paciente.cpf
    ).order_by(
        desc(func.count(Consulta.id_consulta))
    ).limit(limite).all()
    
    dados = [
        {
            "paciente_nome": r.paciente_nome,
            "cpf": r.cpf,
            "total_consultas": r.total_consultas,
            "ultima_consulta": r.ultima_consulta.strftime('%d/%m/%Y') if r.ultima_consulta else 'N/A'
        }
        for r in resultados
    ]
    
    # Se solicitado PDF, gera e retorna
    if formato == "pdf":
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet
        from io import BytesIO
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        elements = []
        styles = getSampleStyleSheet()
        
        # Título
        titulo = Paragraph(f"<b>Relatório de Pacientes Mais Frequentes (Top {limite})</b>", styles['Title'])
        elements.append(titulo)
        elements.append(Spacer(1, 0.5*cm))
        
        # Período
        periodo_texto = "Período: "
        if data_inicio and data_fim:
            periodo_texto += f"{data_inicio.strftime('%d/%m/%Y')} a {data_fim.strftime('%d/%m/%Y')}"
        elif data_inicio:
            periodo_texto += f"A partir de {data_inicio.strftime('%d/%m/%Y')}"
        elif data_fim:
            periodo_texto += f"Até {data_fim.strftime('%d/%m/%Y')}"
        else:
            periodo_texto += "Todos os registros"
        
        elements.append(Paragraph(periodo_texto, styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))
        
        # Tabela
        table_data = [['Posição', 'Paciente', 'CPF', 'Total de Consultas', 'Última Consulta']]
        for idx, d in enumerate(dados, 1):
            table_data.append([
                str(idx),
                d['paciente_nome'],
                d['cpf'],
                str(d['total_consultas']),
                d['ultima_consulta']
            ])
        
        table = Table(table_data, colWidths=[1.5*cm, 5*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        elements.append(table)
        doc.build(elements)
        
        buffer.seek(0)
        return StreamingResponse(
            buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": "inline; filename=relatorio_pacientes_frequentes.pdf"}
        )
    
    return dados


@router.get("/relatorios/estatisticas-gerais")
def get_estatisticas_gerais(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retorna estatísticas gerais para dashboard de relatórios
    """
    verificar_admin(current_user)
    
    # Total de consultas por status
    total_consultas = db.query(Consulta).count()
    realizadas = db.query(Consulta).filter(Consulta.status == 'realizada').count()
    agendadas = db.query(Consulta).filter(Consulta.status == 'agendada').count()
    canceladas = db.query(Consulta).filter(Consulta.status == 'cancelada').count()
    
    # Percentuais
    perc_realizadas = (realizadas / total_consultas * 100) if total_consultas > 0 else 0
    perc_agendadas = (agendadas / total_consultas * 100) if total_consultas > 0 else 0
    perc_canceladas = (canceladas / total_consultas * 100) if total_consultas > 0 else 0
    
    # Especialidades mais procuradas
    especialidades_query = db.query(
        Especialidade.nome,
        func.count(Consulta.id_consulta).label('total')
    ).join(
        Medico, Medico.id_especialidade_fk == Especialidade.id_especialidade
    ).join(
        Consulta, Consulta.id_medico_fk == Medico.id_medico
    ).group_by(
        Especialidade.nome
    ).order_by(
        desc('total')
    ).limit(3).all()
    
    especialidades_top = [
        {"nome": esp.nome, "total": esp.total}
        for esp in especialidades_query
    ]
    
    return {
        "total_consultas": total_consultas,
        "realizadas": realizadas,
        "perc_realizadas": round(perc_realizadas, 2),
        "agendadas": agendadas,
        "perc_agendadas": round(perc_agendadas, 2),
        "canceladas": canceladas,
        "perc_canceladas": round(perc_canceladas, 2),
        "especialidades_top": especialidades_top
    }
