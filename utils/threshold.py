from db.diagnostic.models.model_sensor import Sensors
from db.diagnostic.models.model_model_tag import ModelTag
from db.base import session

def get_actual_low(sensor_names):
    values = session.query(Sensors.actual_low).filter(Sensors.name.in_(sensor_names)).all()
    return [v[0] for v in values]

def get_actual_high(sensor_names):
    values = session.query(Sensors.actual_high).filter(Sensors.name.in_(sensor_names)).all()
    return [v[0] for v in values]

def get_sensor_id(sensor_names):
    values = session.query(Sensors.id).filter(Sensors.name.in_(sensor_names)).all()
    return [v[0] for v in values]

def get_residual_positive_threshold(sensor_id):
    values = session.query(ModelTag.residual_positive_threshold).filter(ModelTag.sensor.in_(sensor_id)).all()
    return [v[0] for v in values]

def get_residual_negative_threshold(sensor_id):
    values = session.query(ModelTag.residual_negative_threshold).filter(ModelTag.sensor.in_(sensor_id)).all()
    return [v[0] for v in values]