from sqlalchemy import Table, Column, BigInteger, ForeignKey, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db.base import Base
from .model_sensor import sensor_model
from ..ruleassignment import RuleAssignment
from ..tagbuilder import TagBuilder
import numpy as np


model_indications = Table('mi_diagnostic',Base.metadata,
    Column('mi_id', BigInteger, ForeignKey('model_indication.id'), primary_key=True),
    Column('diagnostic_id', BigInteger, ForeignKey('diagnostic.id'), primary_key=True)
)

class ModelIndication(Base):
    __tablename__ = 'model_indication'

    id = Column(BigInteger, primary_key=True)
    name= Column(String(255))
    mnemonic = Column(String(100))
    model_blueprint = Column(String(100))
    sensors = relationship('Sensors', secondary=sensor_model, back_populates='model_indications')
    diagnostics = relationship('Diagnostic', secondary=model_indications, back_populates='model_indications')

    def __init__(self) -> None:
        super().__init__()

    def create_name(self):
        sensors = '['
        for i in range(len(self.sensors)):
            if i != len(self.sensors)-1:
                sensors+=self.sensors[i].tag_alias+', '
            else:
                sensors+=self.sensors[i].tag_alias+']'
        self.name='ModelIndications('+self.model_blueprint+','+self.mnemonic+','+sensors+')'

    def __repr__(self):
        sensors = '['
        for i in range(len(self.sensors)):
            if i != len(self.sensors)-1:
                sensors+=self.sensors[i].tag_alias+', '
            else:
                sensors+=self.sensors[i].tag_alias+']'
        
        # return 'ModelIndications('+self.model_blueprint+','+self.mnemonic+','+sensors+')'
        return self.name

    #private
    def pair_rule_and_asset(self, tag_rules, asset_tags):
        '''
        :params:
        tag_rules: list of str
            ModelIndication's tag rules
        asset_tags: list of Sensors
            ModelIndication's sensors input
        '''
        result = []
        for rule in tag_rules:
            for asset in asset_tags:
                result.append((rule, asset))
        return result

    def calculate(self, fault, date, model="MECHANICAL") -> float:
        '''
        :params:
        model: str
            MECHANICAL
        date: datetime
        menghitung model indication
        '''
        # tag rules dictionary
        mi_tag_rules = self.mnemonic
        mi_tag_rules = mi_tag_rules[1:-1]
        mi_tag_rules = mi_tag_rules.split(", ")

        mi_sensors = []
        for sensor in self.sensors:
            mi_sensors.append(sensor)

        indication = []

        for rule, sensor in self.pair_rule_and_asset(mi_tag_rules, mi_sensors):
            # initialize tag
            tag = TagBuilder(sensor=sensor, fault=fault, date=date)
            ra = RuleAssignment(tag)
            rules = {
                'H': ra.high,
                'VH': ra.very_high,
                'SH': ra.step_high,
                'SVH': ra.step_very_high,
                'VAR': ra.variance,
                'AVMH': ra.actual_high_model,
                'L': ra.low,
                'LH': ra.long_high,
                'SL': ra.step_low,
                'SVL': ra.step_very_low,
                'VL': ra.very_low
            }
            # assign rule
            ind = rules.get(rule)(tag)
            indication.append(ind)
        return np.sum(indication)
        # return round(random.uniform(0,2),3)