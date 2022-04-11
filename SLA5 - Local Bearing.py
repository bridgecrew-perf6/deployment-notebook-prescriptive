from estimate.vbm import VBM
from residual.residual import Residual
from utils.pihelper import PIHelper
from utils.transform import TransformData
from utils.model import Model
from utils.db import insert_to_table_runtime
from utils.threshold import get_actual_low, get_actual_high, get_sensor_id
from utils.threshold import get_residual_positive_threshold, get_residual_negative_threshold

from db.base import session
from db.diagnostic.models.model_fault import Fault
from db.assets.models.model_assets import Assets
from db.assets.models.model_asset_failure import AssetFailure
from db.diagnostic.models.model_model_tag import ModelTag
from db.diagnostic.models.model_priority import Priority
from db.diagnostic.models.model_diagnose_date import DiagnoseDate

from osisoft.pidevclub.piwebapi.models import PIAnalysis, PIItemsStreamValues, PIStreamValues, PITimedValue, PIRequest

import pandas as pd
import time
import asyncio
from datetime import timedelta, date, datetime


# extract and transform data
def etl(sensor, start_time, end_time, interval):
    paths = [parent+sensor[i] for i in range(len(sensor))]
    
    # extract
    data = client.data.get_multiple_interpolated_values(paths, start_time=start_time, end_time=end_time, interval=interval)
    # transform
    transformer = TransformData()
    data = transformer.reduce_columns(data, sensor)
    data = transformer.transform(data)
    return data

def upload_recommendation(batch_data, points):
    # point1 -> recommedation
    # point2 -> priority
    # point3 -> fault
    point1, point2, point3 = points[0], points[1], points[2]
    streamValue1, streamValue2, streamValue3 = PIStreamValues(), PIStreamValues(), PIStreamValues()
    values1, values2, values3 = list(), list(), list()
    value1, value2, value3 = PITimedValue(), PITimedValue(), PITimedValue()
    
    for data in batch_data:
        timestamp = data[0]
        fault = data[1]
        priority = data[2]
        recommendation = data[3]
        
        value1.value = recommendation
        value1.timestamp = timestamp
        streamValue1.web_id = point1.web_id
        values1.append(value1)

        value2.value = priority
        value2.timestamp = timestamp
        streamValue2.web_id = point2.web_id
        values2.append(value2)

        value3.value = fault
        value3.timestamp = timestamp
        streamValue3.web_id = point3.web_id
        values3.append(value3)

    streamValue1.items = values1
    streamValue2.items = values2
    streamValue3.items = values3

    streamValues = list()
    streamValues.append(streamValue1)
    streamValues.append(streamValue2)
    streamValues.append(streamValue3)

    response = client.streamSet.update_values_ad_hoc_with_http_info(streamValues, None, None)
    return response


