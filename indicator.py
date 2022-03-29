import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

class Macd:
    def __init__(self, fname, pricecap="Close", reverse=False, day_count=None):
        prices_input = pd.read_csv(fname)[pricecap]
        prices_input = prices_input[::-1] if reverse else prices_input

        if day_count:
            prices_input = prices_input[:day_count]

        self.prices = [price for price in prices_input]
        self.get_indicators()
    
    def get_indicators(self):
        self.macd = self.get_macd()
        self.signal = self.get_signal()
        self.buy, self.sell = self.get_points()
        self.histogram = self.get_histogram(2)
    
    def add_day(self, price):
        self.prices = self.prices + [price]
        self.get_indicators()

    def ema(self, p, N):
        alpha = 2/(N + 1)
        nominator = sum(p[i]*(1-alpha)**i for i in range(min(N + 1, len(p))))
        denominator = sum((1-alpha)**i for i in range(min(N + 1, len(p))))
        return nominator / denominator
    
    def ema_n(self, prices, N):
        return [self.ema(prices[::-1][i:N+i+1], N) for i in range(len(prices))][::-1]

    def get_macd(self):
        ema12 = self.ema_n(self.prices, 12)
        ema26 = self.ema_n(self.prices, 26)
        return [e12 - e26 for e12, e26 in zip(ema12, ema26)]

    def get_signal(self):
        return self.ema_n(self.macd, 9)

    def get_histogram(self, spl):
        return [m - s if i % spl == 0 else 0 for m, s, i in zip(self.macd, self.signal, range(len(self.macd)))]

    def intersect(self, i):
        if self.macd[i] >= self.signal[i] and self.macd[i - 1] < self.signal[i - 1]:
            return 1
        elif self.macd[i] <= self.signal[i] and self.macd[i - 1] > self.signal[i - 1]:
            return -1
        return 0

    def buy_or_sell(self):
        price_index = len(self.prices) - 1
        return self.intersect(price_index)

    def get_points(self):
        buying_points = [i for i in range(1, len(self.prices)) if self.intersect(i) == 1]
        selling_points = [i for i in range(1, len(self.prices)) if self.intersect(i) == -1]
        return buying_points, selling_points

    def plot(self):
        plt.clf()
        fig, (ax1, ax2) = plt.subplots(2)

        ax1.plot(self.prices, color="cornflowerblue", zorder=-1, label="Price")
        ax1.set_title("Stock Prices")
        ax1.scatter(self.buy, [self.prices[i] for i in self.buy], color="forestgreen", zorder=1, label="Buy Signal")
        ax1.scatter(self.sell, [self.prices[i] for i in self.sell], color="crimson", zorder=1, label="Sell Signal")
        ax1.legend()
        ax1.set_xlabel("Day")
        ax1.set_ylabel("Price")

        ax2.bar(range(len(self.histogram)), self.histogram, color="crimson")

        ax2.plot(self.macd, color="royalblue", label="MACD Line")
        ax2.plot(self.signal, color="orange", label="Signal Line")
        ax2.set_title("Indicator")
        ax2.legend()
        ax2.set_xlabel("Day")
        ax2.set_ylabel("Indicator Value")

        # plt.savefig('macd.pgf')

        plt.show()

if __name__ == "__main__":
    # matplotlib.use("pgf")
    # matplotlib.rcParams.update({
    #     "pgf.texsystem": "pdflatex",
    #     'font.family': 'serif',
    #     'text.usetex': True,
    #     'pgf.rcfonts': False,
    # })

    a = Macd("BA.csv", pricecap="Open", reverse=True)
    a.plot()