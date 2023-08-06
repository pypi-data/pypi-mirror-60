import pandas as pd
import sqlite3
from fbprophet import Prophet
import matplotlib.pyplot as plt

"""
The Quantly Forecast module adds a collection of functions for forecasting equity data.

The data can be imported from an SQLite3 database, CSV file or a Pandas DataFrame.
This can be combined with the Quantly Data module for easy workflow.
Forecast data can be exported using regular DataFrame export methods.

'All models are wrong, some are just more wrong than others.' - Brandon Boisvert
"""


def from_database(path: str, query: vars, date_column: str, data_column: str,
                  d_seasonality: bool = True, y_seasonality: bool = True,
                  forecast_periods: int = 365, chart: bool = True):

    conn = sqlite3.connect(path)

    df = pd.read_sql_query(query, conn)
    df = df.loc([date_column, data_column])
    df.rename(columns={date_column: 'ds', data_column: 'y'}, inplace=True)

    m = Prophet(daily_seasonality=d_seasonality, yearly_seasonality=y_seasonality)
    m.fit(df)

    future = m.make_future_dataframe(periods=forecast_periods)

    forecast = m.predict(future)

    if chart is True:
        m.plot(forecast)
        plt.show()
        return forecast
    else:
        return forecast


def from_dataframe(dataframe: vars, data_column: str, date_as_index: bool, date_column: str = '',
                   d_seasonality: bool = True, y_seasonality: bool = True, forecast_periods: int = 365,
                   chart: bool = True):

    if date_as_index is True:
        dataframe['ds'] = dataframe.index
        df = dataframe[['ds', data_column]]
    else:
        df = dataframe[[date_column, data_column]]
    df.rename(columns={date_column: 'ds', data_column: 'y'}, inplace=True)

    m = Prophet(daily_seasonality=d_seasonality, yearly_seasonality=y_seasonality)
    m.fit(df)

    future = m.make_future_dataframe(periods=forecast_periods)

    forecast = m.predict(future)

    if chart is True:
        m.plot(forecast)
        plt.show()
        return forecast
    else:
        return forecast


def from_csv(path: str, date_column: str, data_column: str, sep: str = ',', d_seasonality: bool = True,
             y_seasonality: bool = True, forecast_periods: int = 365, chart: bool = True):

    df = pd.read_csv(path, sep)
    df.rename(columns={date_column: 'ds', data_column: 'y'}, inplace=True)

    m = Prophet(daily_seasonality=d_seasonality, yearly_seasonality=y_seasonality)
    m.fit(df)

    future = m.make_future_dataframe(periods=forecast_periods)

    forecast = m.predict(future)

    if chart is True:
        m.plot(forecast)
        plt.show()
        return forecast
    else:
        return forecast
