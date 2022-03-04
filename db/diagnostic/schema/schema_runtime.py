from ../..assets.model_asset_failure import AssetFailure
from model_runtime import Runtime
from ..schema.schema_sensors import SensorsSchema
from ../..schema import ma
from marshmallow_sqlalchemy.fields import Nested
from marshmallow import fields

class RuntimeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Runtime
        include_fk=True
        exclude = ("actual_smoothed", "residual_smoothed")
    priority = fields.Function(lambda obj: obj.priority if hasattr(obj,'priority') else None, dump_only=True)
    # priority = fields.Int(dump_only=True)
    # priority = fields.Method("get_prio")
    flag = fields.Function(lambda obj: 1 if hasattr(obj,'priority') else 0, dump_only=True)

    # def get_prio(self,obj):
    #     print(hasattr(obj,'priority'))

runtime_schema = RuntimeSchema(many=True)