from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
from googlesearch import search
import re
from lxml import etree
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
chrome_options = Options()
chrome_options.add_argument("--window-size=1024x768")
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=chrome_options)
#driver = webdriver.Chrome(ChromeDriverManager().install())


import config
import time
def get_url(name,site,urlkey):
    try:
        query = name + ' ' + site
        #url_list = search(query, tld="co.in", num=10, stop=10, pause=2)
        url_list = search(query)

        #print(list(url_list))
        url_list = [x for x in list(url_list) if re.search(urlkey, x)]
        req = driver.get(url_list[0])
        driver.set_page_load_timeout(20)
        driver.maximize_window()
        return url_list[0],driver
    except Exception as e:
        print(e)
        return 'nan'
    
def get_attributedata(driver,xpath,regex):
    try:
        attribute_data = (driver.find_element_by_xpath(xpath).text)
        attribute_data = re.findall(regex, attribute_data)
        try:
            attribute_data = [float(data.strip().replace(',','')) for data in attribute_data]
            return attribute_data
        except Exception as e:
            print(e)
            return attribute_data
        
    except Exception as e:
        print(e)
        return '-'
    
def get_data(name,excol,cols):
    try:
        url_data,driver_data = get_url(name, 
                config.keyworddict[excol][0],
                config.keyworddict[excol][1])

        data = {}
        for i in range(len(cols)):
            try:
                data[cols[i]]=get_attributedata(driver_data,
                                                     config.xpathdict[cols[i]],
                                                     config.regexdict[cols[i]])
            except:
                continue
            data['Company'] = [name]*5
            data = pd.DataFrame(data)
        return data
    except:
        data = pd.DataFrame({k:'-' for k in cols+['Company']},index=[0])
        return data
    
def get_alldata(name):
    print("getting data for {}".format(name))
    financialratios = get_data(name,'EarningsPerShare',config.columns[0:6])
    consolidatedratios = get_data(name,'InterestCoverageRatio',[config.columns[6]])
    balancesheet = get_data(name,'Assets',config.columns[7:])
    df_final = pd.concat([financialratios,consolidatedratios,balancesheet],axis=1)
    time.sleep(300)
    return df_final 

securities = pd.read_csv('Equity.csv')

def daily_run(n):    
    seclist = list(securities['Security Name'])[n:n+15]
    df_list = [get_alldata(sec) for sec in seclist]
    df_list_new = [ df.loc[:,~df.columns.duplicated()] for df in df_list]
    df_final = pd.concat(df_list_new)
    df_final.to_csv('fundamentals_data_{}_{}.csv'.format(n,n+15))
    return None

def consolidate():
    import glob
    jpgFilenamesList = glob.glob('fundamentals_data*.csv')
    df_list = [pd.read_csv(file) for file in jpgFilenamesList]
    df_final = pd.concat(df_list)
    print("number of rows before dropping empty earnings per share and interest coverage ratio is {}".format(len(df_final)))
    df_final = df_final.dropna(subset=['EarningsPerShare','InterestCoverageRatio'],how='any')
    print("number of rows after dropping empty earnings per share and interest coverage ratio is {}".format(len(df_final))) 
    df_final.to_csv('fundamentals_and_ratios.csv',index=False)
    
def main_run():
    num_list = list(range(3195,len(securities),15))
    for i in num_list:
        daily_run(i)
        time.sleep(3600)
        consolidate()
        
main_run()