from fastapi import FastAPI, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os

import crud, models, schemas
from database import SessionLocal, engine, get_db

# Crea las tablas en la base de datos (Ideal para el MVP con SQLite)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="MVP Escrow Construcción")

# Crear directorio estático si no existe (para evitar errores al iniciar)
if not os.path.exists("static"):
    os.makedirs("static")

# Montar carpeta de archivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("static/index.html")

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

@app.get("/usuarios/{usuario_id}/contratos", response_model=List[schemas.Contrato])
def read_contratos_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = crud.get_usuario(db, usuario_id=usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return crud.get_contratos_por_usuario(db, usuario_id=usuario_id)

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

# ---- Endpoints Complementarios (Pruebas) ----
@app.post("/usuarios/{usuario_id}/agregar_saldo", response_model=schemas.Usuario)
def agregar_saldo(usuario_id: int, monto: float, db: Session = Depends(get_db)):
    usuario = crud.get_usuario(db, usuario_id)
    if not usuario:
         raise HTTPException(status_code=404, detail="Usuario no encontrado")
    usuario.saldo_billetera += monto
    db.commit()
    db.refresh(usuario)
    return usuario

# ---- Endpoints de Hitos ----
@app.post("/contratos/{contrato_id}/hitos/", response_model=schemas.HitoObra)
def create_hito_para_contrato(contrato_id: int, hito: schemas.HitoObraCreate, db: Session = Depends(get_db)):
    db_contrato = crud.get_contrato(db, contrato_id=contrato_id)
    if not db_contrato:
        raise HTTPException(status_code=404, detail="Contrato no encontrado")
    return crud.create_hito_obra(db=db, hito=hito, contrato_id=contrato_id)

# ---- Flujo 1: Fondear Contrato (Escrow) ----
@app.post("/contratos/{contrato_id}/fondear", response_model=schemas.Contrato)
def fondear_contrato(contrato_id: int, db: Session = Depends(get_db)):
    contrato, error = crud.fondear_contrato(db, contrato_id=contrato_id)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return contrato

# ---- Flujo 2: Aprobar y Pagar Hito ----

# El maestro sube la evidencia o marca como "Listo para revisión"
@app.post("/hitos/{hito_id}/enviar_revision", response_model=schemas.HitoObra)
def enviar_hito_revision(hito_id: int, db: Session = Depends(get_db)):
    hito, error = crud.enviar_hito_a_revision(db, hito_id=hito_id)
    if error:
         raise HTTPException(status_code=400, detail=error)
    return hito

# El cliente revisa la evidencia y si está de acuerdo, aprueba (Paga)
@app.post("/hitos/{hito_id}/aprobar", response_model=schemas.HitoObra)
def aprobar_hito(hito_id: int, db: Session = Depends(get_db)):
    hito_pagado, error = crud.aprobar_y_pagar_hito(db, hito_id=hito_id)
    if error:
         raise HTTPException(status_code=400, detail=error)
    return hito_pagado
