from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Banco de Dados
DATABASE_URL = "sqlite:///./usuarios.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

# Modelo do Banco
class UsuarioDB(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, unique=True, index=True)

Base.metadata.create_all(bind=engine)

# Pydantic (validação de dados)
class Usuario(BaseModel):
    nome: str
    email: str

class UsuarioOut(Usuario):
    id: int

    class Config:
        orm_mode = True

# Instancia API
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ou defina ["http://localhost:5500"] se quiser mais seguro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
@app.post("/usuarios/", response_model=UsuarioOut)
def criar_usuario(usuario: Usuario):
    db = SessionLocal()
    db_usuario = UsuarioDB(nome=usuario.nome, email=usuario.email)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    db.close()
    return db_usuario

@app.get("/usuarios/", response_model=List[UsuarioOut])
def listar_usuarios():
    db = SessionLocal()
    usuarios = db.query(UsuarioDB).all()
    db.close()
    return usuarios

@app.get("/usuarios/{usuario_id}", response_model=UsuarioOut)
def obter_usuario(usuario_id: int):
    db = SessionLocal()
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    db.close()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario

@app.put("/usuarios/{usuario_id}", response_model=UsuarioOut)
def atualizar_usuario(usuario_id: int, usuario: Usuario):
    db = SessionLocal()
    db_usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if db_usuario is None:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db_usuario.nome = usuario.nome
    db_usuario.email = usuario.email
    db.commit()
    db.refresh(db_usuario)
    db.close()
    return db_usuario

@app.delete("/usuarios/{usuario_id}")
def deletar_usuario(usuario_id: int):
    db = SessionLocal()
    usuario = db.query(UsuarioDB).filter(UsuarioDB.id == usuario_id).first()
    if usuario is None:
        db.close()
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    db.delete(usuario)
    db.commit()
    db.close()
    return {"mensagem": "Usuário deletado com sucesso"}
