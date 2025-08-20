from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///local.db") #Fallback para desarrollo

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind = engine)
Base = declarative_base()

class Gasto(Base):
    __tablename__ = "gastos"
    id = Column(Integer, primary_key = True)
    fecha = Column(String)
    categoria = Column(String)
    monto = Column(Float)
    descripcion = Column(String)

Base.metadata.create_all(engine)