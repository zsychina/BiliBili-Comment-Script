import os
import json
import time
import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


with open('config.json', 'r') as file:
    config = json.load(file)


os.environ['NO_PROXY'] = '*'
service = Service(executable_path=config['driver_path'])
driver = webdriver.Chrome(service=service)


# 第一次登陆
driver.get('https://www.bilibili.com/')


driver.implicitly_wait(10)
input('第一次登陆完成？如果登陆完成请按回车键：')

dictcookie = driver.get_cookies()
# print(f'{dictcookie}')

jsoncookie = json.dumps(dictcookie)
# print(f'{jsoncookie}')

with open('jsoncookie.json','w') as f:
    f.write(jsoncookie)
    

driver.close()



