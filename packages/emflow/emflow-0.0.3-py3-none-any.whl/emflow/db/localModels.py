import os
from dataclasses import dataclass
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

@dataclass
class Statistics(Base):
    __tablename__ = 'statistics'
    name:str = Column(String(127), primary_key=True)
    df:float = Column(Float)
    astig:float = Column(Float)
    shift:float = Column(Float)
    fit:float = Column(Float)
    mark:int = Column(Integer)
    picks:int = Column(Integer)

@dataclass
class Tasks(Base):
    __tablename__ = 'tasks'
    name:str = Column(String(127), primary_key=True)
    id:str = Column(String(127))
    ids:list = Column(JSON)
    modules:list = Column(JSON)
    test:bool = Column(Boolean)
    movies_id:str = Column(String(127))
    extract_id:str = Column(String(127))

def get_engine(localDir):
    return create_engine('sqlite:////'+os.path.join(localDir, 'emflow.sqlite'), convert_unicode=True)

def create_all(localDir):
    engine = get_engine(localDir)
    Base.metadata.create_all(engine)

def drop_all(localDir):
    engine = get_engine(localDir)
    Base.metadata.drop_all(engine)

def yield_local_session(localDir):
    engine = get_engine(localDir)
    Session = sessionmaker(bind=engine)
    db_session = Session()
    yield db_session
    db_session.close()

