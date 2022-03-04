from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base  
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

db = create_engine('postgresql+psycopg2://postgres:Ontar10!@localhost:5432/proto-app')

Session = sessionmaker(db)  
session = Session()

# base.metadata.create_all(db)