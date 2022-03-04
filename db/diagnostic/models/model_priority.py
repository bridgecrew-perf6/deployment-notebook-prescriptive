from db.base import Base
from db.assets.models.model_asset_failure import AssetFailure
from sqlalchemy import Column, BigInteger, String, ForeignKey, Integer, Text


class Priority(Base):
    __tablename__ = 'priority'
    
    id = Column(BigInteger, primary_key=True)
    fault = Column(String(100), ForeignKey('fault.name'))
    # recomendation = db.Column(db.Text())
    recomendation = Column(Text())
    priority = Column(Integer)
    next = Column(Integer)

    def __init__(self) -> None:
        super().__init__()

    # def make_data_dummy_rekomendasi(fault,priority,asset):
    #     recs = Priority.query.with_entities(Priority.priority,Priority.recomendation).filter(Priority.fault==fault,Priority.priority.in_(priority)).order_by(Priority.priority.asc()).all()
    #     for i in range (len (recs)):

    def get_recomendation(fault,an_prior):
        prior = [prior[0] for prior in an_prior]
        an = [an[1] for an in an_prior]
        recs = Priority.query.with_entities(Priority.priority, Priority.recomendation).filter(Priority.fault==fault, Priority.priority.in_(prior)).order_by(Priority.priority.asc()).all()
        # print(recs)
        result = []
        i=0
        for i in range (len (recs)):
            first = AssetFailure.get_first_occurence(fault,recs[i].priority)
            last = AssetFailure.get_last_occurence(fault,recs[i].priority)
            result.append({
                'priority':recs[i].priority,
                'recomendation':recs[i].recomendation,
                'occurence':an[i],
                'first':first,
                'last':last
            })
            i+=1
        return result