from selenium import webdriver
import time
import numpy as np
import pandas as pd
import requests
from urllib import parse
import re
from  bs4 import BeautifulSoup
import json
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from selenium.webdriver.support.ui import Select
import random
import csv
write_to_csv_name = "背書_1.csv"
read_file = "tick_name1.csv"


url = "https://mops.twse.com.tw/mops/web/t05st11"

def start_driver():
    path = "chromedriver"
    chrome_options = webdriver.ChromeOptions()  # bihmplhobchoageeokmgbdihknkjbknd
    # chrome_options.add_extension('bihmplhobchoageeokmgbdihknkjbknd')
    chrome_options.add_extension('extension_7_0_10_0.crx')
    chrome_options.add_argument("enable-automation")
    chrome_options.add_argument("test-type=browser")
    chrome_options.add_argument("disable-plugins")
    chrome_options.add_argument("disable-infobars")
    # chrome_options.add_extension('scrapy_win/t.crx')
    prefs = {"profile.default_content_setting_values.notifications": 2}
    chrome_options.add_experimental_option("prefs", prefs)
    driver1 = webdriver.Chrome(path, options=chrome_options)
    return driver1


driver1 = start_driver()
driver1.get("data:,")
driver1.execute_script("window.open('chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html')")
handles = driver1.window_handles



#%%

#選擇歷史資訊
def select_history():
    driver1.get(url)
    select_history_data = Select(driver1.find_element_by_css_selector("select#isnew"))
    select_history_data.select_by_index(1)


#寫入股價代號
def send_tick_name(tick_name):
    driver1.find_element_by_css_selector("input#co_id").clear()
    driver1.find_element_by_css_selector('input#co_id').send_keys(tick_name)

#寫入要的年份
def send_year(year):
    driver1.find_element_by_css_selector("input#year").clear()
    driver1.find_element_by_css_selector("input#year").send_keys(str(year))

#寫入要的月份
def send_mounth(mounth):
    select_mounth = Select(driver1.find_element_by_css_selector("select#month"))
    select_mounth.select_by_index(mounth)

#按查詢
def click_send_button():
    element = driver1.find_element_by_css_selector("div.search input[type=button]")
    driver1.execute_script("arguments[0].click();", element)

#等到確認目標存在
def check_is_ready():
    element = WebDriverWait(driver1, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR,
                                        "table.hasBorder tr th.tblHead"))
    )
    
#掛載vpn
def vpn(number):
    try:
        if number == 0:
            driver1.switch_to.window(handles[1])
            driver1.get("chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html")
            time.sleep(2)
            driver1.find_element_by_css_selector("div.main__button-group button").click()
            time.sleep(2)
            driver1.switch_to.window(handles[0])
        else:
            driver1.switch_to.window(handles[1])
            # driver1.get("chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html")
            driver1.find_element_by_css_selector("div.main__button-group button").click()
            time.sleep(2)
            driver1.switch_to.window(handles[0])
    except:
        driver1.quit()


#獲取頁面資訊
def get_data_page():
    html = driver1.page_source
    soup = BeautifulSoup(html, "lxml")
    table = soup.select("table.hasBorder")[2]
    datas = table.select("tr")[1:]
    return datas


columns=["tick_name","year","mounth","本公司有背書保證資訊","各子公司有背書保證資訊"]

#%%
#檢查上次爬到的位置
start = 0
try:
    start_point = pd.read_csv("r2.csv")
    start_point = start_point["remember"]
    start = start_point.values[0]
    print("start:" , start)
except:
    print("start")

#如果是第一次啟動 建立一個csv儲存爬到的位置
if start == 0:
    with open(write_to_csv_name, "a", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
else:
    pass


tick_name = pd.read_csv(read_file)
tick_name =tick_name["tick_name"]


end = len(tick_name[start:len(tick_name)])

all_data =[]

block_time = 0
#選擇歷史資訊
select_history()

#帶入所有股票代碼
for tick in tick_name[start:len(tick_name)]:
    for year in range(90, 111):

        try:
            driver1.switch_to.window(handles[0])
        except:
            driver1 = start_driver()
            driver1.get("data:,")
            driver1.execute_script(
                "window.open('chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html')")
            handles = driver1.window_handles
            driver1.switch_to.window(handles[0])
            block_time = 0

        try:
            driver1.get(url)

        except:
            driver1.refresh()



        mounth = 3


        # 因為怕被擋所以用while迴圈,如果被擋月數不會繼續,直到抓到資料
        while mounth <= 12:
            data_year_mounth = []
             # 嘗試去點頁面資訊 如果出錯代表被擋 掛載vpn
            try:
                select_history()
                send_year(year)
                send_mounth(mounth)
                send_tick_name(tick)
                click_send_button()
            except:
                vpn(block_time)
                print("我們被擋了")
                continue

            try:
             #try 確認資料存再不,如果不存在，可能被檔，進except檢查是否被擋
                check_is_ready()
            except:
                d = driver1.page_source
                soup = BeautifulSoup(d, "lxml")
                try:
                    cc = soup.select("center h3")[0]
                    #檢查是否是資料庫無資料
                    if cc.text.strip() == "資料庫中查無需求資料":
                        data_year_mounth.append(tick)
                        # 將年寫入data_year_mounth
                        data_year_mounth.append(year)
                        # 將月寫入data_year_mounth
                        data_year_mounth.append(mounth)
                        all_data.append(data_year_mounth)
                        mounth += 3
                        continue
                except:
                    vpn(block_time)
                    print("我們被擋了")
                    continue



            data_year_mounth.append(tick)

            #將年寫入data_year_mounth
            data_year_mounth.append(year)

            # 將月寫入data_year_mounth
            data_year_mounth.append(mounth)

            datas = get_data_page()

            for data in datas:
                information = data.select("td")[1].text.replace(" ", "").replace("\xa0", "")

                #將information 合併到data_year_mounth
                data_year_mounth.append(information)

            with open(write_to_csv_name, "a", newline="\n") as f:
                print(data_year_mounth)
                writer = csv.writer(f)
                writer.writerow(data_year_mounth)

            # 取完資料mouth+1 取下個月
            if year == 110 and mounth == 3:
                break

            mounth += 3
    start += 1
    re = pd.DataFrame({"remember": [start]}).to_csv("r2.csv")
    end -= 1
    print("remaining amount:", end)




