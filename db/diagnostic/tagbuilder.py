from datetime import datetime, timedelta
from .models.model_runtime import Runtime
from .models.model_model_tag import ModelTag
from .models.model_sensor import Sensors
from db.base import session
import numpy as np


class TagBuilder():
    '''
    mengumpulkan nilai dari sensor ModelTag dan Runtime yang diperlukan dari
    dalam database untuk kemudian dimasukkan ke RuleAssignment
    Attributes
    ----------
    sensor : Sensor
        ya sensor
    date : datetime
        objek datetime
    sensor_id : int
        id sensor untuk mengambil data Runtime nya
    Methods
    -------
    """
    '''
    def __init__(self, sensor, fault, date):
        self.sensor = sensor
        self.sensor_id = sensor.id
        self.date = date
        self.fault = fault
        self.actual = []
        self.actual_high = self.get_actual_high()
        self.actual_low = self.get_actual_low()
        self.residual = []
        self.residual_indication_positive = []
        self.residual_indication_negative = []
        self.residual_positive_threshold = self.get_residual_positive_threshold()
        self.residual_negative_threshold = self.get_residual_negative_threshold()
        self.active_in_model = self.get_active_in_model()

    def Actual(self, n=1):
        start_date = self.get_start_date(n)
        # print(self.fault,self.sensor_id,start_date.isoformat(), self.date.isoformat())
        self.actual = [r.actual for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).all()]
        # self.actual = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).with_entities(Runtime.actual).all()
        # check num of data
        # print(n,len(self.actual))
        if n != len(self.actual):
            # self.actual = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).limit(n).with_entities(Runtime.actual).all()
            self.actual = [r.actual for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).limit(n).all()]

        # self.actual = np.array(list(self.actual))
        # print(self.actual)
        self.actual = np.array(self.actual)
        # print('actual', len(self.actual), self.actual)
        return self.actual

    def Residual(self, n=1):
        start_date = self.get_start_date(n)
        self.residual = [r.residual for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).all()]
        # self.residual = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).with_entities(Runtime.residual).all()
        # check num of data
        # print(n,len(self.residual))
        if n != len(self.residual):
            # self.residual = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).with_entities(Runtime.residual).limit(n).all()
            self.residual = [r.residual for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).limit(n).all()]

        # self.residual = np.array(list(self.residual))
        self.residual = np.array(self.residual)
        # print('residual', self.residual)
        return self.residual

    def ResidualIndicationPositive(self, n=1):
        start_date = self.get_start_date(n)
        self.residual_indication_positive = [r.residual_indication_positive for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).all()]
        # self.residual_indication_positive = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).with_entities(Runtime.residual_indication_positive).all()
        # check num of data
        if n != len(self.residual_indication_positive):
            # self.residual_indication_positive = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).with_entities(Runtime.residual_indication_positive).limit(n).all()
            self.residual_indication_positive = [r.residual_indication_positive for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).limit(n).all()]

        # self.residual_indication_positive = np.array(list(self.residual_indication_positive))
        self.residual_indication_positive = np.array(self.residual_indication_positive)
        return self.residual_indication_positive

    def ResidualIndicationNegative(self, n=1):
        start_date = self.get_start_date(n)
        self.residual_indication_negative = [r.residual_indication_negative for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).all()]
        # self.residual_indication_negative = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp>=start_date, Runtime.timestamp <= self.date).with_entities(Runtime.residual_indication_negative).all()
        # check num of data
        if n != len(self.residual_indication_negative):
            # self.residual_indication_negative = Runtime.query.filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).with_entities(Runtime.residual_indication_negative).limit(n).all()
            self.residual_indication_negative = [r.residual_indication_negative for r in session.query(Runtime).filter(Runtime.sensor==self.sensor_id, Runtime.fault==self.fault, Runtime.timestamp <= self.date).order_by(Runtime.timestamp.desc()).limit(n).all()]
        
        # self.residual_indication_negative = np.array(list(self.residual_indication_negative))
        self.residual_indication_negative = np.array(self.residual_indication_negative)
        return self.residual_indication_negative

    def ResidualPositiveThreshold(self):
        return self.residual_positive_threshold

    def ResidualNegativeThreshold(self):
        return self.residual_negative_threshold
    
    def ActualHigh(self):
        return self.actual_high
    
    def ActualLow(self):
        return self.actual_low
    
    def ActiveInModel(self):
        return self.active_in_model

    #private
    def get_start_date(self, n):
        return  self.date - timedelta(minutes=n-1)

    def get_residual_positive_threshold(self):
        query = session.query(ModelTag).filter_by(sensor=self.sensor_id, type="MECHANICAL").first()
        return query.residual_positive_threshold

    def get_residual_negative_threshold(self):
        return session.query(ModelTag).filter_by(sensor=self.sensor_id, type="MECHANICAL").first().residual_negative_threshold
    
    def get_actual_high(self):
        return session.query(Sensors).get(self.sensor_id).actual_high
    
    def get_actual_low(self):
        return session.query(Sensors).get(self.sensor_id).actual_low
    
    def get_active_in_model(self):
        return session.query(ModelTag).filter_by(sensor=self.sensor_id, type="MECHANICAL").first().active_in_model