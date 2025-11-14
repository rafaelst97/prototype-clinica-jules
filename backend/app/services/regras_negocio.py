"""
Serviços de Regras de Negócio - Clínica Saúde+
Implementa todas as regras de negócio especificadas no EstudoDeCaso.txt
"""
from datetime import datetime, timedelta, date
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from app.models.models import Consulta, Paciente, Medico, HorarioTrabalho
from typing import List, Optional


class RegraConsulta:
    """
    Regras de Negócio para Consultas conforme EstudoDeCaso.txt
    """
    
    @staticmethod
    def validar_cancelamento_24h(consulta: Consulta) -> tuple[bool, str]:
        """
        RN1: Consultas só podem ser canceladas/remarcadas até 24h antes do horário agendado
        
        Args:
            consulta: Objeto da consulta
            
        Returns:
            tuple: (pode_cancelar: bool, mensagem: str)
        """
        agora = datetime.now()
        limite_cancelamento = consulta.data_hora_inicio - timedelta(hours=24)
        
        if agora > limite_cancelamento:
            horas_faltando = (consulta.data_hora_inicio - agora).total_seconds() / 3600
            return False, f"Cancelamento não permitido. Só é possível cancelar até 24h antes da consulta. Faltam apenas {horas_faltando:.1f} horas."
        
        return True, "Cancelamento permitido"
    
    @staticmethod
    def validar_reagendamento_24h(consulta: Consulta) -> tuple[bool, str]:
        """
        RN1: Consultas só podem ser canceladas/remarcadas até 24h antes do horário agendado
        
        Args:
            consulta: Objeto da consulta
            
        Returns:
            tuple: (pode_reagendar: bool, mensagem: str)
        """
        return RegraConsulta.validar_cancelamento_24h(consulta)
    
    @staticmethod
    def validar_limite_consultas_futuras(db: Session, paciente_id: int) -> tuple[bool, str]:
        """
        RN2: Cada paciente pode ter no máximo 2 consultas futuras agendadas por vez
        
        Args:
            db: Sessão do banco de dados
            paciente_id: ID do paciente
            
        Returns:
            tuple: (pode_agendar: bool, mensagem: str)
        """
        agora = datetime.now()
        
        consultas_futuras = db.query(Consulta).filter(
            and_(
                Consulta.id_paciente_fk == paciente_id,
                Consulta.data_hora_inicio > agora,
                Consulta.status.in_(['agendada', 'confirmada'])
            )
        ).count()
        
        if consultas_futuras >= 2:
            return False, f"Limite de consultas futuras atingido. Você já possui {consultas_futuras} consultas agendadas. Máximo permitido: 2."
        
        return True, f"Você pode agendar mais {2 - consultas_futuras} consulta(s)"
    
    @staticmethod
    def validar_conflito_horario_medico(
        db: Session,
        medico_id: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime,
        consulta_id_ignorar: Optional[int] = None
    ) -> tuple[bool, str]:
        """
        RN4: O sistema deve evitar conflitos de agendamento para o médico
        
        Args:
            db: Sessão do banco de dados
            medico_id: ID do médico
            data_hora_inicio: Data/hora de início da nova consulta
            data_hora_fim: Data/hora de fim da nova consulta
            consulta_id_ignorar: ID da consulta a ignorar (útil para reagendamento)
            
        Returns:
            tuple: (sem_conflito: bool, mensagem: str)
        """
        query = db.query(Consulta).filter(
            and_(
                Consulta.id_medico_fk == medico_id,
                Consulta.status.in_(['agendada', 'confirmada']),
                # Verifica sobreposição de horários
                Consulta.data_hora_inicio < data_hora_fim,
                Consulta.data_hora_fim > data_hora_inicio
            )
        )
        
        if consulta_id_ignorar:
            query = query.filter(Consulta.id_consulta != consulta_id_ignorar)
        
        conflito = query.first()
        
        if conflito:
            return False, f"Horário indisponível. O médico já possui consulta agendada das {conflito.data_hora_inicio.strftime('%H:%M')} às {conflito.data_hora_fim.strftime('%H:%M')}."
        
        return True, "Horário disponível"
    
    @staticmethod
    def validar_horario_trabalho_medico(
        db: Session,
        medico_id: int,
        data_hora_inicio: datetime
    ) -> tuple[bool, str]:
        """
        RN: Cada médico define seus horários disponíveis semanalmente
        
        Args:
            db: Sessão do banco de dados
            medico_id: ID do médico
            data_hora_inicio: Data/hora de início da consulta
            
        Returns:
            tuple: (esta_no_horario: bool, mensagem: str)
        """
        dia_semana = data_hora_inicio.weekday()  # 0=Segunda, 6=Domingo
        hora = data_hora_inicio.time()
        
        horario_trabalho = db.query(HorarioTrabalho).filter(
            and_(
                HorarioTrabalho.id_medico_fk == medico_id,
                HorarioTrabalho.dia_semana == dia_semana,
                HorarioTrabalho.hora_inicio <= hora,
                HorarioTrabalho.hora_fim > hora
            )
        ).first()
        
        if not horario_trabalho:
            dias = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
            return False, f"Médico não atende neste horário. Verifique os horários disponíveis para {dias[dia_semana]}."
        
        return True, "Horário dentro do expediente do médico"


