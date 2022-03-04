import os
from datetime import timedelta, datetime
import numpy as np


class Model(object):
	def __init__(self, date):
		self.date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
		self.filepath = os.path.join(os.path.abspath(os.getcwd()), 'state-matrix', self.define_filepath())
	
	def define_filepath(self):
		first_day_of_the_week =  self.date - timedelta(days=self.date.weekday() % 7)
		year = first_day_of_the_week.year
		month = first_day_of_the_week.month
		day = first_day_of_the_week.day
		filepath = f"{year}/{month}/{day}.npy"
		return filepath
	
	def load_state_matrix(self):
		if os.path.exists(self.filepath):
			return np.load(self.filepath)
		else:
			# create new directory for model
			path = '/'.join(self.filepath.split('/')[:-1])
			os.makedirs(path, exist_ok=True)
			
			# get last model instead
			first_day_of_the_week =  self.date - timedelta(days=self.date.weekday() % 7)
			last_week = first_day_of_the_week - timedelta(days=7)
			filepath = f"{last_week.year}/{last_week.month}/{last_week.day}.npy"
			path = os.path.join(os.path.abspath(os.getcwd()), 'state-matrix', filepath)
			return np.load(path)
	
	def update_state_matrix(self, state_matrix):
		np.save(self.filepath, state_matrix)
