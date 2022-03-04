from db.base import Base
from sqlalchemy import Column, BigInteger, String, ForeignKey
from sqlalchemy.orm import relationship

class Fault(Base):
    __tablename__ = 'fault'

    name = Column(String(100), primary_key=True)
    diagnostics=relationship('Diagnostic', lazy='dynamic')

    def __init__(self) -> None:
        super().__init__()