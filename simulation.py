# simulation.py
import logging
from datetime import datetime, timedelta
from config import MAX_TRADE_DURATION, LONG_TRAILING_STOP_MULTIPLIER, LONG_TRAILING_STOP_OFFSET

class Trade:
    def __init__(self, symbol, entry_price, tp, sl, size, trade_type, atr):
        self.symbol = symbol
        self.entry_price = entry_price
        self.tp = tp
        self.sl = sl
        self.size = size
        self.trade_type = trade_type  # only "long" trades in pure spot trading
        self.atr = atr  # ATR at entry (used for trailing stop)
        self.status = 'open'
        self.exit_price = None
        self.pnl = 0.0
        self.entry_time = datetime.now()  # record when trade is entered

    def update(self, current_price):
        if self.trade_type == 'long':
            # Calculate profit for a long trade.
            profit = current_price - self.entry_price

            # Check for trailing stop: if profit > ATR * multiplier, update stop loss.
            threshold = self.atr * LONG_TRAILING_STOP_MULTIPLIER
            if profit > threshold:
                # For a long trade, new SL is current_price minus an offset.
                new_sl = current_price - self.atr * LONG_TRAILING_STOP_OFFSET
                # Only update if the new stop loss is higher than the current one.
                if new_sl > self.sl:
                    logging.info(f"Updating stop loss for {self.symbol}: {self.sl:.6f} -> {new_sl:.6f}")
                    self.sl = new_sl

            # Time-based exit: if trade has been open longer than MAX_TRADE_DURATION, force exit.
            now = datetime.now()
            if (now - self.entry_time).total_seconds() > MAX_TRADE_DURATION:
                logging.info(f"Time-based exit for {self.symbol}")
                self.status = 'closed'
                self.exit_price = current_price
                self.pnl = (current_price - self.entry_price) * self.size
                return True

            # Check if stop loss is hit (price falls below SL)
            if current_price <= self.sl:
                self.status = 'closed'
                self.exit_price = current_price
                self.pnl = (current_price - self.entry_price) * self.size
                return True
            # Check if take profit is hit (price rises to or above TP)
            elif current_price >= self.tp:
                self.status = 'closed'
                self.exit_price = current_price
                self.pnl = (current_price - self.entry_price) * self.size
                return True
        else:
            # No short trade logic in pure spot trading.
            pass
        return False

class SimulationAccount:
    def __init__(self, initial_balance=1000.0):
        self.balance = initial_balance
        self.open_trades = {}  # symbol -> Trade
        self.closed_trades = []

    def enter_trade(self, symbol, entry_price, tp, sl, trade_type='long', allocation=0.1, atr=0):
        if symbol in self.open_trades:
            logging.info(f"Trade already open for {symbol}")
            return
        trade_amount = self.balance * allocation
        size = trade_amount / entry_price
        trade = Trade(symbol, entry_price, tp, sl, size, trade_type, atr)
        self.open_trades[symbol] = trade
        logging.info(f"Entered {trade_type} trade for {symbol} at {entry_price:.6f}, TP: {tp:.6f}, SL: {sl:.6f}, size: {size:.6f}")
        # Optionally, you can call send_telegram_alert() here.

    def update_trades(self, symbol, current_price):
        if symbol in self.open_trades:
            trade = self.open_trades[symbol]
            if trade.update(current_price):
                self.balance += trade.pnl
                self.closed_trades.append(trade)
                logging.info(f"Trade for {symbol} closed at {trade.exit_price:.6f}, PnL: {trade.pnl:.2f}, New Balance: {self.balance:.2f}")
                # Optionally, you can send an exit alert here.
                del self.open_trades[symbol]

    def summary(self):
        total_pnl = sum(t.pnl for t in self.closed_trades)
        summary_info = {
            "balance": self.balance,
            "total_pnl": total_pnl,
            "num_trades": len(self.closed_trades),
            "closed_trades": self.closed_trades
        }
        logging.info(f"Simulation Summary: Balance: {self.balance:.2f}, Total PnL: {total_pnl:.2f}, Trades: {len(self.closed_trades)}")
        return summary_info
