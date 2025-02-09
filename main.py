import os
import json
import time

import selenium
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import argparse


def scroll(driver, max_comments=1000):
    # 向下滚直到加载完所有评论或者达到最大数量
    driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
    time.sleep(2)
    
    last_comments_count = 0

    while True:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        
        comments_area_shadow_root = comments_area.shadow_root
        comment_thread_renderers = WebDriverWait(driver, 5).until(
            lambda driver: comments_area_shadow_root.find_elements(By.CSS_SELECTOR, 'bili-comment-thread-renderer')
        )
        current_comments_count = len(comment_thread_renderers)
        print(f'当前评论数：{current_comments_count}')
        
        if current_comments_count == last_comments_count:
            print('全部评论加载完毕')
            break
        
        if current_comments_count >= max_comments:
            print('达到最大评论数')
            break
        
        last_comments_count = current_comments_count
        
        time.sleep(2)




def save(comment_contents, vd, format='xlsx'):
    path = f'./results/{vd}.{format}'
    df = pd.DataFrame(comment_contents, columns=['评论', '点赞数'])
    if format == 'xlsx':
        df.to_excel(path, index=False)
        print(f'视频{vd}的评论已保存至{path}')
    
    if format == 'csv':
        df.to_csv(path, index=False)
        print(f'视频{vd}的评论已保存至{path}')




with open('config.json', 'r') as file:
    config = json.load(file)



parser = argparse.ArgumentParser()

parser.add_argument('--format', choices=['xlsx', 'csv'], default='xlsx', required=False, help='保存评论的格式')

args = parser.parse_args()



os.environ['NO_PROXY'] = '*'
service = Service(executable_path=config['driver_path'])
driver = webdriver.Chrome(service=service)


driver.get('https://www.bilibili.com/')


# 写cookie
driver.delete_all_cookies()
with open('jsoncookie.json', 'r') as f:
    ListCookies = json.loads(f.read())

for cookie in ListCookies:
    driver.add_cookie({
        'domain': '.bilibili.com',
        'name': cookie['name'],
        'value': cookie['value'],
        'path': '/',
        'expires': None,
        'httponly': False,
    })
    
driver.refresh()


for vd in config['vd_list']:
    driver.get(f'https://bilibili.com/video/{vd}')
    # shadow-root
    comments_area = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'bili-comments'))
    )
    
    # 向下滚直到加载完所有评论或者达到最大数量
    scroll(driver, config['max_count'])
    
    # 提取shadow-root
    comments_area_shadow_root = comments_area.shadow_root
    
    comment_thread_renderers = WebDriverWait(driver, 5).until(
        lambda driver: comments_area_shadow_root.find_elements(By.CSS_SELECTOR, 'bili-comment-thread-renderer')
    )

    # def wait_for_non_empty_comment_thread_renderers(driver):
    #     elements = comments_area_shadow_root.find_elements(By.CSS_SELECTOR, 'bili-comment-thread-renderer')
    #     return elements if len(elements) > 0 else False
    # comment_thread_renderers = WebDriverWait(driver, 5).until(wait_for_non_empty_comment_thread_renderers)

        
    if len(comment_thread_renderers) == 0:
        raise Exception('爬取评论区出错或者评论区为空')    
    
    comment_contents = []
    for comment_thread_renderer in comment_thread_renderers:
        # 提取shadow-root
        comment_thread_renderer_shadow_root = comment_thread_renderer.shadow_root
        # 一级评论，shadow-root
        comment_renderer_shadow_root = comment_thread_renderer_shadow_root.find_element(By.CSS_SELECTOR, "bili-comment-renderer") 
        # 提取一级评论的shadow-root
        comment_renderer_shadow_root_shadow_root = comment_renderer_shadow_root.shadow_root
        
        # 评论正文element
        comment_content = comment_renderer_shadow_root_shadow_root.find_element(By.ID, 'content')
        
        # 脚注（点赞量等），shadow-root
        comment_action_buttons_renderer = comment_renderer_shadow_root_shadow_root.find_element(By.CSS_SELECTOR, 'bili-comment-action-buttons-renderer')
        comment_action_buttons_renderer_shadow_root = comment_action_buttons_renderer.shadow_root
        # 点赞量element
        likes = comment_action_buttons_renderer_shadow_root.find_element(By.ID, 'count')
        
        # print((comment_content.text, likes.text))
        
        if likes.text == '':
            likes = 0
        else:
            likes = int(likes.text)
        
        # print(comment_content.text)
        comment_contents.append((comment_content.text, likes))
    
    
    save(comment_contents, vd, format=args.format)
    

driver.close()

