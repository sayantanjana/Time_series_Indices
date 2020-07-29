# -*- coding: utf-8 -*-
"""ML_NIFTY_2020.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/172dEIozcMINdYlGsafrYXWkSGXIgwXxv

# Import Libraries
"""

pip install pyramid-arima

# pip install git+git://github.com/bashtage/arch.git

import os
import warnings
warnings.filterwarnings('ignore')
import numpy as np
import pandas as pd
import scipy
import scipy.stats
import pylab
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from matplotlib import rcParams
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import math
from math import sqrt
import statsmodels.graphics.tsaplots as sgt
import statsmodels.tsa.stattools as sts
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from fbprophet import Prophet
from pyramid.arima import auto_arima
from datetime import datetime as dt
from datetime import timedelta
from matplotlib.ticker import NullFormatter
from matplotlib.dates import MonthLocator, DateFormatter
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
# from arch import arch_model
plt.style.use('fivethirtyeight')
sns.set_style('darkgrid')

"""# Import Dataset"""

url = 'https://raw.githubusercontent.com/sj-leshrac/Stock_Market_Data/master/SENSEX2020.csv'
df = pd.read_csv(url)

# Set Date as Index
df['Date'] = pd.to_datetime(df.Date)
df.set_index("Date", inplace = True)

"""# Descriptives & Visualizations"""

# Line plot
rcParams['figure.figsize'] = 18,6
plt.xlabel("Time",fontsize=12)
plt.ylabel("Close Prices", fontsize=12)
plt.suptitle("NIFTY50 Close Prices", fontsize=16, color='darkcyan')
plt.xticks(rotation=45)
ax = sns.lineplot(data=df["Close"], color="coral")
ax.tick_params(direction='out')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

#ax.get_legend().remove()
#ax.xaxis.set_major_locator(MonthLocator())
#ax.xaxis.set_major_formatter(DateFormatter('%b'))

# Scatter Plot
fig, ax = plt.subplots()
ax.scatter(x=df.index.values, y=df['Close'])
plt.xticks(rotation=45)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
plt.show()

scipy.stats.probplot(df.Close, plot = pylab)
plt.title("QQ Plot", size = 24)
pylab.show()

"""## Test For stationarity"""

#Test for staionarity
def test_stationarity(timeseries):
    #Determing rolling statistics
    rolmean = timeseries.rolling(12).mean()
    rolstd = timeseries.rolling(12).std()
    #Plot rolling statistics:
    plt.plot(timeseries, color='blue',label='Original')
    plt.plot(rolmean, color='red', label='Rolling Mean')
    plt.plot(rolstd, color='black', label = 'Rolling Std')
    plt.legend(loc='best')
    plt.title('Rolling Mean and Standard Deviation')
    plt.show(block=False)
    
    print("Results of dickey fuller test")
    adft = adfuller(timeseries,autolag='AIC')
    # output for dft will give us without defining what the values are.
    #hence we manually write what values does it explains using a for loop
    output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
    for key,values in adft[4].items():
        output['critical value (%s)'%key] =  values
    print(output)
    
test_stationarity(df['Close'])

"""## Seperate trend and seasonality"""

# Multiplicative Seasonality
mult_seasonality = seasonal_decompose(df["Close"], model='multiplicative', freq = 30)
fig = plt.figure()  
fig = mult_seasonality.plot() 
fig.set_size_inches(16, 9)

#Additive Seasonality
add_seasonality = seasonal_decompose(df["Close"], model='additive', freq = 30)
fig = plt.figure()  
fig = mult_seasonality.plot()  
fig.set_size_inches(16, 9)

"""## Moving Average"""

from pylab import rcParams
rcParams['figure.figsize'] = 10, 6
df_close=df["Close"]
df_log = np.log(df_close)
moving_avg = df_log.rolling(12).mean()
std_dev = df_log.rolling(12).std()
plt.legend(loc='best')
plt.title('Moving Average')
plt.plot(std_dev, color ="black", label = "Standard Deviation")
plt.plot(moving_avg, color="red", label = "Mean")
plt.xticks(rotation=30)
plt.show()

"""# Train Test split of data"""

size = int(len(df)*0.8)
df_train1, df_test1 = df.iloc[:size], df.iloc[size:]
df_train=df_train1.Close
df_train=df_train.to_frame()
df_test=df_test1.Close
df_test=df_test.to_frame()

