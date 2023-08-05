import unittest

from unibit_api_v2.company import CompanyInfo
from unibit_api_v2.corporate import Corporate
from unibit_api_v2.crypto import CryptoPrice
from unibit_api_v2.forex import ForexRate
from unibit_api_v2.news import StockNews
from unibit_api_v2.reference import Coverage
from unibit_api_v2.stock import StockPrice

sp = StockPrice(key="demo")
data1 = sp.getHistoricalStockPrice(ticker=["AAPL", "WORK"], startDate="2019-09-15", endDate="2019-09-20",
                                   selectedFields="ticker,date")
# print(data1)

data2 = sp.getRealTimeStockPrice(ticker=["AAPL"], startDate="2019-09-15", endDate="2019-09-20", startMinute="default",
                                 endMinute="default", selectedFields="price,date")
# print(data2)


ci = CompanyInfo(key="demo")
data3 = ci.getCompanyFinancials(ticker=["AAPL,WORK"], statement="all", interval="quarterly", startDate="2019-03-25",
                                endDate="2019-08-30")
# print(data3)

data4 = ci.getCompanyProfile(ticker=["AAPL"])
# print(data4)

data5 = ci.getCompanyFinancialSummary(ticker=["AAPL"])
# print(data5)

data6 = ci.getOwnershipStructure(ticker=["AAPL,WORK"], ownershipType="majority_holder", startDate="2019-09-12",
                                 endDate="2019-09-27")
# print(data6)

data7 = ci.getInsiderTransactions(ticker=["AAPL,WORK"], startDate="2019-08-25", endDate="2019-08-30")
# print(data7)

data8 = ci.getSECFilingLinks(ticker=["AAPL"], startDate="2019-07-25", endDate="2019-08-30", selectedFields="cik")
print(data8)

sn = StockNews(key="demo")
data9 = sn.getStockNews(ticker=["AAPL"], startDate="2019-08-25", endDate="2019-08-30", startMinute="10:00:00",
                        endMinute="11:00:00", genre="partnership", sector="technology", selectedFields="date,time")
print(data9)

corporate = Corporate(key="demo")
data10 = corporate.getCorporateSplits(ticker=["all"], startDate="2019-02-01", endDate="2019-02-11")
# print(data10)

data11 = corporate.getCorporateDividends(ticker=["all"], startDate="2019-02-01", endDate="2019-02-11")
# print(data11)


cp = CryptoPrice(key="demo")
data12 = cp.getHistoricalCryptoPrice(ticker=["BCH-USD"], startDate="2019-08-25", endDate="2019-08-30")

fr = ForexRate(key="demo")
data13 = fr.getRealtimeForexRates(base="usd", foreign=["cny,eur,inr"], amount=1, startDate="2019-08-29",
                                  endDate="2019-08-29", startMinute="11:00:00", endMinute="12:00:00")
# print(data13)

data14 = fr.getHistoricalForexRates(base="usd", foreign=["cny,eur,inr"], amount=1, startDate="2019-08-20",
                                    endDate="2019-08-25", startMinute="11:00:00", endMinute="12:00:00")
# print(data14)


c = Coverage(key="demo")
data15 = c.getAssetCoverage(exchange=["NASDAQ"])
# print(data15)

data16 = c.getCryptoCoverage()
# print(data16)

KEY_ZULIN = "Xx14B8DlXDQgE3XA7jIqRAuFH18ZEvmc"

sp = StockPrice(key=KEY_ZULIN)
ci = CompanyInfo(key=KEY_ZULIN)
sn = StockNews(key=KEY_ZULIN)
corporate = Corporate(key=KEY_ZULIN)
cp = CryptoPrice(key=KEY_ZULIN)
fr = ForexRate(key=KEY_ZULIN)
c = Coverage(key=KEY_ZULIN)

data17 = sp.getHistoricalStockPrice(ticker=["AAPL", "WORK", "AMZN"], startDate="2019-09-15", endDate="2019-09-20")
data18 = sp.getRealTimeStockPrice(ticker=["AMZN"], startDate="2019-09-15", endDate="2019-09-20", startMinute="default",
                                  endMinute="default", size=10)
data19 = ci.getCompanyFinancials(ticker=["AAPL,WORK", "AMZN"], statement="all", interval="quarterly",
                                 startDate="2019-03-25", endDate="2019-08-30")
data20 = ci.getCompanyProfile(ticker=["AMZN"])
data21 = ci.getCompanyFinancialSummary(ticker=["AMZN"])
data22 = ci.getOwnershipStructure(ticker=["AAPL,AMZN"], ownershipType="majority_holder", startDate="2019-09-12",
                                  endDate="2019-09-27")
data23 = ci.getInsiderTransactions(ticker=["AAPL,WORK", "AMZN"], startDate="2019-08-25", endDate="2019-08-30")
data24 = ci.getSECFilingLinks(ticker=["AMZN"], startDate="2019-07-25", endDate="2019-08-30")
data25 = sn.getStockNews(ticker=["AAPL", "AMZN"], startDate="2019-08-25", endDate="2019-08-30", startMinute="10:00:00",
                         endMinute="11:00:00", genre="partnership", sector="technology")
data26 = corporate.getCorporateSplits(ticker=["all"], startDate="2019-02-01", endDate="2019-02-11")
data27 = corporate.getCorporateDividends(ticker=["all"], startDate="2019-02-01", endDate="2019-02-11")
data28 = cp.getHistoricalCryptoPrice(ticker=["BCH-USD"], startDate="2019-08-25", endDate="2019-08-30")
data29 = fr.getRealtimeForexRates(base="usd", foreign=["cny,eur,inr"], amount=1, startDate="2019-08-29",
                                  endDate="2019-08-29", startMinute="11:00:00", endMinute="12:00:00")
