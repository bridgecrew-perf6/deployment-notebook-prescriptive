from db.assets.models.model_asset_failure import AssetFailure
from db.assets.models.model_assets import Assets
from .model_sensor import Sensors
from db.base import Base
from sqlalchemy import distinct, func
from sqlalchemy.orm import aliased
from sqlalchemy import and_
from sqlalchemy import Column, DateTime, BigInteger, ForeignKey, Float, String
import math


class Runtime(Base):
    __tablename__ = 'runtime'

    timestamp = Column(DateTime, primary_key=True)
    sensor = Column(BigInteger, ForeignKey('sensors.id'), primary_key=True)
    fault = Column(String(100), ForeignKey('fault.name'), primary_key=True)
    actual = Column(Float, nullable=True)
    actual_smoothed = Column(Float, nullable=True)
    estimate = Column(Float, nullable=True)
    residual = Column(Float, nullable=True)
    residual_smoothed = Column(Float, nullable=True)
    residual_indication_positive = Column(Float, nullable=True)
    residual_indication_negative = Column(Float, nullable=True)

    def __init__(self, timestamp, sensor, fault, actual, actual_smoothed, estimate, residual, residual_smoothed, residual_indication_positive, residual_indication_negative):
        self.timestamp = timestamp
        self.sensor = sensor
        self.fault = fault
        self.actual = actual
        self.actual_smoothed = actual_smoothed
        self.estimate = estimate
        self.residual = residual
        self.residual_smoothed = residual_smoothed
        self.residual_indication_positive = residual_indication_positive
        self.residual_indication_negative = residual_indication_negative

    # def _fault_runtime(per_page):
        # last_page = Runtime.query.paginate(page=1,per_page=per_page).pages
        # fault_runtime = Runtime.query.join(Sensors,Sensors.id==Runtime.sensor, isouter=True).join(AssetFailure,AssetFailure.asset_id==Sensors.asset, isouter=True)\
        #         .filter(Runtime.timestamp==AssetFailure.date, Runtime.sensor==sensor).order_by(Runtime.timestamp.asc()).paginate(page=last_page, per_page=per_page)

    def is_data_exists(sensors,fault,date):
        sensors = [sensor.id for sensor in sensors]
        return True if Runtime.query.filter_by(fault=fault,timestamp=date).filter(Runtime.sensor.in_(sensors)).first() is not None else False

    def get_sensors(asset,fault):
        s = Assets.query.get(asset).sensors.all()
        s = [s.id for s in s]
        x = [a[0] for a in db.session.query(distinct(Runtime.sensor)).filter(Runtime.fault==fault, Runtime.sensor.in_(s)).all()]
        return Sensors.query.filter(Sensors.id.in_(x)).all()
    
    # def get_sensors(asset_id,fault):
    #     return Runtime.query.filter_by(fault=fault).with_entities(func.count(Runtime.id))        

    def make_data_dummy_visualization(sensors,fault,date):
        for sensor in sensors:
            inner_stmt = db.session.query(Runtime.timestamp,Runtime.actual,Runtime.estimate,Runtime.fault,Sensors.id,Sensors.name, Sensors.asset).join(Sensors,Sensors.id==Runtime.sensor)\
                    .filter(Sensors.id==sensor.id,Runtime.fault==fault, Runtime.timestamp==date)
            subq = inner_stmt.subquery()
            rt = aliased(Runtime,subq)
            af = aliased(AssetFailure)
            query = db.session.query(rt.timestamp,subq.c.name,rt.fault,subq.c.asset,rt.actual,rt.estimate,af.priority).select_entity_from(subq)\
                .outerjoin(af, and_ (rt.timestamp==af.date , af.fault==rt.fault)).first()
            ts=query[0].isoformat()
            prio = query[6]
            query = list(query)
            query[0]=ts
            # if prio:
            #     query[6]=prio
            # else:
            #     query[6]='NULL'
            query=tuple(query)
        return query

    def get_runtimes(sensors,_sensors,fault,per_page):
        from flaskr.diagnostics.schema.schema_runtime import runtime_schema
        results=[]
        last_page=None
        _sensors = [sensor for sensor in _sensors if sensor not in sensors ]
        print(sensors,_sensors)

        for sensor in _sensors:
            if last_page is None:
                last_page = Runtime.get_last_page(sensor,fault,per_page) - 2
            print('last',last_page,sensor)
            # runtimes = Runtime.query.filter_by(sensor=sensor.id).order_by(Runtime.timestamp.asc()).paginate(page=last_page, per_page=per_page)
            inner_stmt = db.session.query(Runtime.timestamp,Runtime.actual,Runtime.estimate,Runtime.fault,Sensors.id).join(Sensors,Sensors.id==Runtime.sensor)\
                .filter(Sensors.id==sensor.id,Runtime.fault==fault)
            subq = inner_stmt.subquery()
            rt = aliased(Runtime,subq)
            af = aliased(AssetFailure)
            query = db.session.query(rt.timestamp,rt.actual,rt.estimate,rt.fault).select_entity_from(subq)\
                .outerjoin(af, and_ (rt.timestamp==af.date , af.fault==rt.fault))\
                .order_by(Runtime.timestamp.asc())
            # .filter(rt.sensor==sensor.id)\
            # print(str(query))
            runtimes = query\
                .paginate(page=last_page, per_page=per_page)

            temp = {
                'sensor_id': sensor.id,
                'sensor': sensor.name,
                'runtimes':runtime_schema.dump(runtimes.items),
                # 'last_page': runtimes.pages
                # 'item_count':runtimes.total
            }
            results.append(temp)

        for sensor in sensors:
            if last_page is None:
                last_page = Runtime.get_last_page(sensor,fault,per_page) - 2
            print('last',last_page,sensor)
            # runtimes = Runtime.query.filter_by(sensor=sensor.id).order_by(Runtime.timestamp.asc()).paginate(page=last_page, per_page=per_page)
            inner_stmt = db.session.query(Runtime.timestamp,Runtime.actual,Runtime.estimate,Runtime.fault,Sensors.id).join(Sensors,Sensors.id==Runtime.sensor)\
                .filter(Sensors.id==sensor.id,Runtime.fault==fault)
            subq = inner_stmt.subquery()
            rt = aliased(Runtime,subq)
            af = aliased(AssetFailure)
            query = db.session.query(rt.timestamp,rt.actual,rt.estimate,rt.fault,af.priority).select_entity_from(subq)\
                .outerjoin(af, and_ (rt.timestamp==af.date , af.fault==rt.fault))\
                .order_by(Runtime.timestamp.asc())
            # .filter(rt.sensor==sensor.id)\
            # print(str(query))
            runtimes = query\
                .paginate(page=last_page, per_page=per_page)
            temp = {
                'sensor_id': sensor.id,
                'sensor': sensor.name,
                'runtimes':runtime_schema.dump(runtimes.items),
                # 'last_page': runtimes.pages
                # 'item_count':runtimes.total
            }
            results.append(temp)
        return results

    def get_last_page(sensor,fault,page):
        inner_stmt = db.session.query(Runtime.timestamp,Runtime.actual,Runtime.estimate,Runtime.fault,Sensors.id).join(Sensors,Sensors.id==Runtime.sensor)\
                .filter(Sensors.id==sensor.id,Runtime.fault==fault)
        subq = inner_stmt.subquery()
        rt = aliased(Runtime,subq)
        af = aliased(AssetFailure)
        last_page = db.session.query(rt.timestamp,rt.actual,rt.estimate,rt.fault,af.priority).select_entity_from(subq)\
            .outerjoin(af, and_ (rt.timestamp==af.date , af.fault==rt.fault))\
            .order_by(Runtime.timestamp.asc()).paginate(page=1, per_page=page).pages
        return last_page