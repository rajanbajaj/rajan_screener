from rajan_nse import Session
from time import sleep

class Screener:
    BASE_URL="https://www.screener.in"
    def __init__(self):
        self.session = Session(self.BASE_URL)

    def getCompanyId(self, symbol):
        data = self.session.makeRequest(self.BASE_URL+'/api/company/search/?q='+symbol)
        if data:
            return data[0]['id']
        return None
        
    def getChart(self, symbol, days=365, type='price'):
        id = self.getCompanyId(symbol)
        q = 'Price-DMA50-DMA200-Volume'

        if id:
            if type == 'pe':
                q = 'Price to Earning-Median PE-EPS'
            elif type == 'ebita':
                q = 'EV Multiple-Median EV Multiple-EBITDA'
            elif type == 'pb':
                q = 'Price to book value-Median PBV-Book value'

            url = f'{self.BASE_URL}/api/company/{str(id)}/chart/?q={q}&days={days}'
            data = self.session.makeRequest(url)
            return data['datasets']
        else:
            return None
        
    def getPrice(self, symbol, days=365, offsetDays=0):
        try:
            priceData = []
            actualDays = days+offsetDays
            dataset = self.getChart(symbol, actualDays, 'price')
            for data in dataset:
                if data['metric'] == 'Price':
                    priceData = data['values']
                    priceData = priceData[0:days]
            return priceData
        except:
            sleep(3)
            return self.getPrice(symbol, days, offsetDays)

    def getPE(self, symbol, days=365, offsetDays=0):
        try:
            peData = []
            actualDays = days+offsetDays
            dataset = self.getChart(symbol, actualDays, 'pe')
            for data in dataset:
                if data['metric'] == 'Price to Earning':
                    peData = data['values']
                    peData = peData[0:days]
            return peData
        except:
            sleep(3)
            return self.getPE(symbol, days, offsetDays)
    
    def getEPS(self, symbol, days=365, offsetDays=0):
        try:
            epsData = []
            actualDays = days+offsetDays
            dataset = self.getChart(symbol, actualDays, 'pe')
            for data in dataset:
                if data['metric'] == 'EPS':
                    epsData = data['values']
                    epsData = epsData[0:days]
            return epsData
        except:
            sleep(3)
            return self.getEPS(symbol, days, offsetDays)

    def getReturns(self, symbol, days=365, offsetDays=0):
        priceData = self.getPrice(symbol, days, offsetDays)
        peData = self.getPE(symbol, days, offsetDays)
        epsData = self.getEPS(symbol, days, offsetDays)

        # calculate total returns using priceData
        if len(priceData) > 0 and len(peData) > 0 and len(epsData) > 0:
            totalReturns = ((float(priceData[-1][1]) - float(priceData[0][1])) / float(priceData[0][1])) * 100
            speculativeReturns = ((float(epsData[-1][1]) * (float(peData[-1][1]) - float(peData[0][1]))) / float(priceData[0][1])) * 100 
            fundamentalReturns = totalReturns - speculativeReturns
            return {'total': totalReturns, 'speculative': speculativeReturns, 'fundamental': fundamentalReturns}