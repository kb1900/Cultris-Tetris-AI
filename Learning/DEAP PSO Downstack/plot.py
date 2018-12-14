import matplotlib.pyplot as plt

import numpy as np
import pandas as pd

from sklearn import linear_model


class Regression():

	def linear_regression(x, y,ind):
		lm = linear_model.LinearRegression()
		model = lm.fit(np.array(x).reshape(-1, 1),np.array(y).reshape(-1, 1))
		
		slope = lm.coef_
		intercept = lm.intercept_
		prediction = slope*ind + intercept

		regression = [lm.coef_,lm.intercept_,lm.score(np.array(x).reshape(-1, 1),np.array(y).reshape(-1, 1)), prediction]

		return regression

	def plot(x,y, y1):
		plt.plot(x, y, 'o-')
		plt.plot(x, y1, 'x-')
		plt.xticks(range(min(x), max(x)+1))
		plt.title('GA Progress Over Generations')
		plt.ylabel('Game Score')
		plt.xlabel('Epoch')

		plt.savefig('Graph')


