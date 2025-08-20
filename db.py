from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

engine = create_engine("postgresql://user:password@localhost/calculadora_gastos")
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Gasto(Base):
    __tablename__ = "gastos"
    id = Column(Integer, primary_key = True, autoincrement=True)
    fecha = Column(DateTime, default = datetime.now)
    categoria = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)

Base.metadata.create_all(engine)