import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our custom modules
from backtester import backtest

def fetch_stock_data(symbol, period="2y"):
    """
    Fetch stock data using yfinance
    symbol: Stock symbol (e.g., 'RELIANCE.NS' for NSE, 'RELIANCE.BO' for BSE)
    period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
    """
    try:
        print(f"Connecting to Yahoo Finance for {symbol}...")
        
        # Download stock data
        stock = yf.Ticker(symbol)
        data = stock.history(period=period)

        # Check if data is empty
        if data.empty:
            print(f"❌ No data found for symbol: {symbol}")
            print("💡 Try these alternatives:")
            print("   - RELIANCE.NS (NSE)")
            print("   - RELIANCE.BO (BSE)")
            print("   - Check if symbol is correct")
            return None
        
        # Validate data quality
        if len(data) < 60:  # Need at least 60 days for 50-day SMA
            print(f"⚠️  Warning: Only {len(data)} days of data available.")
            print("   Strategy may not work properly with less than 60 days.")
        
        # Display basic info about the stock
        stock_info = stock.info
        company_name = stock_info.get('longName', 'Unknown Company')
        current_price = data['Close'].iloc[-1]
        
        print(f"✅ Successfully fetched data for {company_name}")
        print(f"📊 Data points: {len(data)} days")
        print(f"📅 Date range: {data.index[0].date()} to {data.index[-1].date()}")
        print(f"💰 Current price: ₹{current_price:.2f}")
        print(f"📈 Price range: ₹{data['Low'].min():.2f} - ₹{data['High'].max():.2f}")
        
        # Check for missing data
        missing_data = data.isnull().sum().sum()
        if missing_data > 0:
            print(f"⚠️  Warning: {missing_data} missing data points found")
        
        return data
        
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None

def display_results(data, final_balance, trades, initial_balance=100000):
    """Display backtesting results"""
    
    print("\n" + "="*50)
    print("BACKTESTING RESULTS")
    print("="*50)
    
    # Performance metrics
    total_return = final_balance - initial_balance
    return_percentage = (total_return / initial_balance) * 100
    
    print(f"Initial Balance: ₹{initial_balance:,.2f}")
    print(f"Final Balance: ₹{final_balance:,.2f}")
    print(f"Total Return: ₹{total_return:,.2f}")
    print(f"Return Percentage: {return_percentage:.2f}%")
    
    # Trade analysis
    buy_trades = [trade for trade in trades if trade[0] == 'Buy']
    sell_trades = [trade for trade in trades if trade[0] == 'Sell']
    
    print(f"\nTotal Trades: {len(trades)}")
    print(f"Buy Orders: {len(buy_trades)}")
    print(f"Sell Orders: {len(sell_trades)}")
    
    # Show recent trades
    print(f"\nRecent Trades:")
    for trade in trades[-5:]:  # Show last 5 trades
        action, date, price, quantity = trade
        print(f"{action}: {quantity} shares at ₹{price:.2f} on {date.date()}")

def plot_strategy(data):
    """Plot the stock price with SMA lines and buy/sell signals"""
    
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Price and SMAs
    plt.subplot(2, 1, 1)
    plt.plot(data.index, data['Close'], label='Close Price', linewidth=1, alpha=0.8)
    plt.plot(data.index, data['SMA_Short'], label='SMA Short (20)', linewidth=1.5)
    plt.plot(data.index, data['SMA_Long'], label='SMA Long (50)', linewidth=1.5)
    
    # Mark buy and sell signals
    buy_signals = data[data['Position'] == 1]
    sell_signals = data[data['Position'] == -1]
    
    plt.scatter(buy_signals.index, buy_signals['Close'], 
               color='green', marker='^', s=100, label='Buy Signal')
    plt.scatter(sell_signals.index, sell_signals['Close'], 
               color='red', marker='v', s=100, label='Sell Signal')
    
    plt.title('Reliance Stock Price with SMA Crossover Strategy')
    plt.ylabel('Price (₹)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # Plot 2: Trading Signals
    plt.subplot(2, 1, 2)
    plt.plot(data.index, data['Signal'], label='Signal (1=Buy, 0=Sell)', linewidth=2)
    plt.fill_between(data.index, data['Signal'], alpha=0.3)
    plt.title('Trading Signals Over Time')
    plt.ylabel('Signal')
    plt.xlabel('Date')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.show()

def main():
    """Main function to run the complete trading strategy"""
    
    print("="*60)
    print("QUANTITATIVE TRADING STRATEGY - SMA CROSSOVER")
    print("="*60)
    
    # Configuration
    STOCK_SYMBOL = "RELIANCE.NS"  # Reliance on NSE
    INITIAL_BALANCE = 100000  # ₹1 Lakh
    SHORT_WINDOW = 20  # 20-day SMA
    LONG_WINDOW = 50   # 50-day SMA
    PERIOD = "2y"      # 2 years of data
    
    print(f"Stock Symbol: {STOCK_SYMBOL}")
    print(f"Initial Investment: ₹{INITIAL_BALANCE:,}")
    print(f"Strategy: {SHORT_WINDOW}-day SMA vs {LONG_WINDOW}-day SMA crossover")
    print(f"Data Period: {PERIOD}")
    
    # Step 1: Fetch stock data
    print(f"\n📈 Fetching stock data for {STOCK_SYMBOL}...")
    stock_data = fetch_stock_data(STOCK_SYMBOL, PERIOD)
    
    if stock_data is None:
        print("❌ Failed to fetch stock data. Exiting...")
        return
    
    # Step 2: Apply SMA crossover strategy
    print(f"\n🔄 Applying SMA crossover strategy...")
    
    # Import the strategy function
    import importlib.util
    spec = importlib.util.spec_from_file_location("sma_crossover", "Strategies/sma_crossover.py")
    sma_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sma_module)
    
    strategy_data = sma_module.sma_crossover_strategy(stock_data.copy(), SHORT_WINDOW, LONG_WINDOW)
    
    # Step 3: Run backtesting
    print(f"\n💰 Running backtesting...")
    final_balance, trades = backtest(strategy_data, INITIAL_BALANCE)
    
    # Step 4: Display results
    display_results(strategy_data, final_balance, trades, INITIAL_BALANCE)
    
    # Step 5: Plot the strategy
    print(f"\n📊 Generating plots...")
    plot_strategy(strategy_data)
    
    # Step 6: Calculate buy-and-hold comparison
    buy_hold_return = ((strategy_data['Close'].iloc[-1] / strategy_data['Close'].iloc[0]) - 1) * 100
    strategy_return = ((final_balance / INITIAL_BALANCE) - 1) * 100
    
    print(f"\n📊 STRATEGY COMPARISON:")
    print(f"Buy & Hold Return: {buy_hold_return:.2f}%")
    print(f"SMA Strategy Return: {strategy_return:.2f}%")
    
    if strategy_return > buy_hold_return:
        print("✅ SMA Strategy outperformed Buy & Hold!")
    else:
        print("❌ Buy & Hold would have been better.")

if __name__ == "__main__":
    main()