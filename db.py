from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()
engine = create_engine("postgresql://cal_gastos_db_user:5AGCwr9zv0w7ypN415NkFW2ve5KSYPqw@dpg-d2j2ulogjchc73fp20a0-a/cal_gastos_db")
Session = sessionmaker(bind=engine)

class Gasto(Base):
    __tablename__ = "gastos"
    id = Column(Integer, primary_key = True, autoincrement=True)
    fecha = Column(DateTime, default = datetime.now)
    categoria = Column(String, nullable=False)
    monto = Column(Float, nullable=False)
    descripcion = Column(String, nullable=True)

Base.metadata.create_all(engine)