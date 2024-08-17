import pandas as pd
import numpy as np
import yfinance as yf
import talib
import backtrader as bt

# Step 1: Fetch NASDAQ stock data
ticker = 'AAPL'  # Example ticker
data = yf.download(ticker, start="2020-01-01", end="2023-01-01")

# Step 2: Calculate Indicators
data['SMA_50'] = talib.SMA(data['Close'], timeperiod=50)
data['SMA_200'] = talib.SMA(data['Close'], timeperiod=200)
data['RSI'] = talib.RSI(data['Close'], timeperiod=14)

# Step 3: Define the NAND Alpha Logic
data['Signal_A'] = np.where(data['SMA_50'] > data['SMA_200'], 1, 0)
data['Signal_B'] = np.where(data['RSI'] < 30, 1, 0)

# NAND Logic: Only one of the signals must be true for the alpha to trigger
data['Alpha_Signal'] = np.where((data['Signal_A'] ^ data['Signal_B']) == 1, 1, 0)

# Step 4: Backtest the Strategy with Backtrader
class NANDAlpha(bt.Strategy):
    def __init__(self):
        self.sma50 = bt.indicators.SimpleMovingAverage(self.data.close, period=50)
        self.sma200 = bt.indicators.SimpleMovingAverage(self.data.close, period=200)
        self.rsi = bt.indicators.RSI(self.data.close, period=14)

    def next(self):
        if (self.sma50 > self.sma200 and self.rsi > 30) or (self.sma50 < self.sma200 and self.rsi < 30):
            if not self.position:
                self.buy()
        elif self.position:
            self.sell()

# Step 5: Run the Backtest
cerebro = bt.Cerebro()
cerebro.addstrategy(NANDAlpha)
data_bt = bt.feeds.PandasData(dataname=data)
cerebro.adddata(data_bt)
cerebro.broker.setcash(100000.0)
cerebro.run()

# Step 6: Plot the Results
cerebro.plot()