rcParams['figure.figsize'] = 14,6
plt.xlabel("Time",fontsize=12)
plt.ylabel("Close Prices", fontsize=12)
plt.suptitle("Train-Test Split", fontsize=16, color='darkcyan')
plt.xticks(rotation=45)
ax = sns.lineplot(data=df_train["Close"], color="green", label='Train Data(80%)')
ax = sns.lineplot(data=df_test["Close"], color="blue", label='Test data(20%)')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))

"""# ARIMA"""

# Determine the orders of ARIMA Model

model_autoARIMA = auto_arima(df_train, start_p=0, start_q=0,
                      test='adf',       # use adftest to find             optimal 'd'
                      max_p=5, max_q=5, # maximum p and q
                      m=5,              # frequency of series
                      d=None,           # let model determine 'd'
                      seasonal=False,   # No Seasonality
                      start_P=0, 
                      D=0, 
                      trace=True,
                      error_action='ignore',  
                      suppress_warnings=True, 
                      stepwise=True)
print(model_autoARIMA.summary())

# Custom settings for AutoARIMA
model_ar1 = ARIMA(df_train, order = (1,0,0))
results_ar = model_ar1.fit()
print(results_ar.summary())

# Make predictions
fc_ar= results_ar.forecast(steps=len(df_test))[0]
fc_ar = pd.DataFrame(fc_ar, index=df_test.index, columns=['prediction'])

"""### Model Performance"""

# Model Stats
from sklearn.metrics import mean_squared_error
MSE=mean_squared_error(df_test,fc_ar)
print("MSE for ARIMA = {}".format(MSE))
mae = mean_absolute_error(df_test, fc_ar)
print('MAE: '+str(mae))
rms_arima = sqrt(mean_squared_error(df_test, fc_ar))
print("RMSE for ARIMA = {}".format(rms_arima))

"""# Auto ARIMA"""

model_ar = auto_arima(df_train, trace=True, error_action='ignore', suppress_warnings=True)
model_ar.fit(df_train)
print(model_ar.summary())

# make predictions
fc_autoar = model_ar.predict(n_periods=len(df_test))
fc_autoar = pd.DataFrame(fc_autoar ,index = df_test.index, columns=['prediction'])

"""### Model Performance"""

#Model stats
from sklearn.metrics import mean_squared_error
MSE1=mean_squared_error(df_test,fc_autoar)
print("MSE for Auto ARIMA = {}".format(MSE1))
mae = mean_absolute_error(df_test, fc_autoar)
print('MAE: '+str(mae))
rms_autoarima = sqrt(mean_squared_error(df_test, fc_autoar))
print("RMSE for Auto ARIMA = {}".format(rms_autoarima))

"""# Forecast Visualization"""

# ARIMA
rcParams['figure.figsize'] = 20,5
plt.xlabel("Time",fontsize=12)
plt.ylabel("Close Prices", fontsize=12)
plt.suptitle("ARIMA", fontsize=24, color='darkcyan')
plt.xticks(rotation=30)
ax = sns.lineplot(data=fc_ar["prediction"], color="black", label='Predicted')
ax = sns.lineplot(data=df_test["Close"], color="green", label='Test data')
#ax = sns.lineplot(data=df_train["Close"], color="teal", label='Train data')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

# AUTO ARIMA
rcParams['figure.figsize'] = 20,5
plt.xlabel("Time",fontsize=12)
plt.ylabel("Close Prices", fontsize=12)
plt.suptitle("Auto ARIMA", fontsize=24, color='darkcyan')
plt.xticks(rotation=30)
ax = sns.lineplot(data=fc_autoar["prediction"], color="black", label='Predicted')
ax = sns.lineplot(data=df_test["Close"], color="green", label='Test data')
#ax = sns.lineplot(data=df_train["Close"], color="teal", label='Train data')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

# ARIMA vs AutoARIMA
rcParams['figure.figsize'] = 20,5
plt.xlabel("Time",fontsize=12)
plt.ylabel("Close Prices", fontsize=12)
plt.suptitle("ARIMA Vs Auto ARIMA", fontsize=24, color='darkcyan')
plt.xticks(rotation=30)
ax = sns.lineplot(data=fc_ar["prediction"], color="red", label='Forecast (ARIMA)',linewidth=3.0)
ax = sns.lineplot(data=fc_autoar["prediction"], color="green", label='Forecast (Auto ARIMA)', linewidth=3.0)
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

"""### With confidence interval"""

