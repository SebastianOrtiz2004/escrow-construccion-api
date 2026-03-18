from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from models import RolEnum, EstadoContratoEnum, EstadoHitoEnum

# ---- Esquemas de Usuario ----
class UsuarioBase(BaseModel):
    nombre: str
    rol: RolEnum

class UsuarioCreate(UsuarioBase):
    pass

class Usuario(UsuarioBase):
    id: int
    saldo_billetera: float

    model_config = ConfigDict(from_attributes=True)

# ---- Esquemas de Hito de Obra ----
class HitoObraBase(BaseModel):
    descripcion: str
    monto_asignado: float

class HitoObraCreate(HitoObraBase):
    pass

class HitoObra(HitoObraBase):
    id: int
    contrato_id: int
    estado: EstadoHitoEnum
    evidencia_url: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

# ---- Esquemas de Contrato ----
class ContratoBase(BaseModel):
    titulo: str
    descripcion: str
    cliente_id: int
    maestro_id: int

class ContratoCreate(ContratoBase):
    pass

class Contrato(ContratoBase):
    id: int
    estado: EstadoContratoEnum
    saldo_retenido: float
    hitos: List[HitoObra] = []

    model_config = ConfigDict(from_attributes=True)
