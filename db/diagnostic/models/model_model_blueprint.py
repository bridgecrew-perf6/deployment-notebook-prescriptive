from sqlalchemy import Column, String
from db.base import Base


class ModelBlueprint(Base):
    __tablename__='model_blueprint'

    type = Column(String(100), primary_key=True)

    def __init__(self, tipe):
        self.type=tipe