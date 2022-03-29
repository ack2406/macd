import indicator as ind
import pandas as pd

class Buyer:
    def __init__(self, fname, history_days, days_count, pricecap="Close", reverse=False, wallet=0, shares=1000):
        self.fname = fname
        self.history_days = history_days
        self.days_count = days_count

        self.wallet = wallet
        self.shares = shares

        self.pricecap = pricecap
        self.reverse = reverse

        self.macd = ind.Macd(self.fname, day_count=self.history_days, pricecap=self.pricecap, reverse=self.reverse)
        self.day_prices = self.get_day_prices()

        self.first_day_value = self.wallet + self.shares * self.day_prices[0]

    def get_day_prices(self):
        prices_input = pd.read_csv(self.fname)[self.pricecap]
        prices_input = prices_input[::-1] if self.reverse else prices_input

        return [price for price in prices_input[self.history_days:]][:self.days_count]

    def simulate(self):
        for day_price in self.day_prices:
            self.macd.add_day(day_price)
            if self.macd.buy_or_sell() == 1:
                    shares_bought = (self.wallet // day_price) // 2
                    self.wallet -= day_price * shares_bought
                    self.shares += shares_bought
            elif self.macd.buy_or_sell() == -1:
                    shares_selled = self.shares // 2
                    self.wallet += day_price * shares_selled
                    self.shares -= shares_selled
            
if __name__ == "__main__":
    b = Buyer("BA.csv", 30, 335, pricecap="Open", reverse=True, wallet=0, shares=1000)

    before = round(b.first_day_value,2)
    print(f"Before:\nWallet: ${round(b.wallet, 2)}, Shares: {b.shares}, Overall: ${before}")

    b.simulate()

    after = round(b.wallet + b.shares * b.day_prices[-1], 2)
    print(f"After:\nWallet: ${round(b.wallet,2)}, Shares: {b.shares}, Overall: ${after}")

    print(f"\nProfit: {round(after / before * 100) }%")

    b.macd.plot()