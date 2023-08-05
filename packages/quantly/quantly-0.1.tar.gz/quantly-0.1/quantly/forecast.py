import pandas as pd
import sqlite3
from fbprophet import Prophet
import matplotlib.pyplot as plt


def from_database(path: str, table_name: str, selection: str, date_column: str, data_column: str,
                  direction: str = 'ascending', limit: int = 0, d_seasonality: bool = True, y_seasonality: bool = True,
                  forecast_periods: int = 365, chart: bool = True):

    conn = sqlite3.connect(path)

    if direction == 'ascending':
        direction = ' ASC '
    else:
        direction = ' DSC '

    if limit == 0:
        query = 'SELECT ' + selection + ' FROM ' + table_name + direction
    else:
        query = 'SELECT ' + selection + ' FROM ' + table_name + direction + ' LIMIT ' + str(limit)

    df = pd.read_sql_query(query, conn)
    df = df[[date_column, data_column]]
    df.rename(columns={date_column: 'ds', data_column: 'y'}, inplace=True)

    m = Prophet(daily_seasonality=d_seasonality, yearly_seasonality=y_seasonality)
    m.fit(df)

    future = m.make_future_dataframe(periods=forecast_periods)

    forecast = m.predict(future)

    if chart is True:
        fig1 = m.plot(forecast)
        plt.show(fig1)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    else:
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


def from_dataframe(dataframe: vars, date_column: str, data_column: str, d_seasonality: bool = True,
                   y_seasonality: bool = True, forecast_periods: int = 365, chart: bool = True):

    df = dataframe[[date_column, data_column]]
    df.rename(columns={date_column: 'ds', data_column: 'y'}, inplace=True)

    m = Prophet(daily_seasonality=d_seasonality, yearly_seasonality=y_seasonality)
    m.fit(df)

    future = m.make_future_dataframe(periods=forecast_periods)

    forecast = m.predict(future)

    if chart is True:
        fig1 = m.plot(forecast)
        plt.show(fig1)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    else:
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]


def from_csv(path: str, date_column: str, data_column: str, sep: str = ',', d_seasonality: bool = True,
             y_seasonality: bool = True, forecast_periods: int = 365, chart: bool = True):

    df = pd.read_csv(path, sep)
    df.rename(columns={date_column: 'ds', data_column: 'y'}, inplace=True)

    m = Prophet(daily_seasonality=d_seasonality, yearly_seasonality=y_seasonality)
    m.fit(df)

    future = m.make_future_dataframe(periods=forecast_periods)

    forecast = m.predict(future)

    if chart is True:
        fig1 = m.plot(forecast)
        plt.show(fig1)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    else:
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
