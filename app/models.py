from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapped_column
import datetime
import uuid

Base = declarative_base()

# Holds business details
class Business(Base):
    __tablename__   = "business"
    id              = Column(Integer, primary_key=True)
    name            = Column(String(100), nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    created_by      = Column(String(100), nullable=True, default="Developer")
    updated_by      = Column(String(100), nullable=True, default="Developer")

# Holds Symptoms data
class Symptoms(Base):
    __tablename__   = "symptoms"
    id              = Column(String(100), primary_key=True)
    name            = Column(String(100), nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    created_by      = Column(String(100), nullable=True, default="Developer")
    updated_by      = Column(String(100), nullable=True, default="Developer")

# Holds business diagnostic data
class Diagnostics(Base):
    __tablename__   = "diagnostics"
    id              = Column(String(100), primary_key=True, default=uuid)
    business_id     = mapped_column(ForeignKey("business.id"), nullable=False)
    symptom_id      = mapped_column(ForeignKey("symptoms.id"), nullable=False)
    Diagnostics     = Column(Boolean, nullable=False)
    created_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    updated_at      = Column(DateTime(timezone=True), nullable=False, default=datetime.datetime.now)
    created_by      = Column(String(100), nullable=True, default="Developer")
    updated_by      = Column(String(100), nullable=True, default="Developer")