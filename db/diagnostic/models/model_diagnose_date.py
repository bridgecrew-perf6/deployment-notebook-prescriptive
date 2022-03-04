from sqlalchemy import Column, DateTime
from sqlalchemy.orm import relationship
from db.base import Base, session
from datetime import datetime

from .model_diagnostic import Diagnostic
from .model_runtime import Runtime


class DiagnoseDate(Base):
    __tablename__ = 'diagnose_date'

    timestamp = Column(DateTime(), primary_key=True)

    def __init__(self, timestamp):
        self.timestamp = timestamp

    def _get_last_diagnose():
        return session.query(DiagnoseDate).first().timestamp