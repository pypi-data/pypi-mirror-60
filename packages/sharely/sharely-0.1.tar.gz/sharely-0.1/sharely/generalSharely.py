from yahoofinancials import YahooFinancials as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go


class Sharely:

    def __init__(self, share_ticker, start_date, end_date):
        """
        :param share_ticker: ticker of the interested share on the market
        """
        self.ticker = share_ticker
        self.ticker_yf_obj = yf(share_ticker)
        self.data = pd.DataFrame()

        self.start_date = start_date
        self.end_date = end_date

        """
        List of annual financial statements available as df
        """
        self.balance_sheet = self.get_financial_statements("balance")
        self.income_stmt = self.get_financial_statements("income")
        self.cashflow_stmt = self.get_financial_statements("cash")


    def data_info(self, frequency):
        """
        :param start_date: date of first price
        :param end_date: date of end range
        :param frequency: frequency of price
        :return: returns the data requested in a dataframe format
        """
        json_data = self.ticker_yf_obj.get_historical_price_data(self.start_date, self.end_date, frequency)
        df = pd.DataFrame(json_data[self.ticker]['prices']).set_index('formatted_date')

        self.data = df

        return self.data

    def plot_series(self):
        """
        :return: plot the stock prices as a time series graph, with indicators of max and min prices within the time frame
        """
        price_date = self.data.index.tolist()
        price_close = self.data['adjclose']

        fig = go.Figure([go.Scatter(x=price_date, y=price_close, name="Prices"),
                         go.Scatter(x=price_date, y=np.ones(len(price_date)) * min(price_close), name="Min Price",
                                    line=dict(color="red", dash='dash')),
                         go.Scatter(x=price_date, y=np.ones(len(price_date)) * max(price_close), name="Max Price",
                                    line=dict(color="green", dash='dash'))])

        fig.update_layout(
            title={
                'text': self.ticker + " " + "Prices"
            },
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="#7f7f7f"
            )
        )

        fig.show()

    def candlestick(self):
        """

        :return: Plots a daily spread of the ticker price to better understand its volatility
        """
        fig = go.Figure(data=[go.Candlestick(x=self.data.index,
                                             open=self.data['open'],
                                             high=self.data['high'],
                                             low=self.data['low'],
                                             close=self.data['close'])])

        fig.update_layout(
            title={
                'text': self.ticker,
                'y': 0.9,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            font=dict(
                family="Courier New, monospace",
                size=12,
                color="#7f7f7f"
            )
        )

        fig.show()

    def get_financial_statements(self, type):
        stmt = self.ticker_yf_obj.get_financial_stmts('annual', type)
        data_lst = []
        if type == "balance":
            json_stmt_lst = stmt['balanceSheetHistory'][self.ticker]
        elif type == "cash":
            json_stmt_lst = stmt['cashflowStatementHistory'][self.ticker]

        elif type == "income":
            json_stmt_lst = stmt['incomeStatementHistory'][self.ticker]

        for i in range(len(json_stmt_lst)):
            data_lst.append(pd.DataFrame(json_stmt_lst[i]).T)

        return pd.concat(data_lst,sort=False)