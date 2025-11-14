"""
Testes de Endpoints de Consultas
Performance: ~2-3 segundos total
"""
import pytest
from datetime import datetime, timedelta
from fastapi import status


@pytest.mark.integration
class TestConsultasEndpoints:
    """Suite de testes dos endpoints de consultas"""
    
    def test_agendar_consulta_sucesso(
        self, client, medico_cardiologista, horarios_trabalho_cardio,
        auth_headers_paciente
    ):
        """Teste: Agendar consulta com sucesso"""
        data_futura = datetime.now() + timedelta(days=5)
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
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["status"] == "Agendada"
        assert data["id_medico_fk"] == medico_cardiologista.id_medico
    
    def test_listar_minhas_consultas(
        self, client, db_session, paciente_teste, medico_cardiologista,
        auth_headers_paciente
    ):
        """Teste: Listar consultas do paciente logado"""
        from app.models.models import Consulta
        
        # Criar consulta
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=datetime.now() + timedelta(days=3),
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        
        # Listar
        response = client.get("/consultas/minhas", headers=auth_headers_paciente)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 1
    
    def test_buscar_consulta_por_id(
        self, client, db_session, paciente_teste, medico_cardiologista,
        auth_headers_paciente
    ):
        """Teste: Buscar consulta específica"""
        from app.models.models import Consulta
        
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=datetime.now() + timedelta(days=3),
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        db_session.refresh(consulta)
        
        response = client.get(
            f"/consultas/{consulta.id_consulta}",
            headers=auth_headers_paciente
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id_consulta"] == consulta.id_consulta
    
    def test_cancelar_consulta(
        self, client, db_session, paciente_teste, medico_cardiologista,
        auth_headers_paciente
    ):
        """Teste: Cancelar consulta"""
        from app.models.models import Consulta
        
        # Consulta com 48h de antecedência
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=datetime.now() + timedelta(hours=48),
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        db_session.refresh(consulta)
        
        response = client.put(
            f"/consultas/{consulta.id_consulta}/cancelar",
            headers=auth_headers_paciente
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "Cancelada"
    
    def test_reagendar_consulta(
        self, client, db_session, paciente_teste, medico_cardiologista,
        horarios_trabalho_cardio, auth_headers_paciente
    ):
        """Teste: Reagendar consulta"""
        from app.models.models import Consulta
        
        # Consulta original
        data_original = datetime.now() + timedelta(hours=72)
        data_original = data_original.replace(hour=10, minute=0)
        
        consulta = Consulta(
            id_paciente_fk=paciente_teste.id_paciente,
            id_medico_fk=medico_cardiologista.id_medico,
            data_hora=data_original,
            tipo="Consulta",
            status="Agendada"
        )
        db_session.add(consulta)
        db_session.commit()
        db_session.refresh(consulta)
        
        # Nova data
        nova_data = datetime.now() + timedelta(hours=120)
        nova_data = nova_data.replace(hour=14, minute=0)
        
        response = client.put(
            f"/consultas/{consulta.id_consulta}/reagendar",
            headers=auth_headers_paciente,
            json={"nova_data_hora": nova_data.strftime("%Y-%m-%dT14:00:00")}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id_consulta"] == consulta.id_consulta
    
    def test_buscar_horarios_disponiveis(
        self, client, medico_cardiologista, horarios_trabalho_cardio
    ):
        """Teste: Buscar horários disponíveis de um médico"""
        data_consulta = (datetime.now() + timedelta(days=7)).date()
        
        response = client.get(
            f"/consultas/horarios-disponiveis/{medico_cardiologista.id_medico}",
            params={"data": data_consulta.isoformat()}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    def test_agendar_sem_autenticacao(self, client, medico_cardiologista):
        """Teste: Não permite agendar sem autenticação"""
        data_futura = datetime.now() + timedelta(days=5)
        
        response = client.post(
            "/consultas/agendar",
            json={
                "id_medico": medico_cardiologista.id_medico,
                "data_hora": data_futura.strftime("%Y-%m-%dT10:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_agendar_medico_inexistente(self, client, auth_headers_paciente):
        """Teste: Erro ao agendar com médico inexistente"""
        data_futura = datetime.now() + timedelta(days=5)
        
        response = client.post(
            "/consultas/agendar",
            headers=auth_headers_paciente,
            json={
                "id_medico": 99999,  # ID inexistente
                "data_hora": data_futura.strftime("%Y-%m-%dT10:00:00"),
                "tipo": "Consulta"
            }
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
