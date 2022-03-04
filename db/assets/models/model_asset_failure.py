from db.base import Base
from sqlalchemy import Column, BigInteger, DateTime, ForeignKey, Integer, String
from sqlalchemy import func

class AssetFailure(Base):
    __tablename__='asset_failure'

    id = Column(BigInteger, primary_key=True)
    date = Column(DateTime)
    asset_id = Column(BigInteger, ForeignKey('assets.id'))
    fault = Column(String(100), ForeignKey('fault.name'))
    priority = Column(Integer)

    def __init__(self,date, asset_id, fault, priority):
        self.date=date
        self.asset_id=asset_id
        self.fault=fault
        self.priority=priority

    def get_first_occurence(fault,prio=None):
        if prio:
            first = AssetFailure.query.filter_by(priority=prio,fault=fault).order_by(AssetFailure.date.asc()).first()
            if first:
                return first.date
            
        else:
            first = AssetFailure.query.filter_by(fault=fault).order_by(AssetFailure.date.asc()).first()
            if first:
                return first.date
            
        return None
    
    def get_last_occurence(fault,prio=None):
        if prio:
            first = AssetFailure.query.filter_by(priority=prio,fault=fault).order_by(AssetFailure.date.desc()).first()
            if first:
                return first.date
        else:
            first = AssetFailure.query.filter_by(fault=fault).order_by(AssetFailure.date.desc()).first()
            if first:
                return first.date
        return None

    def get_anomaly_severity(fault):
        query = AssetFailure.query.with_entities(AssetFailure.priority,func.count(AssetFailure.id)).filter(AssetFailure.fault==fault).group_by(AssetFailure.priority)\
            .order_by(AssetFailure.priority.asc()).all()
        # print(query)
        se = [a[0] for a in query]
        an = [a[1] for a in query]
        if se:
            index=an.index(max(an))
            se = se[index]

        return an,se,query