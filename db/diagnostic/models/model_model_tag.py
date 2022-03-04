from sqlalchemy import Column, BigInteger, ForeignKey, String, Float, Boolean
from db.base import Base
from .model_model_blueprint import ModelBlueprint


class ModelTag(Base):
    __tablename__='model_tag'

    type = Column(String(100), ForeignKey('model_blueprint.type'), primary_key=True)
    sensor = Column(BigInteger, ForeignKey('sensors.id'), primary_key=True)
    residual_positive_threshold = Column(Float, nullable=True)
    residual_negative_threshold = Column(Float, nullable=True)
    active_in_model = Column(Boolean, default=False)


    def __init__(self, tipe, sensor):
        self.type=tipe
        self.sensor=sensor

    def __repr__(self) -> str:
        return self.type + '-' + str(self.sensor)