# Forecast ARIMA
fc, se, conf = results_ar.forecast(len(df_test), alpha=0.05)  # 95% confidence
fc_series = pd.Series(fc, index=df_test.index)
lower_series = pd.Series(conf[:, 0], index=df_test.index)
upper_series = pd.Series(conf[:, 1], index=df_test.index)
plt.figure(figsize=(16,5), dpi=100)
plt.plot(df_train, label='Train data', color= 'green')
plt.plot(df_test, color = 'blue', label='Test data')
plt.plot(fc_ar, color = 'orange',label='Predicted')
plt.fill_between(lower_series.index, lower_series, upper_series, color='k', alpha=.10)
plt.title('ARIMA with confidence interval')
plt.xlabel('Time')
plt.ylabel('Close Prices')
plt.legend(loc='upper right', fontsize=8)
plt.xticks(rotation=30)
plt.show()

# Forecast Auto ARIMA
fc, se, conf = results_ar.forecast(len(df_test), alpha=0.05)  # 95% confidence
fc_series = pd.Series(fc, index=df_test.index)
lower_series = pd.Series(conf[:, 0], index=df_test.index)
upper_series = pd.Series(conf[:, 1], index=df_test.index)
plt.figure(figsize=(16,5), dpi=100)
plt.plot(df_train, label='Train data', color= 'green')
plt.plot(df_test, color = 'blue', label='Test data')
plt.plot(fc_autoar, color = 'orange',label='Predicted')
plt.fill_between(lower_series.index, lower_series, upper_series, color='k', alpha=.10)
plt.title('Auto ARIMA with confidence interval')
plt.xlabel('Date')
plt.ylabel('Close Prices')
plt.legend(loc='upper right', fontsize=8)
plt.xticks(rotation=30)
plt.show()

"""# LSTM"""

training_set=df_train[:]
testing_set=df_test[:]

from sklearn.preprocessing import MinMaxScaler
sc = MinMaxScaler(feature_range = (0, 1))
training_set_scaled = sc.fit_transform(training_set)

X_train = []
y_train = []
for i in range(1, len(training_set)):
    X_train.append(training_set_scaled[i-1:i, 0])
    y_train.append(training_set_scaled[i, 0])
X_train, y_train = np.array(X_train), np.array(y_train)

X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

len(X_train)

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import Dropout

from tensorflow.python.framework import ops
ops.reset_default_graph()

regressor = Sequential()

regressor.add(LSTM(units = 50, return_sequences = True, input_shape = (X_train.shape[1], 1)))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 50, return_sequences = True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units = 50))
regressor.add(Dropout(0.2))

regressor.add(Dense(units = 1))

regressor.compile(optimizer = 'adam', loss = 'mean_squared_error')

regressor.fit(X_train, y_train, epochs = 100, batch_size = 32)

dataset_total = pd.concat((training_set['Close'], testing_set['Close']), axis = 0)
inputs = dataset_total[len(dataset_total) - len(testing_set) :].values
inputs = inputs.reshape(-1,1)
inputs = sc.transform(inputs)
X_test = []
for i in range(1, len(testing_set)):
    X_test.append(inputs[i-1:i, 0])
X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
predicted_stock_price = regressor.predict(X_test)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

testing_set1=testing_set[1:len(testing_set)]
fc_LSTM = pd.DataFrame(predicted_stock_price ,index = testing_set1.index, columns=['prediction'])

# LSTM
rcParams['figure.figsize'] = 15,6
plt.xlabel("Time",fontsize=15)
plt.ylabel("Close Prices", fontsize=15)
plt.suptitle("LSTM", fontsize=24, color='darkcyan')
plt.xticks(rotation=30)
ax = sns.lineplot(data=fc_LSTM["prediction"], color="green", label='Predicted')
ax = sns.lineplot(data=testing_set1["Close"], color="black", label='Test data')
#ax = sns.lineplot(data=training_set["Close"], color="teal", label='Train data')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

rms_LSTM = (np.sqrt(mean_squared_error(testing_set1, predicted_stock_price)))
test_set_r2 = r2_score(testing_set1, predicted_stock_price)
print("RMSE {}".format(rms_LSTM))
print("R2 Score {}".format(test_set_r2))

"""# Prophet

### Additive Seasonality
"""

train=df_train[:]
test=df_test[:]
train["ds"] = df_train.index
train[ "y"] = df_train.Close

# fit the model
model = Prophet(seasonality_mode="additive", daily_seasonality=True)
model.fit(train)

# Predict
future = model.make_future_dataframe(periods=len(test),freq='D')
forecast = model.predict(future)

# get the forecast values
forecast_valid = forecast["yhat"][len(train):]

# insert prediction values into validation set
test.insert(loc=1, column="prediction", value=forecast_valid.values)

