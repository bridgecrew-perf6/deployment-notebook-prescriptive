from db.base import Base
from .model_calculated_tags import CalculatedTags
from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.orm import relationship


class Tags(Base):
    __tablename__='tags'

    tag = Column(String(100), primary_key=True)
    sensors = relationship('Sensors', backref='tags', lazy=True)
    input_calc_tag = Column(String(100), ForeignKey('calculated_tags.calc_tag'), nullable=True)

    def __init__(self, tag) -> None:
        self.tag = tag