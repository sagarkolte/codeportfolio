columns = [
    "Dates",
    "EarningsPerShare",
    "DividendPerShare",
    "RetentionRatio",
    "Price/BookRatio",
    "Debt/EquityRatio",
    "InterestCoverageRatio",
    "Assets",
    "NonCurrentLiabilities",
    "CurrentLiabilities",
    "ShareholdersEquity"]

xpathdict = {"EarningsPerShare":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[3]',
            "DividendPerShare":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[8]',
            "RetentionRatio":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[30]',
            "Price/BookRatio":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[38]',
            "Debt/EquityRatio":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[22]',
            "InterestCoverageRatio":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[34]',
            "Assets":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[43]',
            "Dates": '//*[@id="standalone-new"]/div[1]/table/tbody/tr[1]',
            "NonCurrentLiabilities":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[15]',
            "CurrentLiabilities":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[21]',
            "ShareholdersEquity":'//*[@id="standalone-new"]/div[1]/table/tbody/tr[9]'}


regexdict={"EarningsPerShare":'\s\d*\.\d*',
            "DividendPerShare":'\s\d*\.\d*',
            "RetentionRatio":'\s\d*\.\d*',
            "Price/BookRatio":'\s\d*\.\d*',
            "Debt/EquityRatio":'\s\d*\.\d*',
            "InterestCoverageRatio":'\s\d*\.\d*',
            "Assets":'[^A-Z\s-]\d*,*\d*.\d*',
            "Dates": 'MAR\s\d*',
            "NonCurrentLiabilities":'[^A-Z\s-]\d*,*\d*.\d*',
            "CurrentLiabilities":'[^A-Z\s-]\d*,*\d*.\d*',
            "ShareholdersEquity":'[^A-Z\s-]\d*,*\d*.\d*'}


keyworddict = {"EarningsPerShare":['moneycontrol financial ratios','ratiosVI'],
            "DividendPerShare":['moneycontrol financial ratios','ratiosVI'],
            "RetentionRatio":['moneycontrol financial ratios','ratiosVI'],
            "Price/BookRatio":['moneycontrol financial ratios','ratiosVI'],
            "Debt/EquityRatio":['moneycontrol financial ratios','ratiosVI'],
            "InterestCoverageRatio":['moneycontrol consolidated ratios','consolidated-ratiosVI'],
            "Assets":['moneycontrol balancesheet',''],
            "Dates": ['moneycontrol balancesheet',''],
            "CurrentLiabilities":['moneycontrol balancesheet',''],
            "ShareholdersEquity":['moneycontrol balancesheet','']}