# calculate rmse
rms_prophet_as = sqrt(mean_squared_error(test["Close"], forecast_valid))
print("RMSE for Prophet = {}".format(rms_prophet_as))

# Prophet Additive
rcParams['figure.figsize'] = 15,6
plt.xlabel("Time",fontsize=15)
plt.ylabel("Close Prices", fontsize=15)
plt.suptitle("Prophet (Additive Seasonality)", fontsize=24, color='darkcyan')
plt.xticks(rotation=30)
ax = sns.lineplot(data=test["prediction"], color="green", label='Predicted')
ax = sns.lineplot(data=testing_set["Close"], color="black", label='Test data')
#ax = sns.lineplot(data=train["y"], color="teal", label='Train data')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

# plot the components
fig_components = model.plot_components(forecast)
fig_components.text(0.5, 0.99, "Prophet (Additive Seasonality)", ha="center", fontsize=14)

"""### Multiplicative Seasonality"""

train1=df_train[:]
test1=df_test[:]
train1["ds"] = df_train.index
train1[ "y"] = df_train.Close

# fit the model
model1 = Prophet(seasonality_mode="multiplicative", daily_seasonality=True)
model1.fit(train1)

# make predictions
future1 = model1.make_future_dataframe(periods=len(test1), freq="D")
forecast1 = model1.predict(future1)

# get the forecast values
forecast_valid1 = forecast1["yhat"][len(train1):]

# insert prediction values into validation set
test1.insert(loc=1, column="prediction", value=forecast_valid1.values)

# calculate rmse
rms_prophet_ms = sqrt(mean_squared_error(test1["Close"], forecast_valid1))
print("RMSE for Prophet = {}".format(rms_prophet_ms))

# Prophet Multiplicative
rcParams['figure.figsize'] = 15,6
plt.xlabel("Time",fontsize=15)
plt.ylabel("Close Prices", fontsize=15)
plt.suptitle("Prophet (Multiplicative Seasonality)", fontsize=24, color='darkcyan')
plt.xticks(rotation=30)
ax = sns.lineplot(data=test1["prediction"], color="green", label='Predicted')
ax = sns.lineplot(data=test1["Close"], color="black", label='Test data')
#ax = sns.lineplot(data=train["y"], color="teal", label='Train data')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

# plot the components
fig_components = model1.plot_components(forecast1)
fig_components.text(0.5, 0.99, "Prophet (Multiplicative Seasonality)", ha="center", fontsize=14)

"""# RMSE Comparison"""

# combine all models' results into one dataframe
data = {"Model": ["ARIMA", "Auto ARIMA", "LSTM", "Prophet (Additive Seasonality)", "Prophet (Multiplicative Seasonality)"], 
        "RMSE": [rms_arima, rms_autoarima, rms_LSTM, rms_prophet_as, rms_prophet_ms]}

results = pd.DataFrame(data=data)
sns.set_style('white')
ax = sns.barplot(x="Model", y="RMSE", data=results)
for p in ax.patches:
    height = p.get_height()
    ax.text(p.get_x()+p.get_width()/2., height+1, "{:1.2f}".format(height), ha="center", fontsize=14) 
plt.title('RMSE Comparison', size=20)
plt.xlabel('Model', size=15)
plt.ylabel('RMSE Values', size=15)
plt.xticks(rotation=5)
plt.show(fig)

# Prediction Comparison
rcParams['figure.figsize'] = 18,8
plt.xlabel("Time",fontsize=12)
plt.ylabel("Close Prices", fontsize=12)
plt.suptitle("Comparison of Model Predictions", size = 24, color="Purple")
plt.xticks(rotation=30)
ax = sns.lineplot(data=df_test["Close"], color="blue", label='Test data', linewidth=3.0)
ax = sns.lineplot(data=fc_ar["prediction"], color="red", label='ARIMA', linewidth=1.5)
ax = sns.lineplot(data=fc_autoar["prediction"], color="lawngreen", label='Auto ARIMA', linewidth=1.5)
ax = sns.lineplot(data=fc_LSTM["prediction"], color="green", label='LSTM',  linewidth=1.5)
ax = sns.lineplot(test.index, test["prediction"], label="Prophet Additive", color= "Black",  linewidth=1.5)
ax = sns.lineplot(test1.index, test1["prediction"], label="Prophet Multiplication", color= "teal",  linewidth=1.5)
#ax = sns.lineplot(data=df_train["Close"], color="dodgerblue", label='Train Data')
ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))

!jupyter nbconvert --to html ARIMA_NIFTY20.ipynb

