from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    func,
    Index,
    Float,
    ForeignKey,
    UUID as SQLAlchemyUUID,
)
import uuid
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import expression

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    api_key = Column(String, unique=True, index=True, nullable=False)
    is_active = Column(Boolean, server_default=expression.true(), nullable=False)
    is_admin = Column(
        Boolean, server_default=expression.false(), nullable=False, name="is_admin"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, is_active={self.is_active})>"

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "api_key": self.api_key if self.is_admin else None,
        }


class PanelModel(Base):
    __tablename__ = "panel_models"

    id = Column(
        SQLAlchemyUUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4
    )
    name = Column(String, nullable=False)
    capacity = Column(Float, nullable=False)  # in kWp
    efficiency = Column(Float, nullable=False)  # in percentage
    manufacturer = Column(String, nullable=False)
    type = Column(String, nullable=False)  # e.g., Monocristalino

    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), onupdate=func.now(), server_default=func.now()
    )

    __table_args__ = (
        Index("ix_panel_models_user_id", "user_id"),
        Index("ix_panel_models_manufacturer_type", "manufacturer", "type", "user_id"),
    )

    def to_dict(self):
        return {
            "id": str(self.id),
            "name": self.name,
            "capacity": self.capacity,
            "efficiency": self.efficiency,
            "manufacturer": self.manufacturer,
            "type": self.type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