class RegraPaciente:
    """
    Regras de Negócio para Pacientes
    """
    
    @staticmethod
    def contar_faltas_consecutivas(db: Session, paciente_id: int) -> int:
        """
        Conta quantas faltas consecutivas o paciente teve (status='faltou')
        
        Args:
            db: Sessão do banco de dados
            paciente_id: ID do paciente
            
        Returns:
            int: Número de faltas consecutivas
        """
        # Buscar consultas passadas ordenadas por data decrescente
        consultas = db.query(Consulta).filter(
            and_(
                Consulta.id_paciente_fk == paciente_id,
                Consulta.data_hora_inicio < datetime.now()
            )
        ).order_by(Consulta.data_hora_inicio.desc()).all()
        
        faltas_consecutivas = 0
        for consulta in consultas:
            if consulta.status == 'faltou':
                faltas_consecutivas += 1
            else:
                # Se encontrou uma consulta que não foi falta, para a contagem
                break
        
        return faltas_consecutivas
    
    @staticmethod
    def verificar_bloqueio_por_faltas(db: Session, paciente_id: int) -> tuple[bool, str]:
        """
        RN3: Se o paciente faltar a 3 consultas seguidas sem aviso,
        o sistema deve bloquear novos agendamentos até liberação pela administração
        
        Args:
            db: Sessão do banco de dados
            paciente_id: ID do paciente
            
        Returns:
            tuple: (esta_bloqueado: bool, mensagem: str)
        """
        paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
        
        if not paciente:
            return True, "Paciente não encontrado"
        
        if paciente.esta_bloqueado:
            faltas = RegraPaciente.contar_faltas_consecutivas(db, paciente_id)
            return True, f"Paciente bloqueado por {faltas} faltas consecutivas. Entre em contato com a administração."
        
        # Verificar se deve ser bloqueado
        faltas_consecutivas = RegraPaciente.contar_faltas_consecutivas(db, paciente_id)
        
        if faltas_consecutivas >= 3:
            # Bloquear paciente automaticamente
            paciente.esta_bloqueado = True
            db.commit()
            return True, f"Paciente bloqueado automaticamente por {faltas_consecutivas} faltas consecutivas. Entre em contato com a administração."
        
        return False, "Paciente não está bloqueado"
    
    @staticmethod
    def desbloquear_paciente(db: Session, paciente_id: int) -> tuple[bool, str]:
        """
        Permite que o administrador desbloqueie um paciente
        
        Args:
            db: Sessão do banco de dados
            paciente_id: ID do paciente
            
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        paciente = db.query(Paciente).filter(Paciente.id_paciente == paciente_id).first()
        
        if not paciente:
            return False, "Paciente não encontrado"
        
        if not paciente.esta_bloqueado:
            return False, "Paciente não está bloqueado"
        
        paciente.esta_bloqueado = False
        db.commit()
        
        return True, "Paciente desbloqueado com sucesso"


class RegraHorarioDisponivel:
    """
    Regras para validação de horários disponíveis
    """
    
    @staticmethod
    def listar_horarios_disponiveis(
        db: Session,
        medico_id: int,
        data: date,
        duracao_consulta_minutos: int = 30
    ) -> List[str]:
        """
        Lista os horários disponíveis de um médico para uma data específica
        considerando seu horário de trabalho e consultas já agendadas
        
        Args:
            db: Sessão do banco de dados
            medico_id: ID do médico
            data: Data para verificar disponibilidade
            duracao_consulta_minutos: Duração padrão da consulta em minutos
            
        Returns:
            List[str]: Lista de horários disponíveis no formato "HH:MM"
        """
        dia_semana = data.weekday()
        
        # Buscar horários de trabalho do médico neste dia da semana
        horarios_trabalho = db.query(HorarioTrabalho).filter(
            and_(
                HorarioTrabalho.id_medico_fk == medico_id,
                HorarioTrabalho.dia_semana == dia_semana
            )
        ).all()
        
        if not horarios_trabalho:
            return []
        
        # Buscar consultas já agendadas nesta data
        consultas_agendadas = db.query(Consulta).filter(
            and_(
                Consulta.id_medico_fk == medico_id,
                func.date(Consulta.data_hora_inicio) == data,
                Consulta.status.in_(['agendada', 'confirmada'])
            )
        ).all()
        
        horarios_disponiveis = []
        
        for horario_trabalho in horarios_trabalho:
            hora_atual = horario_trabalho.hora_inicio
            hora_fim = horario_trabalho.hora_fim
            
            while hora_atual < hora_fim:
                # Criar datetime para verificar conflito
                data_hora = datetime.combine(data, hora_atual)
                data_hora_fim = data_hora + timedelta(minutes=duracao_consulta_minutos)
                
                # Verificar se este horário tem conflito com alguma consulta
                tem_conflito = False
                for consulta in consultas_agendadas:
                    if (data_hora < consulta.data_hora_fim and 
                        data_hora_fim > consulta.data_hora_inicio):
                        tem_conflito = True
                        break
                
                if not tem_conflito:
                    horarios_disponiveis.append(hora_atual.strftime("%H:%M"))
                
                # Avançar para o próximo slot
                hora_atual = (datetime.combine(date.today(), hora_atual) + 
                             timedelta(minutes=duracao_consulta_minutos)).time()
        
        return sorted(horarios_disponiveis)


class ValidadorAgendamento:
    """
    Valida todas as regras antes de criar um agendamento
    """
    
    @staticmethod
    def validar_novo_agendamento(
        db: Session,
        paciente_id: int,
        medico_id: int,
        data_hora_inicio: datetime,
        data_hora_fim: datetime
    ) -> tuple[bool, str]:
        """
        Valida todas as regras de negócio antes de criar um novo agendamento
        
        Returns:
            tuple: (pode_agendar: bool, mensagem: str)
        """
        # Validar se paciente está bloqueado
        bloqueado, msg_bloqueio = RegraPaciente.verificar_bloqueio_por_faltas(db, paciente_id)
        if bloqueado:
            return False, msg_bloqueio
        
        # Validar limite de consultas futuras
        pode_agendar, msg_limite = RegraConsulta.validar_limite_consultas_futuras(db, paciente_id)
        if not pode_agendar:
            return False, msg_limite
        
        # Validar se está no horário de trabalho do médico
        no_horario, msg_horario = RegraConsulta.validar_horario_trabalho_medico(
            db, medico_id, data_hora_inicio
        )
        if not no_horario:
            return False, msg_horario
        
        # Validar conflito de horário
        sem_conflito, msg_conflito = RegraConsulta.validar_conflito_horario_medico(
            db, medico_id, data_hora_inicio, data_hora_fim
        )
        if not sem_conflito:
            return False, msg_conflito
        
        return True, "Agendamento válido"
