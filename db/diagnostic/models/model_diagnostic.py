# from flaskr.models import db
from sqlalchemy import Column, String, BigInteger, Text, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base, session
from .model_model_indication import ModelIndication, model_indications
from ..expressions.expressions import BooleanExpression
import re


class Diagnostic(Base):
    __tablename__ = 'diagnostic'

    id = Column(BigInteger, primary_key=True)
    rule_name = Column(String(100))
    # expression = db.Column(db.String(255))
    expression = Column(Text())
    model_indications = relationship('ModelIndication', secondary=model_indications, back_populates='diagnostics')
    fault = Column(String(100), ForeignKey('fault.name'))

    def __init__(self,rule_name, expression):
        self.rule_name=rule_name
        self.expression=expression

    def add_expression(self,exp):
        self.expression=exp

    def get_asset(self):
        mi = self.model_indications
        asset = mi[0].sensors[0].asset
        return asset

    def get_sensors(self):
        # if exclude:
        #     mi = [a for a in self.model_indications if a.model_blueprint != None ]
        # else:
        mi = self.model_indications
        sensors = set()
        for a in mi:
            m = a.sensors
            for sensor in m:
                sensors.add(sensor)
        sensors = list(sensors)
        return sensors

    def parse_if_stmt(self,date,fault):
        # get value of MI
        models = {}
        p1 = r"(?<=\[)([^*><=|&]+)(?=\])|(\[|\])"
        reg = re.compile(p1)
        tokens = reg.split(self.expression)
        tokens = [a for a in tokens if a is not None]
        tokens = [t.strip() for t in tokens if t.strip() not in ["", "[", "]"]]
        model = [model for model in tokens if model.startswith("Model")]
        for i in model:
            models[i]=0
        id_model = [s.strip('Model ') for s in model]

        for i in range (0, len(id_model)):
            # print(id_model[i])
            m = session.query(ModelIndication).get(id_model[i]).calculate(fault,date)
            # print(m)
            models[model[i]]=str(m)

        tokens=[models.get(item,item) for item in tokens]

        #separate if stmt
        new_exp = ' '.join(tokens)
        p2 = r"(\bIF\b|\bTHEN\b|\bELIF\b|\bELSE\b)"
        reg = re.compile(p2)


        # reg = re.compile('|'.join(x for x in patterns))

        tokens = reg.split(new_exp)
        tokens = [t.strip() for t in tokens if t.strip() != ""]
        return tokens

    def calculate(self, date,fault):
        stmts = self.parse_if_stmt(date,fault)
        conditional_op = ['IF', 'THEN', 'ELIF', 'ELSE']
        # make boolean exp based on class BooleanExpression
        stmt = [a for a in stmts if a not in conditional_op]
        i=0
        # print(stmt, len(stmt))
        # assign default value prior = 0
        priority=0
        while i < len(stmt):
            # print(i)
            if i>len(stmt)-2:
                priority = stmt[-1]
                break
                # return PRIORITY[stmt[-1]]
            elif BooleanExpression(stmt[i]).evaluate() == True:
                priority = stmt[i+1]
                break
                # return PRIORITY[stmt[i+1]]
            i+=2
        # print('======== PRIORITY ', priority, ' ========')
        return priority