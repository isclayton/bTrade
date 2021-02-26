import requests
import sys
import json
import time
import os
import numpy as np
from termcolor import colored
from terminalplot import plot
base_url = 'https://api.kraken.com/'

API_KEY = ''
API_SIG = ''
VOLUME = 10
LIMIT_BUY_THRESHOLD = 1.01
LIMIT_SELL_THRESHOLD = 0.99
class Kraken:
    USD = 1000
    ADA = 1000
    orders = {'sell':[], 'buy': []}
    history = {'Time': [], 'Price': []}
    positions = {}
    STDEVS = 1
    #Simulate limit orders
    def process_orders(self, current_price):
        try:
            sell_orders = self.orders['sell']
            buy_orders = self.orders['buy']
        except KeyError:
            return
       
        if len(sell_orders) > 0:
            if order[0] <= self.ADA and order[1] <= current_price:
                    self.sell_market(current_price,order[0])
                    self.orders['sell'].remove(order)
        if len(buy_orders) > 0:
        
            for order in buy_orders:
                if order[0]*order[1] <= self.USD and order[1] >= current_price:
                    self.buy_market(current_price,order[0])
                    self.orders['buy'].remove(order)
        #orders = {'sell':[], 'buy': []}

    #Buy {amount} at current market price
    def buy_market(self, current_price, amount):
        
        if amount*current_price <= self.USD:
            self.ADA += amount
            self.USD -= amount*current_price 
            self.positions[current_price] = amount
            return True
        else:
            return False
        
    #Sell {amount} at current market price
    def sell_market(self,current_price, amount):
        if amount <= self.ADA:
            self.ADA -= amount
            self.USD += amount*current_price 
            return True
        else:
            return False
        
    #Buy {amount} at some price {price}
    def buy_limit(self, amount, price):
        self.orders['buy'].append([amount, price])
        pass
        #sdada
    
    #Sell {amount} at some price {price}
    def sell_limit(self, amount, price):

        self.orders['sell'].append([amount, price])
        pass
        #asda

    #Get current asset price
    def getAssetPrice(self, asset):
        url = base_url+f'0/public/Ticker?pair={asset}'
        res = json.loads(requests.get(url).text)['result'][f'{asset}']['c']
        #print(res)
        return float(res[0])

    def getAssetHistory(self, asset):
        url = f'https://api.kraken.com/0/public/OHLC?pair={asset}&since={time.time()-(12000)}'
        res = requests.get(url).json()['result'][f'{asset}']
       
        last_20 = []
        prices = []
       
        timestamps = []
        while len(last_20) < 20:
            for timestep in res[-20:]:
     
                last_20.append(float(timestep[1]))
                timestamps.append(timestep[0])
            for timestep in res:
      
                prices.append(float(timestep[1]))
                timestamps.append(timestep[0])
        self.history['Time'] = timestamps
        self.history['Price'] = prices
        #print(timestamps)
        return last_20
    
    def showPositions(self, current_price):
        os.system('clear')
        lower = colored(self.LOWER_BAND, 'green')
        upper = colored(self.UPPER_BAND,'red')
        print(f"\r{colored(f'============================================================================================','yellow')}")
        print(f"{f'Lower: {lower}    Current price: {current_price}   Upper: {upper}     ADA: {self.ADA}     USD: {self.USD}'}")
        print(f"\r{colored(f'============================================================================================','yellow')}")

        if len(self.orders['sell']) > 0 :
            text = f"Limit Sells: {sorted([i[1] for i in self.orders['sell']])}"
            print(colored(text, 'red'))
        else:
            text = f"Limit Sells: No Sell Orders"
            print(colored(text, 'red'))
       
        if len(self.orders['buy']) > 0 :
            text = f"Limit Buys: {sorted([i[1] for i in self.orders['buy']])}"
            print(colored(text, 'green'))
        else:
            text = f"Limit Buys: No Buy Orders"
            print(colored(text, 'green'))
        
        ''' This doesnt work
        if len(self.positions) > 0 :
            text = f"Positions: {sorted([i[1] for i in self.positions])}"
            print(colored(text, 'yellow'))
        else:
            text = f"Positions: None"
            print(colored(text, 'yellow'))
        '''
    def bands(self):
        asset_history = self.getAssetHistory('ADAUSD')
        stdev = np.std(asset_history)
        mean = np.mean(asset_history)
        return mean, stdev

    def run(self, current_price):
        mean, stdev = self.bands()
        self.UPPER_BAND = mean+self.STDEVS*stdev
        self.LOWER_BAND = mean-self.STDEVS*stdev
        #print(mean, stdev)
        if current_price > ((mean + self.STDEVS*stdev)):
            return -1
        elif current_price < (mean + -self.STDEVS*stdev):
            return 1
        else:
            return 0


krack = Kraken()

while True:
    
    current_price = krack.getAssetPrice('ADAUSD')
    krack.process_orders(current_price)
    
    try:
        action = krack.run(current_price)
        if action == 0:
            pass
        elif action == 1:
            success = krack.buy_market(current_price,VOLUME)
            if success: 
                krack.sell_limit(VOLUME, current_price*LIMIT_SELL_THRESHOLD)
        elif action == -1:
            success = krack.sell_market(current_price,VOLUME)
            if success:
                krack.buy_limit(VOLUME, current_price*LIMIT_BUY_THRESHOLD)
    except Exception as e:
        print(e)
        pass
    krack.showPositions(current_price)
    
    time.sleep(5)