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


write_to_csv_name = "董監_1.csv"
read_file = "tick_name1.csv"



url = "https://mops.twse.com.tw/mops/web/stapap1"

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




#%%

driver1 = start_driver()
driver1.get("data:,")
#健力第二格視窗 給vpn介面
driver1.execute_script("window.open('chrome-extension://gjknjjomckknofjidppipffbpoekiipm/panel/index.html')")
handles = driver1.window_handles

#選擇歷史資訊
def select_history():


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
        EC.presence_of_element_located((By.CSS_SELECTOR,"table.hasBorder tr.odd td")))

#獲取頁面資訊
def get_data_page():
    html = driver1.page_source
    soup = BeautifulSoup(html, "lxml")
    table = soup.select("table.noBorder")

    table2 = soup.select("table.hasBorder")[0]
    rows = table2.select("tr:not(.tblHead)")
    return table , rows


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
            driver1.find_element_by_css_selector("div.main__button-group button").click()
            time.sleep(2)
            driver1.switch_to.window(handles[0])
    except:
        driver1.quit()


all_data =[]

tick_name = pd.read_csv(read_file)

tick_name =tick_name["tick_name"]



start = 0


columns = ["tick_name","year","mounth","非獨立董事持股設質比例","獨立董事持股設質比例","非獨立監察人持股設質比例","獨立監察人持股設質比例","全體董監持股合計","非獨立董監持股設質比例","獨立董監持股設質比例","全體董監持股設質比例","大股東股數"]



#檢查上次爬到的位置
try:
    start_point = pd.read_csv("r1.csv")
    start_point = start_point["remember"]
    start = start_point.values[0]
    print("start:" , start)
except:
    print("start 0")

#如果是第一次啟動 建立一個csv儲存爬到的位置
if start == 0:
    with open(write_to_csv_name, "a", newline="\n") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
else:
    pass
    
    
    
end = len(tick_name[start:len(tick_name)])
block_time = 0

for tick in tick_name[start:len(tick_name)]:
    print(tick)

    for year in range(90, 111):
        # 寫入要的年份
        mounth = 3
        # 因為怕被擋所以用while迴圈,如果被擋月數不會繼續,直到抓到資料
        while mounth <= 12:
            
            #如果網頁意外結束 重新啟動網頁
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

            data_year_mounth = []
            # 嘗試去點頁面資訊 如果出錯代表被擋 掛載vpn
            
            try:
                select_history()
                send_year(year)
                send_mounth(mounth)

                # 寫入當前股價代號
                send_tick_name(tick)

                # 隨機暫停後點選查詢按鈕
                time.sleep(random.randint(1, 3))
                click_send_button()
            except:
                vpn(block_time)
                print("我們被擋了")
                continue



            try:
                #try 確認資料存再不,如果不存在，可能被檔，進except檢查是否被擋
                # time.sleep(1)
                check_is_ready()
            except:
                # time.sleep(1)

                d = driver1.page_source
                soup = BeautifulSoup(d,"lxml")
                try:
                    cc = soup.select("div#zoom h2")[0]
                    #檢查是否是資料庫無資料
                    if cc.text == "資料庫中查無資料 !":
                        print(cc.text)
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
            datas , rows = get_data_page()

            data_year_mounth.append(str(tick))

            #將年寫入data_year_mounth
            data_year_mounth.append(str(year))

            # 將月寫入data_year_mounth
            data_year_mounth.append(str(mounth))


            for number , data in enumerate(datas):
                checks = data.select("tr td")[0].text
                if checks == "非獨立董事持股合計":
                    for number ,i in enumerate(data.select("tr")) :
                        information = i.select("td")[7]
                        data_year_mounth.append(information.text)

                        if number == 6 :
                            other = i.select("td")[1].text.replace(" ","")

                            data_year_mounth.append(other)
            count = 1
            t = 0
            for row in rows:
                row_data = row.select("td")

                if row_data[0].text == "大股東本人":
                    big = row_data[3].text.replace(" ","")
                    t += int(big.replace(",",""))
            data_year_mounth.append(str(t))

            with open(write_to_csv_name ,"a",newline="\n") as f :
                print(data_year_mounth)
                writer = csv.writer(f)
                writer.writerow(data_year_mounth)

            if year == 110 and mounth == 3:
                break
            mounth += 3
    start += 1
    re = pd.DataFrame({"remember":[start]}).to_csv("r1.csv")
    end -= 1
    print("remaining amount:",end)

