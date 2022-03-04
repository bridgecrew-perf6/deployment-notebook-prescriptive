import pandas as pd
import numpy as np
import time
from datetime import timedelta, date, datetime

class TransformData(object):
    def __init__(self):
        pass

    # get data and preprocessing
    def format_timestamp(self, utc_datetime):
        now_timestamp = time.time()
        offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
        return utc_datetime + offset

    def reduce_columns(self, df, sensor):
        idx_cols_selected = [i for i in range(df.shape[1]) if i==0 or i%6==0]
        idx_col_timestamp = [1]
        idx = idx_col_timestamp + idx_cols_selected

        df = df[df.columns[idx]]
        df.columns = ['date'] + sensor

        # format col timestamp
        result = df.copy()
        result['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d %H:%M:%S')
        result['date'] = pd.to_datetime(result['date']).apply(self.format_timestamp)
        return result.iloc[0]

    def transform(self, data):
        date = data['date'].strftime("%Y-%m-%d %H:%M:%S")
        sensors =  data.index.tolist()[1:]
        actuals = []
        for d in data.tolist()[1:]:
            if type(d) == int or type(d) == float:
                actuals.append(np.around(d, 6))
            else:
                actuals.append(np.nan)
        return {'date': date, 'sensors': sensors, 'actuals':actuals}