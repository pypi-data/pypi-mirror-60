from .generalSharely import Sharely


class Metrics(Sharely):
    """
    Metrics Class to retrieve financial ratios computed from financial statements
    """

    def __init__(self, ticker, start_date, end_date):
        Sharely.__init__(self, ticker, start_date, end_date)

    def calculate_metrics(self):
        balance_df = self.balance_sheet
        balance_df['Current Ratio'] = balance_df['totalCurrentAssets'] / balance_df['totalCurrentLiabilities']
        balance_df['Quick Ratio'] = (balance_df['totalCurrentAssets'] - balance_df['inventory']) / balance_df['totalCurrentLiabilities']
        balance_df['Current Capital'] = balance_df['totalCurrentAssets'] - balance_df['totalCurrentLiabilities']
        balance_df['Debt to Equity'] = balance_df['totalLiab'] / balance_df['totalStockholderEquity']

        summary = balance_df[['Current Ratio', 'Quick Ratio', 'Current Capital', 'Debt to Equity']]

        return summary