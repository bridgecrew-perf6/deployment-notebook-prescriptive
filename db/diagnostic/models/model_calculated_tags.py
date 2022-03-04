from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from db.base import Base


class CalculatedTags(Base):
    __tablename__='calculated_tags'

    calc_tag = Column(String(100), primary_key=True)
    expression = Column(String(255))
    tags_input = relationship('Tags', lazy='select', backref='calculated_tags')