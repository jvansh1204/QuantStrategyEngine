import matplotlib.pyplot as plt

def backtest(data, initial_balance=100000):
    balance = initial_balance
    position = 0
    trades = []

    for i in range(1, len(data)):
        if data['Position'][i] == 1 and position == 0:  # Buy signal
            units_to_buy = balance // data['Close'][i]
            amount_spent = units_to_buy * data['Close'][i]
            position += units_to_buy
            balance -= amount_spent  # Deduct only the amount spent
            trades.append(('Buy', data.index[i], data['Close'][i], units_to_buy))

        elif data['Position'][i] == -1 and position > 0:  # Sell signal
            # Sell all or part of the position
            sell_amount = position  # Change this to desired sell amount for partial sells
            balance += sell_amount * data['Close'][i]
            position -= sell_amount
            trades.append(('Sell', data.index[i], data['Close'][i], sell_amount))
    
    # At the end, add any remaining stock value to final balance
    if position > 0:
        balance += position * data['Close'].iloc[-1]

    return balance, trades
