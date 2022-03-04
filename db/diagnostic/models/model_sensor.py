from db.base import Base
from sqlalchemy import Table, Column, BigInteger, ForeignKey, String, Float
from sqlalchemy.orm import relationship


# table relasi antara table sensors dengan table model_indication
sensor_model = Table('sensor_model',Base.metadata,
    Column('id', BigInteger,primary_key=True),
    Column('sensor_id', BigInteger, ForeignKey('sensors.id')),
    Column('mi_id', BigInteger, ForeignKey('model_indication.id'))
)

class Sensors(Base):
    __tablename__ = 'sensors'

    id = Column(BigInteger, primary_key=True)
    asset = Column(BigInteger, ForeignKey('assets.id'))
    tag_alias = Column(String(100), ForeignKey('tags.tag'))
    name = Column(String(100), nullable=True)
    model_indications = relationship('ModelIndication', secondary=sensor_model,back_populates='sensors')
    actual_high = Column(Float, nullable=True)
    actual_low = Column(Float, nullable=True)
    adaptation_high = Column(Float, nullable=True)
    adaptation_low = Column(Float, nullable=True)
    step_high = Column(Float, nullable=True)
    step_low = Column(Float, nullable=True)
    runtime = relationship('Runtime', lazy=True)

    model_tag = relationship('ModelTag', lazy='dynamic')
    asset_ = relationship('Assets', back_populates='sensors')

    # DEFAULT_VALUE = db.Column(db.Float, nullable=True)
    # residual_threshold_positive = db.Column(db.Float, nullable=True)
    # residual_threshold_negative = db.Column(db.Float, nullable=True)
    # sprt_positive = db.Column(db.Float, nullable=True)
    # sprt_negative = db.Column(db.Float, nullable=True)
    # is_independent = db.Column(db.Boolean, nullable=True)
    # residual_variance = db.Column(db.Float, nullable=True)
    # outlier_positive = db.Column(db.Float, nullable=True)
    # outlier_negative = db.Column(db.Float, nullable=True)
    # tag_type = db.Column(db.String(100), nullable=True)
    # data_type = db.Column(db.String(100), nullable=True)
    # standard_units = db.Column(db.String(100), nullable=True)
    # flatline_number = db.Column(db.Float, nullable=True)
    # is_driver = db.Column(db.Boolean, nullable=True)
    # spike_sensitivity = db.Column(db.Float, nullable=True)
    # decimals = db.Column(db.Integer, nullable=True)
    # alarm_type = db.Column(db.String(100), nullable=True)

    def __init__(self, asset, tag, name) -> None:
        self.asset = asset
        self.tag_alias = tag
        self.name = name