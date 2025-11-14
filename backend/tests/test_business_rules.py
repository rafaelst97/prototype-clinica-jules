"""
Testes de Regras de Negócio (RN1, RN2, RN3, RN4)
Performance: ~3-4 segundos total
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.mark.business_rules
class TestBusinessRules:
    """Suite de testes de regras de negócio"""
    
    # ========== RN1: Bloqueio por Faltas ==========
    
    def test_rn1_paciente_bloqueado_nao_pode_agendar(
        self, client, db_session, paciente_teste, medico_cardiologista, 
        horarios_trabalho_cardio, auth_headers_paciente
    ):
        """RN1: Paciente bloqueado não pode agendar consultas"""
        # Bloquear paciente
        paciente_teste.esta_bloqueado = True
        db_session.commit()
        
        # Tentar agendar
        data_futura = datetime.now() + timedelta(days=5)
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT10:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "bloqueado" in response.json()["detail"].lower()
    
    def test_rn1_paciente_desbloqueado_pode_agendar(
        self, client, db_session, paciente_teste, medico_cardiologista,
        horarios_trabalho_cardio, auth_headers_paciente
    ):
        """RN1: Paciente desbloqueado pode agendar normalmente"""
        # Garantir que está desbloqueado
        paciente_teste.esta_bloqueado = False
        db_session.commit()
        
        # Agendar consulta
        data_futura = datetime.now() + timedelta(days=5)
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT10:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    # ========== RN2: Horário de Trabalho ==========
    
    def test_rn2_agendamento_fora_horario_trabalho(
        self, client, medico_cardiologista, horarios_trabalho_cardio,
        auth_headers_paciente
    ):
        """RN2: Não permite agendar fora do horário de trabalho"""
        # Tentar agendar às 20h (fora do horário 9h-17h)
        data_futura = datetime.now() + timedelta(days=5)
        data_futura = data_futura.replace(hour=20, minute=0)
        
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT20:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "horário" in response.json()["detail"].lower()
    
    def test_rn2_agendamento_dentro_horario_trabalho(
        self, client, medico_cardiologista, horarios_trabalho_cardio,
        auth_headers_paciente
    ):
        """RN2: Permite agendar dentro do horário de trabalho"""
        # Agendar às 14h (dentro do horário 9h-17h)
        data_futura = datetime.now() + timedelta(days=5)
        data_futura = data_futura.replace(hour=14, minute=0)
        
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT14:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    def test_rn2_agendamento_dia_sem_trabalho(
        self, client, medico_cardiologista, horarios_trabalho_cardio,
        auth_headers_paciente
    ):
        """RN2: Não permite agendar em dia que médico não trabalha"""
        # Encontrar um sábado (médico trabalha Seg-Sex)
        data_futura = datetime.now() + timedelta(days=1)
        while data_futura.weekday() != 5:  # 5 = Sábado
            data_futura += timedelta(days=1)
        
        data_futura = data_futura.replace(hour=10, minute=0)
        
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT10:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    # ========== RN3: Conflito de Horários ==========
    
    def test_rn3_agendamento_horario_ocupado(
        self, client, db_session, medico_cardiologista, paciente_teste,
        horarios_trabalho_cardio, auth_headers_paciente
    ):
        """RN3: Não permite agendar em horário já ocupado"""
        from app.models.models import Consulta
        
        # Criar consulta existente
        data_hora = datetime.now() + timedelta(days=5)
        data_hora = data_hora.replace(hour=10, minute=0, second=0, microsecond=0)
        
        consulta_existente = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=data_hora,
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta_existente)
        db_session.commit()
        
        # Tentar agendar no mesmo horário
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_hora.strftime("%Y-%m-%dT10:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "ocupado" in response.json()["detail"].lower()
    
    def test_rn3_agendamento_horario_livre(
        self, client, medico_cardiologista, horarios_trabalho_cardio,
        auth_headers_paciente
    ):
        """RN3: Permite agendar em horário livre"""
        data_futura = datetime.now() + timedelta(days=7)
        # Garantir que seja uma segunda-feira (dia 0)
        while data_futura.weekday() != 0:
            data_futura += timedelta(days=1)
        data_futura = data_futura.replace(hour=11, minute=0)
        
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT11:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_201_CREATED
    
    # ========== RN4: Antecedência Mínima ==========
    
    def test_rn4_cancelamento_com_antecedencia(
        self, client, db_session, medico_cardiologista, paciente_teste,
        auth_headers_paciente
    ):
        """RN4: Permite cancelar com antecedência >= 24h"""
        from app.models.models import Consulta
        
        # Criar consulta para daqui a 48 horas
        data_hora = datetime.now() + timedelta(hours=48)
        
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=data_hora,
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        db_session.refresh(consulta)
        
        # Cancelar
        response = client.put(
            f"/consultas/{consulta.id_consulta}/cancelar",
            headers=auth_headers_paciente
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["status"] == "Cancelada"
    
    def test_rn4_cancelamento_sem_antecedencia(
        self, client, db_session, medico_cardiologista, paciente_teste,
        auth_headers_paciente
    ):
        """RN4: Não permite cancelar com antecedência < 24h"""
        from app.models.models import Consulta
        
        # Criar consulta para daqui a 12 horas
        data_hora = datetime.now() + timedelta(hours=12)
        
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=data_hora,
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        db_session.refresh(consulta)
        
        # Tentar cancelar
        response = client.put(
            f"/consultas/{consulta.id_consulta}/cancelar",
            headers=auth_headers_paciente
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "24 horas" in response.json()["detail"].lower()
    
    def test_rn4_reagendamento_com_antecedencia(
        self, client, db_session, medico_cardiologista, paciente_teste,
        horarios_trabalho_cardio, auth_headers_paciente
    ):
        """RN4: Permite reagendar com antecedência >= 24h"""
        from app.models.models import Consulta
        
        # Criar consulta para daqui a 72 horas
        data_hora_original = datetime.now() + timedelta(hours=72)
        data_hora_original = data_hora_original.replace(hour=10, minute=0)
        
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=data_hora_original,
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        db_session.refresh(consulta)
        
        # Reagendar para daqui a 96 horas
        nova_data = datetime.now() + timedelta(hours=96)
        nova_data = nova_data.replace(hour=14, minute=0)
        
        response = client.put(
            f"/consultas/{consulta.id_consulta}/reagendar",
            headers=auth_headers_paciente,
            json={"nova_data_hora": nova_data.strftime("%Y-%m-%dT14:00:00")}
        )
        
        assert response.status_code == status.HTTP_200_OK
