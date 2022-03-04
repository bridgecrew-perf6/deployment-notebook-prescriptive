from db.diagnostic.models.model_runtime import Runtime
from db.base import session


def insert_to_table_runtime(values):
    object_list = []
    for value in values:
        v = Runtime(
            timestamp=value[0],
            sensor=value[1],
            fault=value[2],
            actual=value[3],
            actual_smoothed=value[4],
            estimate=value[5],
            residual=value[6],
            residual_smoothed=value[7],
            residual_indication_positive=value[8],
            residual_indication_negative=value[9]
        )
        object_list.append(v)
    session.add_all(object_list)
    session.commit()