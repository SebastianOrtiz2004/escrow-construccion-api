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

def get_contratos_por_usuario(db: Session, usuario_id: int):
    return db.query(models.Contrato).filter(
        (models.Contrato.cliente_id == usuario_id) | (models.Contrato.maestro_id == usuario_id)
    ).all()

def create_contrato(db: Session, contrato: schemas.ContratoCreate):
    db_contrato = models.Contrato(
        titulo=contrato.titulo,
        descripcion=contrato.descripcion,
        cliente_id=contrato.cliente_id, 
        maestro_id=contrato.maestro_id
    )
    db.add(db_contrato)
    db.commit()
    db.refresh(db_contrato)
    return db_contrato

# ---- Hitos de Obra ----
def create_hito_obra(db: Session, hito: schemas.HitoObraCreate, contrato_id: int):
    db_hito = models.HitoObra(**hito.model_dump(), contrato_id=contrato_id)
    db.add(db_hito)
    db.commit()
    db.refresh(db_hito)
    return db_hito

# ---- Lógica de Escrow (Hito 2) ----
def fondear_contrato(db: Session, contrato_id: int):
    # 1. Obtener contrato
    contrato = get_contrato(db, contrato_id)
    if not contrato:
        return None, "Contrato no encontrado"
    
    # Verificar que esté en BORRADOR
    if contrato.estado != models.EstadoContratoEnum.BORRADOR:
        return None, "El contrato no está en estado BORRADOR"
    
    # 2. Calcular costo total de los hitos
    total_costo = sum(hito.monto_asignado for hito in contrato.hitos)
    if total_costo <= 0:
         return None, "El contrato necesita hitos con monto mayor a 0 para fondearse"
    
    # 3. Verificar que el Cliente tenga saldo suficiente
    cliente = contrato.cliente
    if cliente.saldo_billetera < total_costo:
        return None, f"Saldo insuficiente. El cliente tiene {cliente.saldo_billetera} y requiere {total_costo}."
    
    # Transacción Atómica
    try:
        # 4. Restar saldo al Cliente
        cliente.saldo_billetera -= total_costo
        
        # 5. Sumar saldo al Escrow del Contrato
        contrato.saldo_retenido += total_costo
        
        # 6. Cambiar estado a FONDEADO
        contrato.estado = models.EstadoContratoEnum.FONDEADO
        
        db.commit()
        db.refresh(contrato)
        return contrato, None
    except Exception as e:
        db.rollback()
        return None, f"Error en la transacción: {str(e)}"

# ---- Flujo 2: Lógica de Hitos (Secuencia) ----

# Función para que el Maestro cambie el estado a 'EN_REVISION'
def enviar_hito_a_revision(db: Session, hito_id: int):
    hito = db.query(models.HitoObra).filter(models.HitoObra.id == hito_id).first()
    if not hito:
        return None, "Hito no encontrado"
    if hito.estado != models.EstadoHitoEnum.PENDIENTE:
        return None, "Solo se pueden enviar a revisión hitos que están en estado PENDIENTE."
    
    hito.estado = models.EstadoHitoEnum.EN_REVISION
    db.commit()
    db.refresh(hito)
    return hito, None

def aprobar_y_pagar_hito(db: Session, hito_id: int):
    # 1. Obtener Hito
    hito = db.query(models.HitoObra).filter(models.HitoObra.id == hito_id).first()
    if not hito:
        return None, "Hito no encontrado"
    
    # Validar que esté en revisión
    if hito.estado != models.EstadoHitoEnum.EN_REVISION:
        return None, "El hito no está listo para aprobación (No está en EN_REVISION)"
    
    contrato = hito.contrato
    if contrato.estado != models.EstadoContratoEnum.FONDEADO:
        return None, "El contrato no está fondeado, no se pueden realizar pagos."
    
    maestro = contrato.maestro

    # Transacción Atómica
    try:
        # 2. Cambiar estado del hito a PAGADO
        hito.estado = models.EstadoHitoEnum.PAGADO
        
        # 3. Restar el monto asignado del saldo retenido (Escrow)
        contrato.saldo_retenido -= hito.monto_asignado
        
        # 4. Sumar el monto asignado a la billetera del maestro
        maestro.saldo_billetera += hito.monto_asignado
        
        # 5. (Opcional) Verificar si todos los hitos están pagados
        todos_pagados = all(h.estado == models.EstadoHitoEnum.PAGADO for h in contrato.hitos)
        if todos_pagados:
            contrato.estado = models.EstadoContratoEnum.COMPLETADO
            
        db.commit()
        db.refresh(hito)
        db.refresh(contrato)
        db.refresh(maestro)
        return hito, None
        
    except Exception as e:
        db.rollback()
        return None, f"Error en la transacción de pago: {str(e)}"
