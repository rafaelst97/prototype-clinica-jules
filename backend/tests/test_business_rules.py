"""
Testes de Regras de Negócio, alinhados com a documentação do projeto.
"""
import pytest
from datetime import datetime, timedelta, time
from fastapi import status
from app.models.models import Consulta, Paciente

@pytest.mark.business_rules
class TestBusinessRules:
    """Conjunto de testes para as regras de negócio do sistema."""

    # RN1: Cancelamento/Reagendamento com 24h de antecedência
    def test_rn1_permite_cancelamento_com_antecedencia(self, client, db_session, consulta_agendada, auth_headers_paciente):
        """Verifica se o cancelamento é permitido com mais de 24h de antecedência."""
        # A consulta_agendada é criada com 48h de antecedência por padrão
        response = client.delete(
            f"/pacientes/consultas/{consulta_agendada.id_consulta}",
            headers=auth_headers_paciente,
            json={"paciente_id": consulta_agendada.id_paciente_fk}
        )
        assert response.status_code == status.HTTP_200_OK
        assert "cancelada com sucesso" in response.json()["mensagem"]

    def test_rn1_bloqueia_cancelamento_sem_antecedencia(self, client, db_session, consulta_proxima, auth_headers_paciente):
        """Verifica se o cancelamento é bloqueado com menos de 24h de antecedência."""
        # a consulta_proxima é criada com 12h de antecedência
        response = client.delete(
            f"/pacientes/consultas/{consulta_proxima.id_consulta}",
            headers=auth_headers_paciente,
            json={"paciente_id": consulta_proxima.id_paciente_fk}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "24 horas de antecedência" in response.json()["detail"]

    def test_rn1_permite_reagendamento_com_antecedencia(self, client, db_session, consulta_agendada, auth_headers_paciente):
        """Verifica se o reagendamento é permitido com mais de 24h de antecedência."""
        nova_data_hora = (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%dT10:00:00")
        response = client.put(
            f"/pacientes/consultas/{consulta_agendada.id_consulta}/reagendar",
            headers=auth_headers_paciente,
            json={"nova_data_hora_inicio": nova_data_hora, "paciente_id": consulta_agendada.id_paciente_fk}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json()["data_hora_inicio"] == nova_data_hora

    def test_rn1_bloqueia_reagendamento_sem_antecedencia(self, client, db_session, consulta_proxima, auth_headers_paciente):
        """Verifica se o reagendamento é bloqueado com menos de 24h de antecedência."""
        nova_data_hora = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%dT10:00:00")
        response = client.put(
            f"/pacientes/consultas/{consulta_proxima.id_consulta}/reagendar",
            headers=auth_headers_paciente,
            json={"nova_data_hora_inicio": nova_data_hora, "paciente_id": consulta_proxima.id_paciente_fk}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "24 horas de antecedência" in response.json()["detail"]

    # RN2: Máximo de 2 consultas futuras por paciente
    def test_rn2_permite_agendar_ate_duas_consultas(self, client, db_session, paciente_teste, medico_cardiologista, auth_headers_paciente):
        """Verifica se o paciente pode agendar até duas consultas futuras."""
        # Agendamento da primeira consulta
        data_1 = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%dT10:00:00")
        response_1 = client.post(
            f"/pacientes/consultas?paciente_id={paciente_teste.id_paciente}",
            headers=auth_headers_paciente,
            json={"id_medico": medico_cardiologista.id_medico, "data_hora_inicio": data_1}
        )
        assert response_1.status_code == status.HTTP_201_CREATED

        # Agendamento da segunda consulta
        data_2 = (datetime.now() + timedelta(days=12)).strftime("%Y-%m-%dT11:00:00")
        response_2 = client.post(
            f"/pacientes/consultas?paciente_id={paciente_teste.id_paciente}",
            headers=auth_headers_paciente,
            json={"id_medico": medico_cardiologista.id_medico, "data_hora_inicio": data_2}
        )
        assert response_2.status_code == status.HTTP_201_CREATED

    def test_rn2_bloqueia_terceira_consulta_futura(self, client, db_session, paciente_com_duas_consultas, medico_cardiologista, auth_headers_paciente):
        """Verifica se o sistema bloqueia o agendamento da terceira consulta futura."""
        paciente_id = paciente_com_duas_consultas
        
        # Tentar agendar a terceira consulta
        data_3 = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%dT10:00:00")
        response = client.post(
            f"/pacientes/consultas?paciente_id={paciente_id}",
            headers=auth_headers_paciente,
            json={"id_medico": medico_cardiologista.id_medico, "data_hora_inicio": data_3}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "limite de 2 consultas futuras" in response.json()["detail"]

    # RN3: Bloqueio de paciente por 3 faltas
    def test_rn3_paciente_bloqueado_nao_agenda(self, client, db_session, paciente_bloqueado, medico_cardiologista, auth_headers_paciente_bloqueado):
        """Verifica se um paciente bloqueado por faltas não consegue agendar."""
        data = (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%dT10:00:00")
        response = client.post(
            f"/pacientes/consultas?paciente_id={paciente_bloqueado.id_paciente}",
            headers=auth_headers_paciente_bloqueado,
            json={"id_medico": medico_cardiologista.id_medico, "data_hora_inicio": data}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "paciente está bloqueado" in response.json()["detail"]

    # RN4: Evitar conflitos de agendamento para médicos
    def test_rn4_nao_permite_agendamento_em_horario_ocupado(self, client, db_session, consulta_agendada, auth_headers_paciente):
        """Verifica se o sistema previne agendamentos conflitantes para o mesmo médico."""
        # Tenta agendar no mesmo horário da `consulta_agendada`
        response = client.post(
            f"/pacientes/consultas?paciente_id={consulta_agendada.id_paciente_fk}",
            headers=auth_headers_paciente,
            json={
                "id_medico": consulta_agendada.id_medico_fk,
                "data_hora_inicio": consulta_agendada.data_hora_inicio.isoformat()
            }
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "conflito de horário" in response.json()["detail"]
        
    # Extra: Validar agendamento fora do horário de trabalho do médico
    def test_agendamento_fora_horario_trabalho_medico(self, client, paciente_teste, medico_sem_horario, auth_headers_paciente):
        """Verifica se o sistema bloqueia agendamento fora do horário de trabalho do médico."""
        data = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%dT15:00:00")
        response = client.post(
            f"/pacientes/consultas?paciente_id={paciente_teste.id_paciente}",
            headers=auth_headers_paciente,
            json={"id_medico": medico_sem_horario.id_medico, "data_hora_inicio": data}
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "fora do horário de trabalho" in response.json()["detail"]