data30 = fr.getHistoricalForexRates(base="usd", foreign=["cny,eur,inr"], amount=1, startDate="2019-08-20",
                                    endDate="2019-08-25", startMinute="11:00:00", endMinute="12:00:00")
data31 = c.getAssetCoverage(exchange=["NASDAQ"])
data32 = c.getCryptoCoverage()

data33 = sp.getRealTimeStockPrice(ticker=["AMZN"], startDate="2019-09-15", endDate="2019-09-20", startMinute="default",
                                  endMinute="default", size=10)
# data34 = ci.getCompanyFinancials(ticker=["AAPL,WORK","AMZN"], statement = "all", interval = "quarterly", startDate="2019-03-25", endDate="2019-08-30", size = 10)
data35 = ci.getSECFilingLinks(ticker=["AMZN"], startDate="2019-07-25", endDate="2019-08-30", size=10)
data36 = sn.getStockNews(ticker=["AAPL", "AMZN"], startDate="2019-08-25", endDate="2019-08-30", startMinute="10:00:00",
                         endMinute="11:00:00", genre="partnership", sector="technology", size=10)
data37 = corporate.getCorporateSplits(ticker=["all"], startDate="2019-02-01", endDate="2019-02-11", size=10)
data38 = cp.getHistoricalCryptoPrice(ticker=["BCH-USD"], startDate="2019-08-25", endDate="2019-08-30", size=10)
# data39 = fr.getHistoricalForexRates(base = "usd", foreign = ["cny,eur,inr"], amount = 1, startDate = "2019-08-20", endDate = "2019-08-25", startMinute = "11:00:00", endMinute = "12:00:00", size = 10)

print(data33)
print(data37)
len1 = len(data33["result_data"]["AMZN"])
len2 = len(data35["result_data"]["AMZN"])
len3 = len(data36["result_data"]["AMZN"])
len4 = len(data37["result_data"])
len5 = len(data38["result_data"]["BCH-USD"])

num1 = data33["meta_data"]["num_total_data_points"]
num2 = data35["meta_data"]["num_total_data_points"]
num3 = data36["meta_data"]["num_total_data_points"]
num4 = data37["meta_data"]["data points"]
num5 = data38["meta_data"]["num_total_data_points"]

credit1 = data33["meta_data"]["credit_cost"]
credit2 = data35["meta_data"]["credit_cost"]
credit3 = data36["meta_data"]["credit_cost"]
credit4 = data37["meta_data"]["credit cost"]
credit5 = data38["meta_data"]["credit_cost"]

print(len1)
print(len2)
print(len3)
print(len4)
print(len5)

print(num1)
print(num2)
print(num3)
print(num4)
print(num5)

print("***************")
print(credit1)
print("****************")
print(credit2)
print(credit3)
print(credit4)
print(credit5)

print(data17)


class TestToPass(unittest.TestCase):

    def test_shouldReturnDemoData(self):
        ##### done above #####
        pass

    def test_hasMetaData(self):
        # self.assertEqual("foo".upper(), "FOO")
        self.assertIsNotNone(data17["meta_data"])
        self.assertIsNotNone(data18["meta_data"])
        self.assertIsNotNone(data19["meta_data"])
        self.assertIsNotNone(data20["meta_data"])
        self.assertIsNotNone(data21["meta_data"])
        self.assertIsNotNone(data22["meta_data"])
        self.assertIsNotNone(data23["meta_data"])
        self.assertIsNotNone(data24["meta_data"])
        self.assertIsNotNone(data25["meta_data"])
        self.assertIsNotNone(data26["meta_data"])
        self.assertIsNotNone(data27["meta_data"])
        self.assertIsNotNone(data28["meta_data"])
        self.assertIsNotNone(data29["meta_data"])
        self.assertIsNotNone(data30["meta_data"])
        self.assertIsNotNone(data31["meta_data"])
        self.assertIsNotNone(data32["meta_data"])

    def test_hasContent(self):
        self.assertIsNotNone(data17["result_data"])
        self.assertIsNotNone(data18["result_data"])
        self.assertIsNotNone(data19["result_data"])
        self.assertIsNotNone(data20["result_data"])
        self.assertIsNotNone(data21["result_data"])
        self.assertIsNotNone(data22["result_data"])
        self.assertIsNotNone(data23["result_data"])
        self.assertIsNotNone(data24["result_data"])
        self.assertIsNotNone(data25["result_data"])
        self.assertIsNotNone(data26["result_data"])
        self.assertIsNotNone(data27["result_data"])
        self.assertIsNotNone(data28["result_data"])
        self.assertIsNotNone(data29["result_data"])
        self.assertIsNotNone(data30["result_data"])
        self.assertIsNotNone(data31["result_data"])
        self.assertIsNotNone(data32["result_data"])

    def test_hasDataWithSize(self):
        self.assertEqual(len1, 10)
        self.assertEqual(len2, 4)
        self.assertEqual(len3, 10)
        self.assertEqual(len4, 10)
        self.assertEqual(len5, 7)

    def test_hasCorrectCreditCost(self):
        self.assertEqual(num1, credit1)
        self.assertEqual(num2, credit2)
        self.assertEqual(num3 * 100, credit3)
        self.assertEqual(num4, credit4)
        self.assertEqual(num5 * 10, credit5)

    def test_shouldReturnApiKeyPromotion(self):
        ### done above ###
        pass

    def test_shouldReturnDataWithSelectedFields(self):
        ### current unavailable ###
        pass


if __name__ == '__main__':
    unittest.main()
