from alpha_vantage.timeseries import TimeSeries
import sqlite3

"""
Creates a Quantly Stock class to be used as a handle for more complex operations.

The Stock class has two parameters, ticker and key. Ticker is the symbol of the equity you wish to retrieve data for.
The key parameter is your AlphaVantage API key that can be received from https://www.alphavantage.co/ for free.

The Stock class features a main update method that is used to retrieve and return the data from the API. Once the update
method has run, it returns a Pandas DataFrame, converting the object to a DataFrame object. Regular Pandas methods are
available on the returned DataFrame.

Within the update method, there is a nested function called export. This will be run when export_to_db is True as
defined in the update method's parameters. This exports the data from the generated DataFrame to an SQL database of your
chosen path and/or filename. This can be used with any existing database as it will create the necessary tables, just
point the path and filename to your pre-existing database.
"""


class Stock:
    def __init__(self, ticker: str, key: str = ''):
        self.symbol = ticker.upper()
        # Ability to enter a personal AlphaVantage API key. If no key provided, default is used.
        if key == '':
            self.key = 'WTTQPLFVUWLDDLB'
        else:
            self.key = key

    # The update() method gets the information from the AlphaVantage API.
    def update(self, outputsize: str = 'compact', export_to_db: bool = False, filename: str = 'stockdb.sqlite3',
               path: str = ''):

        ts = TimeSeries(self.key, output_format='pandas')

        # outputsize = 'full' - Previous 20 years of data will be extracted
        # outputsize = 'compact' - Previous 100 open market days of data will be extracted
        data, meta_data = ts.get_daily(self.symbol, outputsize)
        data.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low',
                             '4. close': 'close', '5. volume': 'volume'}, inplace=True)

        # Exports the equity data from the AlphaVantage API's generated Pandas DataFrame to an SQLite3 database.
        def export():
            conn = sqlite3.connect(path + filename)
            cur = conn.cursor()

            cur.executescript('''
                        CREATE TABLE IF NOT EXISTS
                        stock_data (
                        stock_id INTEGER, date TEXT, open NUMBER, high NUMBER, low NUMBER, close NUMBER, volume NUMBER
                        );

                        CREATE TABLE IF NOT EXISTS stock_index (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, symbol TEXT UNIQUE
                        );
                        ''')

            cur.execute('INSERT OR IGNORE INTO stock_index (symbol) VALUES ( ? )', (self.symbol,))
            cur.execute('SELECT id FROM stock_index WHERE symbol = ?', (self.symbol,))
            stock_id = cur.fetchone()[0]

            data.insert(loc=0, column='stock_id', value=stock_id)
            data.to_sql('stock_data', conn, if_exists='append', index=True, index_label='date')

            cur.execute('''DELETE FROM stock_data
                            WHERE ROWID not in(
                                SELECT min(ROWID)
                                FROM stock_data
                                GROUP BY stock_id, date
                            );''')

            conn.commit()
            cur.close()

        if export_to_db is True:
            export()
        else:
            return data
