from sqlalchemy.orm import Session
import models, schemas

# ---- Usuarios ----
def get_usuario(db: Session, usuario_id: int):
    return db.query(models.Usuario).filter(models.Usuario.id == usuario_id).first()

def get_usuarios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Usuario).offset(skip).limit(limit).all()

def create_usuario(db: Session, usuario: schemas.UsuarioCreate):
    db_usuario = models.Usuario(nombre=usuario.nombre, rol=usuario.rol)
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

# ---- Contratos ----
def get_contrato(db: Session, contrato_id: int):
    return db.query(models.Contrato).filter(models.Contrato.id == contrato_id).first()

def get_contratos(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Contrato).offset(skip).limit(limit).all()

def create_contrato(db: Session, contrato: schemas.ContratoCreate):
    db_contrato = models.Contrato(cliente_id=contrato.cliente_id, maestro_id=contrato.maestro_id)
    db.add(db_contrato)
    db.commit()
    db.refresh(db_contrato)
    return db_contrato
