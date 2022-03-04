from ..models.model_sensor import Sensors
from ../..schema import ma

class SensorsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Sensors
        include_fk = True

sensors_schema = SensorsSchema(many=True)
sensor_schema = SensorsSchema()