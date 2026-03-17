from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import SessionLocal, engine, get_db

# Crea las tablas en la base de datos (Ideal para el MVP con SQLite)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MVP Escrow Construcción")

# ---- Endpoints de Usuarios ----

@app.post("/usuarios/", response_model=schemas.Usuario)
def create_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    return crud.create_usuario(db=db, usuario=usuario)

@app.get("/usuarios/", response_model=List[schemas.Usuario])
def read_usuarios(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_usuarios(db, skip=skip, limit=limit)

@app.get("/usuarios/{usuario_id}", response_model=schemas.Usuario)
def read_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if db_usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return db_usuario

# ---- Endpoints de Contratos ----

@app.post("/contratos/", response_model=schemas.Contrato)
def create_contrato(contrato: schemas.ContratoCreate, db: Session = Depends(get_db)):
    # Validaciones básicas
    cliente = crud.get_usuario(db, usuario_id=contrato.cliente_id)
    if not cliente or cliente.rol != models.RolEnum.CLIENTE:
         raise HTTPException(status_code=400, detail="El cliente especificado no existe o no tiene el rol correcto.")
    
    maestro = crud.get_usuario(db, usuario_id=contrato.maestro_id)
    if not maestro or maestro.rol != models.RolEnum.MAESTRO:
         raise HTTPException(status_code=400, detail="El maestro especificado no existe o no tiene el rol correcto.")

    return crud.create_contrato(db=db, contrato=contrato)

@app.get("/contratos/", response_model=List[schemas.Contrato])
def read_contratos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_contratos(db, skip=skip, limit=limit)

@app.get("/contratos/{contrato_id}", response_model=schemas.Contrato)
def read_contrato(contrato_id: int, db: Session = Depends(get_db)):
    db_contrato = crud.get_contrato(db, contrato_id=contrato_id)
    if db_contrato is None:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return db_contrato