## LOOP ##
async def execute_diagnostic_bearing(bearing, sensor, current_time, interval, points):
    
    # get threshold
    actual_low = get_actual_low(sensor)
    actual_high = get_actual_high(sensor)
    sensor_id = get_sensor_id(sensor)
    residual_positive_threshold = get_residual_positive_threshold(sensor_id)
    residual_negative_threshold = get_residual_negative_threshold(sensor_id)

    # get data
    data = etl(sensor, current_time, current_time, interval)
    
    # load model (state matrix)
    model = Model(current_time, unit, bearing, fault)
    state_matrix = model.load_state_matrix()
    
    # estimate with VBM
    vbm = VBM(actual_high, actual_low)
    estimates, state_matrix = vbm.estimate_sensors(data['actuals'], state_matrix)
    
    # update model (state matrix)
    model.update_state_matrix(state_matrix)
    
    # calculate residual
    residual_indication_positives = []
    residual_indication_negatives = []
    residuals = []
    for i in range(len(data['actuals'])):
        resid = Residual(data['actuals'][i], estimates[i], residual_positive_threshold[i], residual_negative_threshold[i])
        residuals.append(resid.residual)
        residual_indication_positives.append(resid.residual_indication_positive)
        residual_indication_negatives.append(resid.residual_indication_negative)
        
    # insert to table runtime
    ## constructing the output
    values = []
    for i in range(len(sensor)):
        val = (current_time, sensor_id[i], fault, data["actuals"][i], None, estimates[i], residuals[i], None, residual_indication_positives[i], residual_indication_negatives[i])
        values.append(val)
    # insert into table runtime
    # insert_to_table_runtime(values)
    
    # diagnostic process
    # get all diagnostic rule expression from the fault
    diag_rule = session.query(Fault).get(fault).diagnostics.all()
    # get spesific based on asset_id
    for d in diag_rule:
        if d.get_asset() == asset.id:
            diag = d
    # determine priority
    current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
    priority = diag.calculate(current_time, fault)
    # print(f'current time: {current_time} with priority = {priority}')
    if int(priority) > 0:
        # print("=== FAILURE DETECTED ===")
        fault_object = AssetFailure(date=current_time, 
                                    asset_id=asset.id,
                                    fault=diag.fault,
                                    priority=int(priority))
        # session.add(fault_object)
        # session.commit()

        recommendation = session.query(Priority.recomendation).filter_by(priority=priority, fault=fault).first()[0]
        # print(f'Recommendation: {recommendation}')
        # upload to PI: timestamp, fault, priority, rekomendasi
        data_uploaded = [(current_time - timedelta(hours=7), fault, priority, recommendation)]
        status = upload_recommendation(data_uploaded, points)
    else:
        data_uploaded = [(current_time - timedelta(hours=7), '', priority, '')]
        status = upload_recommendation(data_uploaded, points)       

    return status

async def execute_diagnostic_unit():
    current_time = DiagnoseDate._get_last_diagnose() + timedelta(minutes=1)
    current_time = current_time.strftime('%Y-%m-%d %H:%M:%S') #get last diagnose date from db
    interval = '1m'
    
    # points
    b1_point1 = client.point.get_by_path("\\\\PI1\SLA5.Turbine.Bearing 1 recommendation prescriptive prediction", None)
    b1_point2 = client.point.get_by_path("\\\\PI1\SLA5.Turbine.Bearing 1 priority prescriptive prediction", None)
    b1_point3 = client.point.get_by_path("\\\\PI1\SLA5.Turbine.Bearing 1 fault prescriptive prediction", None)
    b1_points = [b1_point1, b1_point2, b1_point3]
    
    while True:
        # cek waktu untuk update tiap menit
        now_time = datetime.now().strftime('%Y-%m-%d %H:%M:00')
        if current_time == now_time:
            time.sleep(5)
            continue
        
        b1 = await execute_diagnostic_bearing('Bearing 1', bearing1, current_time, interval, b1_points)
        b2 = await execute_diagnostic_bearing('Bearing 1', bearing1, current_time, interval, b1_points)
        
        # update diagnose_date
        # dgdate = session.query(DiagnoseDate).first()
        # dgdate.timestamp = current_time
        # session.commit()
        
        print(current_time)
        print(b1)
        print(b2)
        print()
        
        current_time = datetime.strptime(current_time, '%Y-%m-%d %H:%M:%S')
        current_time = current_time + timedelta(minutes=1)
        current_time = current_time.strftime('%Y-%m-%d %H:%M:%S')

if __name__ == "__main__":
    # connect client
    pihelper = PIHelper()
    client = pihelper.connect_client()

    # setup paths
    parent = "af:\\\\pi1\\SLA5."
    bearing1 = ['Generator Gross Capacity',
                'Turbine Lube Oil Cooler Outlet Temperature',
                'Turbine.Bearing 1 Drain Oil Temperature',
                'Turbine.Bearing 1 Metal Temperature',
                'Turbine.Bearing 1X Vibration',
                'Turbine.Bearing 1Y Vibration']
    bearing2 = ['Generator Gross Capacity',
                'Turbine Lube Oil Cooler Outlet Temperature',
                'Turbine.Bearing 2 Drain Oil Temperature',
                'Turbine.Bearing 2 Metal Temperature',
                'Turbine.Bearing 2X Vibration',
                'Turbine.Bearing 2Y Vibration']

    # initialize
    unit = 'SLA5'
    fault = 'Local Bearing'
    asset = session.query(Assets).get(2) #get asset->id=2
   
    asyncio.run(execute_diagnostic_unit())