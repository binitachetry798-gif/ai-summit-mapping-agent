from sqlalchemy import create_engine, Column, String, Float, Integer, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./mse_mapper.db")

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class MSEProfile(Base):
    __tablename__ = "mse_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    udyam_number = Column(String(50), unique=True, nullable=True, index=True)
    business_name = Column(String(200), nullable=False)
    owner_name = Column(String(200), nullable=False)
    phone = Column(String(20), nullable=True)
    location = Column(String(200), nullable=False)
    state = Column(String(100), nullable=False)
    product_description = Column(Text, nullable=False)
    ondc_category = Column(String(200), nullable=True)
    ondc_subcategory = Column(String(200), nullable=True)
    hsn_code = Column(String(20), nullable=True)
    annual_capacity = Column(Integer, nullable=True)
    preferred_language = Column(String(20), default="en")
    verified = Column(Boolean, default=False)
    matched_snp_id = Column(String(100), nullable=True)
    match_score = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class SNPProfile(Base):
    __tablename__ = "snp_profiles"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    domain = Column(Text, nullable=False)
    sectors = Column(Text, nullable=False)           # JSON list
    regions = Column(Text, nullable=False)            # JSON list
    operational_capacity = Column(Float, nullable=False)
    contact = Column(String(200), nullable=True)
    ondc_id = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)
