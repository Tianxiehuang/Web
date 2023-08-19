from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import traceback
import time
import re
import os

def click_next_page(current_page,browser):
    # 等待“下一页”元素可见
    next_button_xpath = f'//a[@aria-label="第 {current_page} 页"]'
    next_button = WebDriverWait(browser, 10).until(EC.presence_of_element_located((By.XPATH, next_button_xpath)))
    # 点击“下一页”按钮
    next_button.click()
    
def search(keyword,num_of_results):
    # 预处理
    options = webdriver.ChromeOptions()

    # 处理SSL证书错误问题
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')

    # 忽略无用的日志
    options.add_experimental_option("excludeSwitches", ['enable-automation', 'enable-logging'])
    
    # 加上less选项，不显示浏览器窗口
    options.add_argument('--headless')

    chromedriver_path = 'C:/Users/DELL/AppData/Local/Google/Chrome/Application/chromedriver.exe'
    service = Service(chromedriver_path)
    browser = webdriver.Chrome(service=service, options=options)
    # 打开搜索引擎页面并搜索关键字
    url = f'https://www.bing.com/search?q={keyword}'
    #url = f'https://www.google.com/search?q={keyword}'
    browser.get(url)
    current_page = 1
    # 返回内容
    urls = []
    # 循环点击“下一页”按钮并获取搜索结果链接
    while len(urls) < num_of_results:
        try:
            # 等待一段时间，以便页面加载完成
            time.sleep(3)
            # 获取所有搜索结果的链接
            html = browser.page_source
            soup = BeautifulSoup(html,'html.parser')
            result_links = soup.select("h2 a")
            # 打印所有链接
            cnt = 0
            for link in result_links:
                href = link['href']
                print(href)
                # 如果链接不在urls中，则将其添加到urls列表中
                if href not in urls:
                    urls.append(href)
                else:
                # 如果高度重合,说明到达尽头
                    cnt += 1
                # 如果urls中的链接数量达到了需要返回的链接数，则退出循环
                if len(urls) >= num_of_results:
                    break
                # 如果高度重合
            if (cnt>=9):
                break

            current_page = current_page + 1
            # 点击“下一页”按钮
            try:
                click_next_page(current_page,browser)
            except Exception as e:
                print(f"Failed to click next page on page {current_page}. Error message: {e}")
                traceback.print_exc()
                break

        except Exception as e:
            print(f"Failed to get search results on page {current_page}. Error message: {e}")
            traceback.print_exc()
            break

    # 关闭浏览器
    browser.quit()
    return urls


# 读取word_path中的所有词汇
word_path = r'word.txt'
with open(word_path, 'r', encoding='utf-8') as f:
    words = [line.strip() for line in f.readlines()]
print(words)
# 设置返回结果数和内容
num_of_results = 15
result_urls = []

for word in words:
    
    result_urls.extend(search(word,num_of_results))

result_urls = list(set(result_urls))
# 打印链接列表
#url_path = r'C:\Users\lenovo\Desktop\Data-Task\English_web.txt'
url_path = 'real_web.txt'
with open(url_path, "w", encoding='utf-8') as f:
    for url in result_urls:
    
        f.write(url + '\n')
        
print(f'{len(result_urls)} links have been returned.')
