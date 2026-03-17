import enum
from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship

from database import Base

class RolEnum(enum.Enum):
    CLIENTE = "CLIENTE"
    MAESTRO = "MAESTRO"

class EstadoContratoEnum(enum.Enum):
    BORRADOR = "BORRADOR"
    FONDEADO = "FONDEADO"
    COMPLETADO = "COMPLETADO"
    DISPUTA = "DISPUTA"

class EstadoHitoEnum(enum.Enum):
    PENDIENTE = "PENDIENTE"
    TRABAJANDO = "TRABAJANDO"
    EN_REVISION = "EN_REVISION"
    PAGADO = "PAGADO"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True)
    rol = Column(Enum(RolEnum), nullable=False)
    saldo_billetera = Column(Float, default=0.0)

class Contrato(Base):
    __tablename__ = "contratos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("usuarios.id"))
    maestro_id = Column(Integer, ForeignKey("usuarios.id"))
    estado = Column(Enum(EstadoContratoEnum), default=EstadoContratoEnum.BORRADOR)
    saldo_retenido = Column(Float, default=0.0)

    # Relaciones para los IDs (usando foreign_keys específicos para diferenciar)
    cliente = relationship("Usuario", foreign_keys=[cliente_id])
    maestro = relationship("Usuario", foreign_keys=[maestro_id])
    
    # Un contrato tiene muchos hitos
    hitos = relationship("HitoObra", back_populates="contrato", cascade="all, delete-orphan")

class HitoObra(Base):
    __tablename__ = "hitos_obra"

    id = Column(Integer, primary_key=True, index=True)
    contrato_id = Column(Integer, ForeignKey("contratos.id"))
    descripcion = Column(String)
    monto_asignado = Column(Float, default=0.0)
    estado = Column(Enum(EstadoHitoEnum), default=EstadoHitoEnum.PENDIENTE)
    evidencia_url = Column(String, nullable=True)

    contrato = relationship("Contrato", back_populates="hitos")
