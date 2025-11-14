from datetime import datetime, date, timedelta, time
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import Consulta, HorarioTrabalho, Paciente
import re


def validar_cpf(cpf: str) -> bool:
    """Valida formato do CPF (11 dígitos)"""
    if not cpf:
        return False
    
    # Verifica se tem apenas dígitos, pontos, hífen e espaços válidos do formato
    # Formato válido: 123.456.789-00 ou 12345678900
    if not re.match(r'^[\d\.\-]+$', str(cpf)):
        return False
    
    # Remove caracteres não numéricos
    cpf_limpo = re.sub(r'\D', '', str(cpf))
    
    # Verifica se tem 11 dígitos
    if len(cpf_limpo) != 11:
        return False
    
    # Verifica se não é uma sequência de números iguais
    if cpf_limpo == cpf_limpo[0] * 11:
        return False
    
    return True


def validar_email(email: str) -> bool:
    """Valida formato de email"""
    if not email:
        return False
    
    # Regex simples para validação de email
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validar_telefone(telefone: str) -> bool:
    """Valida formato de telefone brasileiro (10 ou 11 dígitos)"""
    if not telefone:
        return False
    
    # Remove caracteres não numéricos
    telefone_limpo = re.sub(r'\D', '', str(telefone))
    
    # Verifica se tem 10 (fixo) ou 11 (celular) dígitos
    return len(telefone_limpo) in [10, 11]


def validar_senha_alfanumerica(senha: str) -> bool:
    """
    Valida senha alfanumérica conforme requisitos:
    - 8 a 20 caracteres
    - Deve conter letras E números
    """
    if not senha:
        return False
    
    # Verifica tamanho
    if len(senha) < 8 or len(senha) > 20:
        return False
    
    # Verifica se tem letras
    tem_letra = any(c.isalpha() for c in senha)
    
    # Verifica se tem números
    tem_numero = any(c.isdigit() for c in senha)
    
    # Verifica se não tem espaços
    tem_espaco = ' ' in senha
    
    return tem_letra and tem_numero and not tem_espaco

def validar_limite_consultas(db: Session, paciente_id: int) -> bool:
    """Verifica se o paciente tem menos de 2 consultas agendadas (Regra de Negócio)"""
    consultas_ativas = db.query(Consulta).filter(
        Consulta.paciente_id == paciente_id,
        Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.CONFIRMADA]),
        Consulta.data >= date.today()
    ).count()
    
    return consultas_ativas < 2

def validar_cancelamento_24h(consulta: Consulta) -> bool:
    """Verifica se a consulta pode ser cancelada (mais de 24h de antecedência - Regra de Negócio)"""
    data_consulta = datetime.combine(consulta.data, consulta.hora)
    agora = datetime.now()
    diferenca = data_consulta - agora
    
    return diferenca.total_seconds() > 24 * 3600

def verificar_paciente_bloqueado(db: Session, paciente_id: int) -> bool:
    """Verifica se o paciente está bloqueado por 3 faltas consecutivas (Regra de Negócio)"""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        return True
    
    usuario = db.query(Usuario).filter(Usuario.id == paciente.usuario_id).first()
    if not usuario:
        return True
    
    # Verifica se está bloqueado pela administração ou por faltas consecutivas
    return usuario.bloqueado or paciente.faltas_consecutivas >= 3

def atualizar_faltas_consecutivas(db: Session, paciente_id: int, compareceu: bool):
    """Atualiza o contador de faltas consecutivas do paciente"""
    paciente = db.query(Paciente).filter(Paciente.id == paciente_id).first()
    if not paciente:
        return
    
    if compareceu:
        # Se compareceu, zera as faltas consecutivas
        paciente.faltas_consecutivas = 0
    else:
        # Se faltou, incrementa as faltas
        paciente.faltas_consecutivas += 1
        
        # Se atingiu 3 faltas, bloqueia o usuário
        if paciente.faltas_consecutivas >= 3:
            usuario = db.query(Usuario).filter(Usuario.id == paciente.usuario_id).first()
            if usuario:
                usuario.bloqueado = True
    
    db.commit()

def verificar_conflito_horario(
    db: Session,
    medico_id: int,
    data: date,
    hora: time,
    excluir_consulta_id: int = None
) -> bool:
    """
    Verifica se já existe uma consulta no mesmo horário
    excluir_consulta_id: ID da consulta a ser excluída da verificação (usado em reagendamento)
    """
    query = db.query(Consulta).filter(
        Consulta.medico_id == medico_id,
        Consulta.data == data,
        Consulta.hora == hora,
        Consulta.status.in_([StatusConsulta.AGENDADA, StatusConsulta.CONFIRMADA])
    )
    
    # Se fornecido, exclui a consulta especificada da verificação
    if excluir_consulta_id:
        query = query.filter(Consulta.id != excluir_consulta_id)
    
    conflito = query.first()
    
    return conflito is not None

def verificar_horario_bloqueado(
    db: Session,
    medico_id: int,
    data: date,
    hora: time
) -> bool:
    """Verifica se o horário está bloqueado pelo médico"""
    bloqueio = db.query(BloqueioHorario).filter(
        BloqueioHorario.medico_id == medico_id,
        BloqueioHorario.data == data,
        BloqueioHorario.hora_inicio <= hora,
        BloqueioHorario.hora_fim > hora
    ).first()
    
    return bloqueio is not None

def verificar_horario_disponivel(
    db: Session,
    medico_id: int,
    data: date,
    hora: time
) -> bool:
    """Verifica se o horário está na grade de disponibilidade do médico"""
    dia_semana = data.weekday()  # 0=Monday, 6=Sunday
    
    horario = db.query(HorarioDisponivel).filter(
        HorarioDisponivel.medico_id == medico_id,
        HorarioDisponivel.dia_semana == dia_semana,
        HorarioDisponivel.hora_inicio <= hora,
        HorarioDisponivel.hora_fim > hora,
        HorarioDisponivel.ativo == True
    ).first()
    
    return horario is not None

def gerar_horarios_disponiveis(
    db: Session,
    medico_id: int,
    data: date,
    tempo_consulta: int = 30
) -> List[str]:
    """Gera lista de horários disponíveis para uma data específica"""
    dia_semana = data.weekday()
    
    # Buscar grade de horários do médico para esse dia
    horarios_config = db.query(HorarioDisponivel).filter(
        HorarioDisponivel.medico_id == medico_id,
        HorarioDisponivel.dia_semana == dia_semana,
        HorarioDisponivel.ativo == True
    ).all()
    
    if not horarios_config:
        return []
    
    horarios_disponiveis = []
    
    for config in horarios_config:
        hora_atual = datetime.combine(date.today(), config.hora_inicio)
        hora_fim = datetime.combine(date.today(), config.hora_fim)
        
        while hora_atual < hora_fim:
            hora_time = hora_atual.time()
            
            # Verificar se não está bloqueado
            if not verificar_horario_bloqueado(db, medico_id, data, hora_time):
                # Verificar se não tem conflito
                if not verificar_conflito_horario(db, medico_id, data, hora_time):
                    horarios_disponiveis.append(hora_time.strftime("%H:%M"))
            
            hora_atual += timedelta(minutes=tempo_consulta)
    
    return sorted(horarios_disponiveis)
