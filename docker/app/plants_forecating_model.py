import numpy as np
import pandas as pd
from pandas import read_csv
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.layers import GRU, Dense
from tensorflow import keras
from datetime import datetime, timedelta


def GetDataAndLabel(data, TimeStep):
    trainData, trainLabel = [], []
    for i in range(len(data) - TimeStep):
        TrainDataOne = data[i:(i + TimeStep), 0]
        trainData.append(TrainDataOne)
        trainLabel.append(data[i + TimeStep, 0])
    return np.array(trainData), np.array(trainLabel)


# 預測單一欄位的函數
def predict_column(data, f_date: int):
    # 讀取指定欄位的數據
    # dataItem = read_csv('./22plantsales.csv', usecols=[1], skiprows=1, engine='python')
    data = data.values
    data = data[~np.isnan(data)]
    data = data.reshape(-1, 1)
    data = data.astype('float32')
    scaler = MinMaxScaler(feature_range=(0, 1))
    data = scaler.fit_transform(data)

    TrainDataNum = int(len(data))
    # TestDataNum = len(data) - TrainDataNum

    trainData = data[0:TrainDataNum]
    # testData = data[TrainDataNum:len(data):]

    TimeStep = 120
    traindataNew, trainLabelNew = GetDataAndLabel(trainData, TimeStep)
    # testdataNew, testLabelNew = GetDataAndLabel(testData, TimeStep)

    traindataNew = np.reshape(traindataNew, (traindataNew.shape[0], traindataNew.shape[1], 1))
    # testdataNew = np.reshape(testdataNew, (testdataNew.shape[0], testdataNew.shape[1], 1))

    model = keras.Sequential()
    model.add(GRU(256, input_shape=(TimeStep, 1), return_sequences=True))
    model.add(GRU(128, input_shape=(TimeStep, 1), return_sequences=True))
    model.add(GRU(64, input_shape=(TimeStep, 1)))
    model.add(Dense(1))

    optimizer = keras.optimizers.Adam(learning_rate=0.001)
    model.compile(loss='mean_squared_error', optimizer=optimizer)

    hist = model.fit(traindataNew, trainLabelNew, epochs=50, batch_size=32, verbose=1)

    future_days = f_date
    input_data = data[-TimeStep:]
    input_data = np.reshape(input_data, (1, TimeStep, 1))

    future_predictions = []
    for i in range(future_days):
        prediction = model.predict(input_data)
        future_predictions.append(prediction[0])
        input_data = np.concatenate((input_data[:, 1:, :], prediction.reshape(1, 1, 1)), axis=1)

    future_predictions = scaler.inverse_transform(future_predictions)
    global predictions_df
    predictions_df['Column'] = np.squeeze(future_predictions)
    return predictions_df
