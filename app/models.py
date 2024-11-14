from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
import datetime
import uuid

Base = declarative_base()

# Holds business details
class Business(Base):
    __tablename__   = "business"
    id              = Column(String(100), primary_key=True)
    name            = Column(String(100), nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    created_by      = Column(String(100), nullable=True, default="Developer")
    updated_by      = Column(String(100), nullable=True, default="Developer")

    def __repr__(self):
        return (
            f"<Business(id='{self.id}', name='{self.name}', "
            f"created_at='{self.created_at}', updated_at='{self.updated_at}', "
            f"created_by='{self.created_by}', updated_by='{self.updated_by}')>"
        )

# Holds Symptoms data
class Symptoms(Base):
    __tablename__   = "symptoms"
    id              = Column(String(100), primary_key=True)
    name            = Column(String(100), nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    created_by      = Column(String(100), nullable=True, default="Developer")
    updated_by      = Column(String(100), nullable=True, default="Developer")

    def __repr__(self):
        return (
            f"<Symptoms(id='{self.id}', name='{self.name}', "
            f"created_at='{self.created_at}', updated_at='{self.updated_at}', "
            f"created_by='{self.created_by}', updated_by='{self.updated_by}')>"
        )

# Holds business diagnostic data
class Diagnostics(Base):
    __tablename__   = "diagnostics"
    id              = Column(String(100), primary_key=True, default=uuid.uuid4)
    business_id     = mapped_column(ForeignKey("business.id"), nullable=False)
    symptom_id      = mapped_column(ForeignKey("symptoms.id"), nullable=False)
    Diagnostics     = Column(Boolean, nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    created_by      = Column(String(100), nullable=True, default="Developer")
    updated_by      = Column(String(100), nullable=True, default="Developer")

    def __repr__(self):
        return (
            f"<Diagnostics(id='{self.id}', business_id='{self.business_id}', symptom_id='{self.symptom_id}' Diagnostics='{self.Diagnostics}'"
            f"created_at='{self.created_at}', updated_at='{self.updated_at}', "
            f"created_by='{self.created_by}', updated_by='{self.updated_by}')>"
        )