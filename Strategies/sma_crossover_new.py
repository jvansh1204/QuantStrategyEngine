import pandas as pd

def sma_crossover_strategy(data, short_window=20, long_window=50):
   
    data = data.copy()
    
    data['SMA_Short'] = data['Close'].rolling(window=short_window).mean()
    data['SMA_Long'] = data['Close'].rolling(window=long_window).mean()

    data['Signal'] = 0
    
    data['Signal'][short_window:] = (
        (data['SMA_Short'][short_window:] > data['SMA_Long'][short_window:]).astype(int)
    )
    
    data['Position'] = data['Signal'].diff()

    return data

if __name__ == "__main__":
    print("SMA Crossover Strategy module loaded successfully!")
    print("Available function: sma_crossover_strategy")
