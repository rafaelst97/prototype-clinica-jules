from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, pacientes, medicos, admin, consultas, populate

# Criar tabelas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clínica Saúde+ API",
    description="Sistema de Agendamento de Consultas Médicas",
    version="1.0.0"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Incluir routers
app.include_router(auth.router)
app.include_router(consultas.router)  # Router de consultas (NOVO)
app.include_router(pacientes.router)
app.include_router(medicos.router)
app.include_router(admin.router)
app.include_router(populate.router, prefix="/admin", tags=["Database"])

@app.get("/")
def root():
    return {
        "message": "Clínica Saúde+ API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "online"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
