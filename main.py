import base64
import requests
import xlwt
import time
import os
import binascii

from selenium import webdriver

import task

from io import BytesIO
from PIL import Image
import shutil
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By


if __name__ == "__main__":
    urls = []
    with open('./resource/urls.txt', 'r', encoding='utf8') as f:
        urls = f.readlines()
    urls = [url[:-1] for url in urls]

    dir_path = "./tmp"
    # 创建驱动
    path_to_edge_driver = 'C:/Program Files (x86)/Microsoft/Edge/Application/msedgedriver.exe'
    driver = webdriver.Edge()
    driver.maximize_window()
    headers = {"Connection": "close"}

    m = 0
    times = 0
    for url in urls:
        times = times+1
        print("This is " + url)

        pic = xlwt.Workbook(encoding='utf-8', style_compression=0)
        sheet = pic.add_sheet('广告收集', cell_overwrite_ok=True)
        sheet.write(0, 0, 'src')
        sheet.write(0, 1, 'pos_x')
        sheet.write(0, 2, 'pos_y')
        sheet.write(0, 3, 'size_x')
        sheet.write(0, 4, 'size_y')
        sheet.write(0, 5, '广告种类')
        sheet.write(0, 6, '亮度')
        sheet.write(0, 7, '饱和度')
        sheet.write(0, 8, '来源')
        sheet.write(0, 9, '图片总量')
        sheet.write(0, 10, '页面总面积')
        sheet.write(0, 11, '文字')
        sheet.write(0, 12, "minmax")
        sheet.write(0, 18, "颜色种类数")
        sheet.write(0, 19, "最大颜色数量占据的比例")
        sheet.write(0, 20, "最大颜色RGB值")

        n = 1
        m = m + 1
        try:
            driver.get(url)
            # 获取页面初始高度
            initial_height = driver.execute_script("return document.body.scrollHeight")

            # 模拟滚动操作
            while True:
                # 执行滚动操作
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                # 等待页面加载
                time.sleep(1)
                # 获取滚动后的高度
                new_height = driver.execute_script("return document.body.scrollHeight")
                # 判断是否到达页面底部
                if new_height == initial_height:
                    break
                # 更新页面初始高度
                initial_height = new_height

            # 获取页面总面积
            total_area = driver.execute_script("return document.body.scrollWidth * document.body.scrollHeight")
        except Exception as e:
            print("driver get error")

        img_elements = driver.find_elements(By.TAG_NAME, "img")

        length = len(img_elements)

        for img in img_elements:
            try:
                src = img.get_attribute('data-url') or img.get_attribute('src')
            except WebDriverException as e:
                print(f"Failed to get source attribute for image {img}. Reason: {e}")
                continue
            pos_x = img.location.get('x')
            pos_y = img.location.get('y')
            size_x, size_y = img.size.values()
            print(">>>siz1")
            print(size_x, size_y)

            if (pos_x == 0 and pos_y == 0) or (src is None) or ('///' in src):
                continue
            print(src)
            if "base64" in src:
                src = src.split(',')[-1]
                try:
                    img_binary = base64.b64decode(src)
                except binascii.Error as e:
                    print("图片解码错误: ", str(e))
                    continue
                with open(dir_path + '\\' + str(n) + '.jpg', 'wb') as f:
                    f.write(img_binary)
            elif '.jpg' in src or '.gif' in src or '.webp' in src:
                try:
                    response = requests.get(src)
                    if '.gif' in src or '.webp' in src:
                        # 将 GIF 文件转换为 PIL.Image 对象
                        img = Image.open(BytesIO(response.content))
                        # 将 PIL.Image 对象转换为 JPG格式
                        img = img.convert('RGB')
                        # 保存 JPG 文件到本地
                        img.save(dir_path + '\\' + str(n) + '.jpg', 'JPEG')
                    elif '.jpg' in src:
                        with open(dir_path + '\\' + str(n) + '.jpg', 'wb') as f:
                            f.write(response.content)
                    else:
                        continue
                except Exception as e:
                        print("get error")
            else:
                continue

            test_path = os.path.abspath(dir_path + "\\" + str(n) + '.jpg')
            ans = task.complete_evaluate(test_path)
            if ans is None:
                continue
            else:
                print(ans)
            flag = ans[0]
            kind = -1
            if flag:
                for i in range(1, 4):
                    if ans[i] == 1:
                        kind = i
                        break
            word = ans[4]
            size_y, size_x, brightness, saturation, minmax, numcolor, ratio, rgb = task.get_information(test_path)
            print(">>>siz2")
            print(size_x, size_y)

            # 判断是否为广告和其种类
            pos_x = (pos_x + size_x / 2) / 2880
            pos_y = ((pos_y % 1080) + size_y / 2) / 1800

            try:
                sheet.write(n, 0, src)
                sheet.write(n, 1, pos_x)
                sheet.write(n, 2, pos_y)
                sheet.write(n, 3, size_x)
                sheet.write(n, 4, size_y)
                sheet.write(n, 5, kind)
                sheet.write(n, 6, brightness)
                sheet.write(n, 7, saturation)
                sheet.write(n, 8, url)
                sheet.write(n, 9, length)
                sheet.write(n, 10, total_area)
                sheet.write(n, 11, word)
                sheet.write(n, 12, minmax[0])
                sheet.write(n, 13, minmax[1])
                sheet.write(n, 14, minmax[2][0])
                sheet.write(n, 15, minmax[2][1])
                sheet.write(n, 16, minmax[3][0])
                sheet.write(n, 17, minmax[3][1])
                sheet.write(n, 18, numcolor)
                sheet.write(n, 19, ratio)

                R = int(rgb[0])
                G = int(rgb[1])
                B = int(rgb[2])
                sheet.write(n, 20, R)
                sheet.write(n, 21, G)
                sheet.write(n, 22, B)
            except Exception as e:
                print("write execl error")

            n = n + 1

        try:
            # pic.save(u'./pic'+str(-m)+'.xls')
            pic.save('./out/pic' + str(-m) + '.xls')
            # D:\core\web\son-project\data\data\Chinese_web
        except Exception as e:
            print("Excel 文件写入错误: ", str(e))

        # Clean all temp files
        for filename in os.listdir(dir_path):
            file_path = os.path.join(dir_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f"Failed to delete {file_path}. Reason: {e}")

