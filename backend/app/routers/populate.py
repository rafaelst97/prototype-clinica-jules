"""
Router para popular dados de teste no banco
Útil para ambientes de produção sem acesso direto ao banco
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from datetime import datetime, time, date
import bcrypt

from app.database import get_db
from app.models.models import (
    Administrador, Paciente, Medico, PlanoSaude, Especialidade,
    HorarioTrabalho, Consulta
)

router = APIRouter()

# 🔐 TOKEN SECRETO - Mude este valor para algo único!
# Gere um novo com: python -c "import secrets; print(secrets.token_urlsafe(32))"
SECRET_TOKEN = "meu-token-super-secreto-2025"


@router.post("/popular-dados")
def popular_dados_teste(db: Session = Depends(get_db)):
    """
    Popula o banco de dados com dados de teste
    
    ⚠️ ATENÇÃO: Use apenas em ambientes de desenvolvimento/teste!
    """
    
    try:
        # Verificar se já existem dados
        if db.query(Administrador).count() > 0:
            return {
                "message": "Banco de dados já contém dados",
                "warning": "Use DELETE /limpar-dados primeiro se quiser repopular"
            }
        
        # 1. Criar Planos de Saúde
        planos_data = [
            {"nome": "Unimed", "cobertura_info": "Cobertura nacional com rede ampla"},
            {"nome": "Amil", "cobertura_info": "Cobertura nacional premium"},
            {"nome": "Bradesco Saúde", "cobertura_info": "Cobertura regional"}
        ]
        
        planos = []
        for plano_data in planos_data:
            plano = PlanoSaude(**plano_data)
            db.add(plano)
            planos.append(plano)
        
        db.flush()
        
        # 2. Criar Especialidades
        especialidades_data = [
            {"nome": "Cardiologia"},
            {"nome": "Dermatologia"},
            {"nome": "Pediatria"},
            {"nome": "Ortopedia"},
            {"nome": "Ginecologia"}
        ]
        
        especialidades = []
        for esp_data in especialidades_data:
            esp = Especialidade(**esp_data)
            db.add(esp)
            especialidades.append(esp)
        
        db.flush()
        
        # 3. Criar Administrador
        senha_hash_admin = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        admin = Administrador(
            nome="Administrador do Sistema",
            email="admin@clinica.com",
            senha_hash=senha_hash_admin.decode('utf-8'),
            papel="Super Admin"
        )
        db.add(admin)
        db.flush()
        
        # 4. Criar Médicos
        medicos_data = [
            {
                "nome": "Dr. João Silva",
                "cpf": "123.456.789-00",
                "crm": "12345-SP",
                "email": "joao.silva@clinica.com",
                "telefone": "(11) 98765-4321",
                "id_especialidade_fk": especialidades[0].id_especialidade  # Cardiologia
            },
            {
                "nome": "Dra. Maria Santos",
                "cpf": "987.654.321-00",
                "crm": "67890-SP",
                "email": "maria.santos@clinica.com",
                "telefone": "(11) 98765-4322",
                "id_especialidade_fk": especialidades[1].id_especialidade  # Dermatologia
            },
            {
                "nome": "Dr. Pedro Costa",
                "cpf": "111.222.333-44",
                "crm": "11111-SP",
                "email": "pedro.costa@clinica.com",
                "telefone": "(11) 98765-4323",
                "id_especialidade_fk": especialidades[2].id_especialidade  # Pediatria
            }
        ]
        
        senha_hash_medico = bcrypt.hashpw("medico123".encode('utf-8'), bcrypt.gensalt())
        
        medicos = []
        for med_data in medicos_data:
            medico = Medico(
                nome=med_data["nome"],
                cpf=med_data["cpf"],
                crm=med_data["crm"],
                email=med_data["email"],
                senha_hash=senha_hash_medico.decode('utf-8'),
                telefone=med_data["telefone"],
                id_especialidade_fk=med_data["id_especialidade_fk"]
            )
            db.add(medico)
            medicos.append(medico)
        
        db.flush()
        
        # 5. Criar horários de trabalho para médicos
        for medico in medicos:
            # Segunda a Sexta (0 a 4)
            for dia_semana in range(0, 5):
                # Manhã: 8h-12h
                horario_manha = HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia_semana,
                    hora_inicio=time(8, 0),
                    hora_fim=time(12, 0)
                )
                db.add(horario_manha)
                
                # Tarde: 14h-18h
                horario_tarde = HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia_semana,
                    hora_inicio=time(14, 0),
                    hora_fim=time(18, 0)
                )
                db.add(horario_tarde)
        
        # 6. Criar Pacientes
        pacientes_data = [
            {
                "nome": "Maria Oliveira",
                "cpf": "555.666.777-88",
                "email": "maria.oliveira@email.com",
                "telefone": "(11) 91234-5678",
                "data_nascimento": "1990-05-15"
            },
            {
                "nome": "José Santos",
                "cpf": "999.888.777-66",
                "email": "jose.santos@email.com",
                "telefone": "(11) 91234-5679",
                "data_nascimento": "1985-08-20"
            },
            {
                "nome": "Ana Costa",
                "cpf": "444.555.666-77",
                "email": "ana.costa@email.com",
                "telefone": "(11) 91234-5680",
                "data_nascimento": "1995-03-10"
            },
            {
                "nome": "Carlos Silva",
                "cpf": "222.333.444-55",
                "email": "carlos.silva@email.com",
                "telefone": "(11) 91234-5681",
                "data_nascimento": "1988-12-25"
            },
            {
                "nome": "Paula Lima",
                "cpf": "333.444.555-66",
                "email": "paula.lima@email.com",
                "telefone": "(11) 91234-5682",
                "data_nascimento": "1992-07-30"
            }
        ]
        
        senha_hash_paciente = bcrypt.hashpw("paciente123".encode('utf-8'), bcrypt.gensalt())
        
        for pac_data in pacientes_data:
            paciente = Paciente(
                nome=pac_data["nome"],
                cpf=pac_data["cpf"],
                email=pac_data["email"],
                senha_hash=senha_hash_paciente.decode('utf-8'),
                telefone=pac_data["telefone"],
                data_nascimento=datetime.strptime(pac_data["data_nascimento"], "%Y-%m-%d").date(),
                esta_bloqueado=False,
                id_plano_saude_fk=planos[0].id_plano_saude  # Unimed
            )
            db.add(paciente)
        
        db.commit()
        
        # Contar registros criados
        total_admins = db.query(Administrador).count()
        total_medicos = db.query(Medico).count()
        total_pacientes = db.query(Paciente).count()
        total_planos = db.query(PlanoSaude).count()
        total_especialidades = db.query(Especialidade).count()
        
        return {
            "success": True,
            "message": "✅ Banco de dados populado com sucesso!",
            "dados_criados": {
                "administradores": total_admins,
                "medicos": total_medicos,
                "pacientes": total_pacientes,
                "planos_saude": total_planos,
                "especialidades": total_especialidades
            },
            "credenciais_teste": {
                "admin": {"email": "admin@clinica.com", "senha": "admin123"},
                "medico": {"email": "joao.silva@clinica.com", "senha": "medico123"},
                "paciente": {"email": "maria.oliveira@email.com", "senha": "paciente123"}
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao popular dados: {str(e)}")


@router.delete("/limpar-dados")
def limpar_dados(db: Session = Depends(get_db)):
    """
    CUIDADO: Remove TODOS os dados do banco!
    Use apenas para resetar o ambiente de teste.
    """
    
    try:
        # Deletar em ordem para respeitar foreign keys
        db.query(Consulta).delete()
        db.query(HorarioTrabalho).delete()
        db.query(Paciente).delete()
        db.query(Medico).delete()
        db.query(Administrador).delete()
        db.query(Especialidade).delete()
        db.query(PlanoSaude).delete()
        
        db.commit()
        
        return {
            "success": True,
            "message": "✅ Todos os dados foram removidos"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao limpar dados: {str(e)}")


# 🔐 ENDPOINT SECRETO - Acesso via navegador
@router.get("/popula-banco/{token}", response_class=HTMLResponse)
def popular_banco_secreto(token: str, db: Session = Depends(get_db)):
    """
    Endpoint secreto para popular o banco via navegador
    
    Acesse: https://clinica-saude-backend.onrender.com/admin/popula-banco/SEU-TOKEN
    """
    
    # Verificar token
    if token != SECRET_TOKEN:
        return HTMLResponse(
            content="""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>🔒 Acesso Negado</title>
                <style>
                    body { 
                        font-family: Arial, sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        text-align: center;
                        max-width: 500px;
                    }
                    h1 { color: #e74c3c; margin-bottom: 20px; }
                    p { color: #555; line-height: 1.6; }
                    .icon { font-size: 64px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">🔒</div>
                    <h1>Acesso Negado</h1>
                    <p>Token inválido! Este endpoint é protegido.</p>
                    <p style="font-size: 12px; color: #999; margin-top: 20px;">
                        Se você é o administrador, verifique o token configurado.
                    </p>
                </div>
            </body>
            </html>
            """,
            status_code=403
        )
    
    # Popular banco de dados
    try:
        # Verificar se já existem dados
        total_admins = db.query(Administrador).count()
        
        if total_admins > 0:
            return HTMLResponse(
                content=f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>⚠️ Banco já Populado</title>
                    <style>
                        body {{ 
                            font-family: Arial, sans-serif; 
                            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                            display: flex;
                            justify-content: center;
                            align-items: center;
                            min-height: 100vh;
                            margin: 0;
                            padding: 20px;
                        }}
                        .container {{
                            background: white;
                            padding: 40px;
                            border-radius: 10px;
                            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                            max-width: 600px;
                        }}
                        h1 {{ color: #f39c12; margin-bottom: 20px; }}
                        p {{ color: #555; line-height: 1.6; }}
                        .icon {{ font-size: 64px; text-align: center; margin-bottom: 20px; }}
                        .info {{ 
                            background: #fff3cd; 
                            padding: 15px; 
                            border-radius: 5px; 
                            margin: 20px 0;
                            border-left: 4px solid #f39c12;
                        }}
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="icon">⚠️</div>
                        <h1>Banco de Dados Já Contém Dados</h1>
                        <div class="info">
                            <strong>Total de administradores encontrados:</strong> {total_admins}
                        </div>
                        <p>O banco de dados já foi populado anteriormente.</p>
                        <p>Se quiser repopular, primeiro limpe os dados usando o endpoint DELETE /admin/limpar-dados</p>
                    </div>
                </body>
                </html>
                """
            )
        
        # Executar população
        # 1. Criar Planos de Saúde
        planos_data = [
            {"nome": "Unimed", "cobertura_info": "Cobertura nacional com rede ampla"},
            {"nome": "Amil", "cobertura_info": "Cobertura nacional premium"},
            {"nome": "Bradesco Saúde", "cobertura_info": "Cobertura regional"}
        ]
        
        planos = []
        for plano_data in planos_data:
            plano = PlanoSaude(**plano_data)
            db.add(plano)
            planos.append(plano)
        
        db.flush()
        
        # 2. Criar Especialidades
        especialidades_data = [
            {"nome": "Cardiologia"},
            {"nome": "Dermatologia"},
            {"nome": "Pediatria"},
            {"nome": "Ortopedia"},
            {"nome": "Ginecologia"}
        ]
        
        especialidades = []
        for esp_data in especialidades_data:
            esp = Especialidade(**esp_data)
            db.add(esp)
            especialidades.append(esp)
        
        db.flush()
        
        # 3. Criar Administrador
        senha_hash_admin = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
        admin = Administrador(
            nome="Administrador do Sistema",
            email="admin@clinica.com",
            senha_hash=senha_hash_admin.decode('utf-8'),
            papel="Super Admin"
        )
        db.add(admin)
        db.flush()
        
        # 4. Criar Médicos
        medicos_data = [
            {
                "nome": "Dr. João Silva",
                "cpf": "123.456.789-00",
                "crm": "12345-SP",
                "email": "joao.silva@clinica.com",
                "telefone": "(11) 98765-4321",
                "id_especialidade_fk": especialidades[0].id_especialidade
            },
            {
                "nome": "Dra. Maria Santos",
                "cpf": "987.654.321-00",
                "crm": "67890-SP",
                "email": "maria.santos@clinica.com",
                "telefone": "(11) 98765-4322",
                "id_especialidade_fk": especialidades[1].id_especialidade
            },
            {
                "nome": "Dr. Pedro Costa",
                "cpf": "111.222.333-44",
                "crm": "11111-SP",
                "email": "pedro.costa@clinica.com",
                "telefone": "(11) 98765-4323",
                "id_especialidade_fk": especialidades[2].id_especialidade
            }
        ]
        
        senha_hash_medico = bcrypt.hashpw("medico123".encode('utf-8'), bcrypt.gensalt())
        
        medicos = []
        for med_data in medicos_data:
            medico = Medico(
                nome=med_data["nome"],
                cpf=med_data["cpf"],
                crm=med_data["crm"],
                email=med_data["email"],
                senha_hash=senha_hash_medico.decode('utf-8'),
                telefone=med_data["telefone"],
                id_especialidade_fk=med_data["id_especialidade_fk"]
            )
            db.add(medico)
            medicos.append(medico)
        
        db.flush()
        
        # 5. Criar horários de trabalho
        for medico in medicos:
            for dia_semana in range(0, 5):  # Segunda a Sexta
                horario_manha = HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia_semana,
                    hora_inicio=time(8, 0),
                    hora_fim=time(12, 0)
                )
                db.add(horario_manha)
                
                horario_tarde = HorarioTrabalho(
                    id_medico_fk=medico.id_medico,
                    dia_semana=dia_semana,
                    hora_inicio=time(14, 0),
                    hora_fim=time(18, 0)
                )
                db.add(horario_tarde)
        
        # 6. Criar Pacientes
        pacientes_data = [
            {
                "nome": "Maria Oliveira",
                "cpf": "555.666.777-88",
                "email": "maria.oliveira@email.com",
                "telefone": "(11) 91234-5678",
                "data_nascimento": "1990-05-15"
            },
            {
                "nome": "José Santos",
                "cpf": "999.888.777-66",
                "email": "jose.santos@email.com",
                "telefone": "(11) 91234-5679",
                "data_nascimento": "1985-08-20"
            },
            {
                "nome": "Ana Costa",
                "cpf": "444.555.666-77",
                "email": "ana.costa@email.com",
                "telefone": "(11) 91234-5680",
                "data_nascimento": "1995-03-10"
            },
            {
                "nome": "Carlos Silva",
                "cpf": "222.333.444-55",
                "email": "carlos.silva@email.com",
                "telefone": "(11) 91234-5681",
                "data_nascimento": "1988-12-25"
            },
            {
                "nome": "Paula Lima",
                "cpf": "333.444.555-66",
                "email": "paula.lima@email.com",
                "telefone": "(11) 91234-5682",
                "data_nascimento": "1992-07-30"
            }
        ]
        
        senha_hash_paciente = bcrypt.hashpw("paciente123".encode('utf-8'), bcrypt.gensalt())
        
        for pac_data in pacientes_data:
            paciente = Paciente(
                nome=pac_data["nome"],
                cpf=pac_data["cpf"],
                email=pac_data["email"],
                senha_hash=senha_hash_paciente.decode('utf-8'),
                telefone=pac_data["telefone"],
                data_nascimento=datetime.strptime(pac_data["data_nascimento"], "%Y-%m-%d").date(),
                esta_bloqueado=False,
                id_plano_saude_fk=planos[0].id_plano_saude
            )
            db.add(paciente)
        
        db.commit()
        
        # Contar registros
        total_admins = db.query(Administrador).count()
        total_medicos = db.query(Medico).count()
        total_pacientes = db.query(Paciente).count()
        total_planos = db.query(PlanoSaude).count()
        total_especialidades = db.query(Especialidade).count()
        
        # Retornar HTML de sucesso
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>✅ Banco Populado com Sucesso</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        padding: 20px;
                        margin: 0;
                    }}
                    .container {{
                        max-width: 800px;
                        margin: 40px auto;
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                    }}
                    h1 {{ color: #27ae60; text-align: center; margin-bottom: 30px; }}
                    .icon {{ font-size: 64px; text-align: center; margin-bottom: 20px; }}
                    .stats {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                        gap: 15px;
                        margin: 30px 0;
                    }}
                    .stat {{
                        background: #ecf0f1;
                        padding: 20px;
                        border-radius: 8px;
                        text-align: center;
                    }}
                    .stat-number {{
                        font-size: 32px;
                        font-weight: bold;
                        color: #3498db;
                    }}
                    .stat-label {{
                        color: #7f8c8d;
                        font-size: 14px;
                        margin-top: 5px;
                    }}
                    .credentials {{
                        background: #e8f5e9;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 4px solid #27ae60;
                    }}
                    .cred-item {{
                        margin: 10px 0;
                        padding: 10px;
                        background: white;
                        border-radius: 5px;
                    }}
                    .cred-title {{
                        font-weight: bold;
                        color: #27ae60;
                        margin-bottom: 5px;
                    }}
                    .cred-info {{
                        color: #555;
                        font-family: 'Courier New', monospace;
                        font-size: 14px;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 2px solid #ecf0f1;
                        color: #7f8c8d;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>Banco de Dados Populado com Sucesso!</h1>
                    
                    <div class="stats">
                        <div class="stat">
                            <div class="stat-number">{total_admins}</div>
                            <div class="stat-label">Administradores</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{total_medicos}</div>
                            <div class="stat-label">Médicos</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{total_pacientes}</div>
                            <div class="stat-label">Pacientes</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{total_planos}</div>
                            <div class="stat-label">Planos de Saúde</div>
                        </div>
                        <div class="stat">
                            <div class="stat-number">{total_especialidades}</div>
                            <div class="stat-label">Especialidades</div>
                        </div>
                    </div>
                    
                    <div class="credentials">
                        <h2 style="margin-top: 0; color: #27ae60;">🔑 Credenciais de Teste</h2>
                        
                        <div class="cred-item">
                            <div class="cred-title">👨‍💼 ADMINISTRADOR</div>
                            <div class="cred-info">Email: admin@clinica.com</div>
                            <div class="cred-info">Senha: admin123</div>
                        </div>
                        
                        <div class="cred-item">
                            <div class="cred-title">👨‍⚕️ MÉDICO</div>
                            <div class="cred-info">Email: joao.silva@clinica.com</div>
                            <div class="cred-info">Senha: medico123</div>
                        </div>
                        
                        <div class="cred-item">
                            <div class="cred-title">🏥 PACIENTE</div>
                            <div class="cred-info">Email: maria.oliveira@email.com</div>
                            <div class="cred-info">Senha: paciente123</div>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>🏥 <strong>Clínica Saúde+</strong> - Sistema v2.0.0</p>
                        <p style="font-size: 12px;">Banco populado em {datetime.now().strftime("%d/%m/%Y às %H:%M:%S")}</p>
                    </div>
                </div>
            </body>
            </html>
            """
        )
        
    except Exception as e:
        db.rollback()
        return HTMLResponse(
            content=f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>❌ Erro ao Popular Banco</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        background: linear-gradient(135deg, #ee0979 0%, #ff6a00 100%);
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        min-height: 100vh;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        background: white;
                        padding: 40px;
                        border-radius: 10px;
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                        max-width: 600px;
                    }}
                    h1 {{ color: #e74c3c; margin-bottom: 20px; }}
                    .icon {{ font-size: 64px; text-align: center; margin-bottom: 20px; }}
                    .error {{ 
                        background: #fee; 
                        padding: 15px; 
                        border-radius: 5px; 
                        border-left: 4px solid #e74c3c;
                        color: #c0392b;
                        font-family: monospace;
                        margin: 20px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">❌</div>
                    <h1>Erro ao Popular Banco de Dados</h1>
                    <div class="error">
                        {str(e)}
                    </div>
                    <p style="color: #555;">Entre em contato com o administrador do sistema.</p>
                </div>
            </body>
            </html>
            """,
            status_code=500
        )
