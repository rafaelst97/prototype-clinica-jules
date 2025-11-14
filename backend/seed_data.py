"""
Script para popular o banco de dados com dados iniciais
Execute: docker exec -it clinica_backend python seed_data.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models import (
    Usuario, Admin, Especialidade, Convenio, Medico, Paciente, HorarioDisponivel, TipoUsuario
)
from app.utils.auth import get_password_hash
from datetime import time, date

def seed_database():
    db = SessionLocal()
    
    try:
        print("🌱 Iniciando seed do banco de dados...")
        
        # 1. Criar Especialidades
        print("\n📋 Criando Especialidades...")
        especialidades_data = [
            {"nome": "Cardiologia", "descricao": "Especialidade médica que se dedica ao diagnóstico e tratamento das doenças do coração"},
            {"nome": "Dermatologia", "descricao": "Especialidade médica dedicada ao estudo e tratamento da pele"},
            {"nome": "Ortopedia", "descricao": "Especialidade médica que cuida do sistema locomotor"},
            {"nome": "Pediatria", "descricao": "Especialidade médica dedicada à assistência à criança e ao adolescente"},
            {"nome": "Ginecologia", "descricao": "Especialidade médica que trata do sistema reprodutor feminino"},
            {"nome": "Oftalmologia", "descricao": "Especialidade médica que estuda e trata as doenças dos olhos"},
            {"nome": "Psiquiatria", "descricao": "Especialidade médica que lida com a prevenção, diagnóstico e tratamento de transtornos mentais"},
            {"nome": "Neurologia", "descricao": "Especialidade médica que trata do sistema nervoso"},
        ]
        
        for esp_data in especialidades_data:
            existe = db.query(Especialidade).filter(Especialidade.nome == esp_data["nome"]).first()
            if not existe:
                especialidade = Especialidade(**esp_data)
                db.add(especialidade)
                print(f"  ✓ {esp_data['nome']}")
        
        db.commit()
        
        # 2. Criar Convênios
        print("\n🏥 Criando Convênios...")
        convenios_data = [
            {"nome": "Unimed", "codigo": "UNI001", "telefone": "(47) 3333-4444", "email": "contato@unimed.com.br", "descricao": "Convênio Unimed"},
            {"nome": "Bradesco Saúde", "codigo": "BRA001", "telefone": "(47) 3333-5555", "email": "contato@bradescosaude.com.br", "descricao": "Convênio Bradesco Saúde"},
            {"nome": "SulAmérica", "codigo": "SUL001", "telefone": "(47) 3333-6666", "email": "contato@sulamerica.com.br", "descricao": "Convênio SulAmérica"},
            {"nome": "Particular", "codigo": "PAR001", "telefone": None, "email": None, "descricao": "Atendimento particular"},
        ]
        
        for conv_data in convenios_data:
            existe = db.query(Convenio).filter(Convenio.nome == conv_data["nome"]).first()
            if not existe:
                convenio = Convenio(**conv_data)
                db.add(convenio)
                print(f"  ✓ {conv_data['nome']}")
        
        db.commit()
        
        # 3. Criar usuário Admin
        print("\n👤 Criando Administrador...")
        admin_email = "admin@clinica.com"
        admin_existe = db.query(Usuario).filter(Usuario.email == admin_email).first()
        
        if not admin_existe:
            usuario_admin = Usuario(
                email=admin_email,
                senha_hash=get_password_hash("admin123"),
                nome="Administrador Sistema",
                tipo=TipoUsuario.ADMIN
            )
            db.add(usuario_admin)
            db.flush()
            
            admin = Admin(
                usuario_id=usuario_admin.id,
                cargo="Administrador Geral"
            )
            db.add(admin)
            db.commit()
            print(f"  ✓ Admin criado: {admin_email} / admin123")
        else:
            print(f"  ℹ Admin já existe: {admin_email}")
        
        # 4. Criar médicos de exemplo
        print("\n👨‍⚕️ Criando Médicos de exemplo...")
        
        # Buscar especialidades
        cardiologia = db.query(Especialidade).filter(Especialidade.nome == "Cardiologia").first()
        dermatologia = db.query(Especialidade).filter(Especialidade.nome == "Dermatologia").first()
        pediatria = db.query(Especialidade).filter(Especialidade.nome == "Pediatria").first()
        
        medicos_data = [
            {
                "email": "dr.silva@clinica.com",
                "senha": "medico123",
                "nome": "Dr. João Silva",
                "crm": "12345-SC",
                "especialidade_id": cardiologia.id if cardiologia else 1,
                "telefone": "(47) 99999-1111",
                "valor_consulta": 250.00
            },
            {
                "email": "dra.santos@clinica.com",
                "senha": "medico123",
                "nome": "Dra. Maria Santos",
                "crm": "23456-SC",
                "especialidade_id": dermatologia.id if dermatologia else 2,
                "telefone": "(47) 99999-2222",
                "valor_consulta": 200.00
            },
            {
                "email": "dr.oliveira@clinica.com",
                "senha": "medico123",
                "nome": "Dr. Pedro Oliveira",
                "crm": "34567-SC",
                "especialidade_id": pediatria.id if pediatria else 4,
                "telefone": "(47) 99999-3333",
                "valor_consulta": 180.00
            }
        ]
        
        for med_data in medicos_data:
            existe = db.query(Usuario).filter(Usuario.email == med_data["email"]).first()
            if not existe:
                usuario_medico = Usuario(
                    email=med_data["email"],
                    senha_hash=get_password_hash(med_data["senha"]),
                    nome=med_data["nome"],
                    tipo=TipoUsuario.MEDICO
                )
                db.add(usuario_medico)
                db.flush()
                
                medico = Medico(
                    usuario_id=usuario_medico.id,
                    crm=med_data["crm"],
                    especialidade_id=med_data["especialidade_id"],
                    telefone=med_data["telefone"],
                    valor_consulta=med_data["valor_consulta"],
                    tempo_consulta=30
                )
                db.add(medico)
                print(f"  ✓ {med_data['nome']} - {med_data['email']} / {med_data['senha']}")
        
        db.commit()
        
        # 5. Criar horários de trabalho para os médicos
        print("\n⏰ Criando Horários de Trabalho...")
        medicos = db.query(Medico).all()
        
        for medico in medicos:
            # Verificar se já tem horários
            horarios_existentes = db.query(HorarioDisponivel).filter(HorarioDisponivel.medico_id == medico.id).count()
            
            if horarios_existentes == 0:
                # Segunda a Sexta: 8h às 12h e 14h às 18h
                for dia in range(0, 5):  # 0=Segunda, 4=Sexta
                    # Manhã
                    horario_manha = HorarioDisponivel(
                        medico_id=medico.id,
                        dia_semana=dia,
                        hora_inicio=time(8, 0),
                        hora_fim=time(12, 0),
                        ativo=True
                    )
                    db.add(horario_manha)
                    
                    # Tarde
                    horario_tarde = HorarioDisponivel(
                        medico_id=medico.id,
                        dia_semana=dia,
                        hora_inicio=time(14, 0),
                        hora_fim=time(18, 0),
                        ativo=True
                    )
                    db.add(horario_tarde)
                
                print(f"  ✓ Horários criados para {medico.usuario.nome}")
        
        db.commit()
        
        # 6. Criar pacientes de teste
        print("\n👥 Criando Pacientes de teste...")
        
        unimed = db.query(Convenio).filter(Convenio.nome == "Unimed").first()
        particular = db.query(Convenio).filter(Convenio.nome == "Particular").first()
        
        pacientes_data = [
            {
                "email": "paciente1@teste.com",
                "senha": "paciente123",
                "nome": "Carlos Mendes",
                "cpf": "111.222.333-44",
                "data_nascimento": date(1990, 5, 15),
                "telefone": "(47) 98888-1111",
                "endereco": "Rua das Flores, 123",
                "cidade": "Itajaí",
                "estado": "SC",
                "cep": "88301-000",
                "convenio_id": unimed.id if unimed else None,
                "numero_carteirinha": "UNI123456"
            },
            {
                "email": "paciente2@teste.com",
                "senha": "paciente123",
                "nome": "Ana Paula Silva",
                "cpf": "222.333.444-55",
                "data_nascimento": date(1985, 8, 20),
                "telefone": "(47) 98888-2222",
                "endereco": "Av. Central, 456",
                "cidade": "Balneário Camboriú",
                "estado": "SC",
                "cep": "88330-000",
                "convenio_id": particular.id if particular else None,
                "numero_carteirinha": None
            },
            {
                "email": "paciente3@teste.com",
                "senha": "paciente123",
                "nome": "Roberto Costa",
                "cpf": "333.444.555-66",
                "data_nascimento": date(1978, 3, 10),
                "telefone": "(47) 98888-3333",
                "endereco": "Rua São Paulo, 789",
                "cidade": "Itajaí",
                "estado": "SC",
                "cep": "88302-000",
                "convenio_id": unimed.id if unimed else None,
                "numero_carteirinha": "UNI789012"
            }
        ]
        
        for pac_data in pacientes_data:
            existe = db.query(Usuario).filter(Usuario.email == pac_data["email"]).first()
            if not existe:
                usuario_paciente = Usuario(
                    email=pac_data["email"],
                    senha_hash=get_password_hash(pac_data["senha"]),
                    nome=pac_data["nome"],
                    tipo=TipoUsuario.PACIENTE
                )
                db.add(usuario_paciente)
                db.flush()
                
                paciente = Paciente(
                    usuario_id=usuario_paciente.id,
                    cpf=pac_data["cpf"],
                    data_nascimento=pac_data["data_nascimento"],
                    telefone=pac_data["telefone"],
                    endereco=pac_data["endereco"],
                    cidade=pac_data["cidade"],
                    estado=pac_data["estado"],
                    cep=pac_data["cep"],
                    convenio_id=pac_data["convenio_id"],
                    numero_carteirinha=pac_data["numero_carteirinha"],
                    faltas_consecutivas=0
                )
                db.add(paciente)
                print(f"  ✓ {pac_data['nome']} - {pac_data['email']} / paciente123")
        
        db.commit()
        
        print("\n✅ Seed concluído com sucesso!")
        print("\n📝 Credenciais de acesso:")
        print("   Admin: admin@clinica.com / admin123")
        print("   Médicos: dr.silva@clinica.com / medico123")
        print("            dra.santos@clinica.com / medico123")
        print("            dr.oliveira@clinica.com / medico123")
        print("   Pacientes: paciente1@teste.com / paciente123")
        print("              paciente2@teste.com / paciente123")
        print("              paciente3@teste.com / paciente123")
        
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
