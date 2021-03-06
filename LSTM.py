import math
from imp import reload

from sklearn.metrics import mean_squared_error #均方误差
from sklearn.metrics import mean_absolute_error #平方绝对误差
import keras
import numpy
import pandas as pd
import matplotlib.pyplot as plt
from pandas import read_csv
from keras.models import Sequential
from keras.layers import Dense
from keras.layers import LSTM
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
import xlsxwriter as xw
reload(keras)
def create_dataset(dataset,look_back = 16):
	dataX,dataY = [],[]
	for i in range(len(dataset) - look_back - 1):
		a = dataset[i:i+look_back,0]
		b = dataset[i+look_back,0]
		dataX.append(a)
		dataY.append(b)
	return numpy.array(dataX),numpy.array(dataY)

RF=1
RM=1

numpy.random.seed(7)
dataframe = read_csv('flowtime.csv', usecols=[0], header=None, engine='python')
dataset = dataframe.values
dataset = dataset.astype('float32')
scaler = MinMaxScaler(feature_range=(0, 1))
dataset = scaler.fit_transform(dataset)
train_size = int(len(dataset) * 0.67)
test_size = len(dataset) - train_size
train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
look_back = 7
trainX, trainY = create_dataset(train, look_back)
testX, testY = create_dataset(test, look_back)
# reshape input to be [samples, time steps, features]
trainX = numpy.reshape(trainX, (trainX.shape[0], look_back, 1))
testX = numpy.reshape(testX, (testX.shape[0], look_back, 1))
# create and fit the LSTM network
model = Sequential()
model.add(LSTM(64,  return_sequences=True, input_shape=(look_back, 1), RF=1, RM=1))
model.add(LSTM(32, input_shape=(look_back, 1), RF=RF, RM=RM))
model.add(Dense(1))
# optimizer=keras.optimizers.SGD(lr=1e-4,momentum=0.9)
optimizer = 'adam'
model.compile(loss='mean_squared_error', optimizer=optimizer)
model.fit(trainX, trainY, epochs=10, batch_size=1, verbose=1)
# make predictions
trainPredict = model.predict(trainX)
testPredict = model.predict(testX)
# invert predictions
# print(trainPredict)
trainPredict = scaler.inverse_transform(trainPredict)
trainY = scaler.inverse_transform([trainY])
testPredict = scaler.inverse_transform(testPredict)
testY = scaler.inverse_transform([testY])
# calculate root mean squared error
trainScore = math.sqrt(mean_squared_error(trainY[0], trainPredict[:, 0]))
testScore = math.sqrt(mean_squared_error(testY[0], testPredict[:, 0]))
# shift train predictions for plotting
trainPredictPlot = numpy.empty_like(dataset)
trainPredictPlot[:, :] = numpy.nan
trainPredictPlot[look_back:len(trainPredict) + look_back, :] = trainPredict
# shift test predictions for plotting
testPredictPlot = numpy.empty_like(dataset)
testPredictPlot[:, :] = numpy.nan
testPredictPlot[len(trainPredict) + (look_back * 2) + 1:len(dataset) - 1, :] = testPredict
print('WAPE:', mean_absolute_error(testY[0], testPredict[:, 0])*len(testY[0])/sum(testY[0]))
# plot baseline and predictions


