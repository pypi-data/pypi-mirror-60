## Welcome to Quantly

Quantly is an open-source toolkit written in Python for equity traders.

Project Repo: [https://github.com/BluechipData/quantly](https://github.com/BluechipData/quantly)

Currently it consists of two-modules:
* data.py
* forecast.py

The following packages are dependencies and will be installed with Quantly:
* [pandas](https://github.com/pandas-dev/pandas)
* [alpha-vantage](https://github.com/RomelTorres/alpha_vantage)
* [pystan](https://github.com/stan-dev/pystan)
* [FBProphet](https://facebook.github.io/prophet/)

Quantly can be installed into your project's virtual environment (recommended) or your Python root install by executing the following:

'pip install quantly'

### AlphaVantage API

It is advised that you get your own FREE (as in air) AlphaVantage API key from [here](https://www.alphavantage.co/support/#api-key). Upgrade options are available for additional features should you wish.

### The Data Module

Quantly's data module contains powerful tools leveraging the AlphaVantage API with the ability to export equity data from either the past 100 open-market days or the past 20 years of an equity's history. This data can be exported to an SQL database with parameters to customize the path and filename. This can also be integrated into a Django SQLite3 database by simply pointing the output method to the database.

### The Forecasting Module

Quantly's forecast module is a collection of functions using the [FBProphet](https://facebook.github.io/prophet/) package to provide time-series analysis of data provided already collected from an external source or from Quantly's data module. Currently, only linear deterministic models are supported.

