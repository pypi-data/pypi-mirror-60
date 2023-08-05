from alpha_vantage.timeseries import TimeSeries
import sqlite3


class Stock:
    def __init__(self, ticker, key=''):
        self.symbol = ticker.upper()
        if key == '':
            self.key = 'WTTQPLFVUWLDDLB'
        else:
            self.key = key

    def update(self, outputsize='compact', export_to_db=False, filename='stockdb.sqlite3', path=''):

        ts = TimeSeries(self.key, output_format='pandas')

        data, meta_data = ts.get_daily(self.symbol, outputsize)
        data.rename(columns={'1. open': 'open', '2. high': 'high', '3. low': 'low',
                             '4. close': 'close', '5. volume': 'volume'}, inplace=True)

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
