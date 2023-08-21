from cnocr import CnOcr
import easyocr
import cv2
import os
import numpy as np
from fuzzywuzzy import fuzz


# 以下全部为基础准备工作，调入各种文件,注意修改你的路径名
gameword_path = os.path.abspath(r"resource\word\gamingword.txt")
yellowword_path = os.path.abspath(r"resource\word\yellowword.txt")
otherword_path = os.path.abspath(r"resource\word\otherword.txt")
reader = easyocr.Reader(['ch_sim'])

with open(gameword_path, "r", encoding='utf-8') as f:
    gamewordlist = f.readlines()
gamewordlist = [word.strip() for word in gamewordlist]

with open(yellowword_path, "r", encoding='utf-8') as f:
    yellowwordlist = f.readlines()
yellowwordlist = [word.strip() for word in yellowwordlist]

with open(otherword_path, "r", encoding='utf-8') as f:
    otherwordlist = f.readlines()
otherwordlist = [word.strip() for word in otherwordlist]


def ocrcheck(test_path):
    """
    test_path是项目的地址,输入这个地址就可以调用此函数
    返回值有两个:ad_check,判断是不是广告,如果是的话返回1,否则0
    第二个:所有较为清晰可识别的文字,将其合并返回
    """
    ocr = CnOcr(rec_model_name='ch_PP-OCRv3')  # 所有参数都使用默认值
    out = ocr.ocr(test_path)
    game_check = 0
    yellow_check = 0
    other_check = 0
    ad_check = 0
    txt = ''
    # 0 is non and 1 is ads
    # txt is the all text in the pic
    for item in out:
        if item['score'] >= 0.5:
            txt += item["text"].strip() + '###'       
            for word in gamewordlist:
                similarity1 = fuzz.token_set_ratio(item['text'], word)
                similarity2 = fuzz.partial_ratio(item['text'], word)
                similarity3 = fuzz.token_sort_ratio(item['text'], word)
                if similarity1 >= 40 or similarity3 >= 40 or similarity2 >= 40:
                    # print('####',True,item['text'], item['score'], word,similarity1,similarity2,similarity3,'####')
                    game_check = 1
                    break
            for word in yellowwordlist:
                similarity1 = fuzz.token_set_ratio(item['text'], word)
                similarity2 = fuzz.partial_ratio(item['text'], word)
                similarity3 = fuzz.token_sort_ratio(item['text'], word)
                if similarity1 >= 40 or similarity3 >= 40 or similarity2 >= 40:
                    # print('####',True,item['text'], item['score'], word,similarity1,similarity2,similarity3,'####')
                    yellow_check = 1
                    break
            for word in otherwordlist:
                similarity1 = fuzz.token_set_ratio(item['text'], word)
                similarity2 = fuzz.partial_ratio(item['text'], word)
                similarity3 = fuzz.token_sort_ratio(item['text'], word)
                if similarity1 >= 40 or similarity3 >= 40 or similarity2 >= 40:
                    # print('####',True,item['text'], item['score'], word,similarity1,similarity2,similarity3,'####')
                    other_check = 1
                    break
            ad_check = yellow_check + game_check + other_check
            if ad_check > 1:
                ad_check = 1
    if txt == '':
        result = reader.readtext(test_path)
        for item in result:
            if item[2] >= 0.01:
                txt += item[1].strip() + '###'   
                for word in gamewordlist:
                    similarity1 = fuzz.token_set_ratio(item[1], word)
                    similarity2 = fuzz.partial_ratio(item[1], word)
                    similarity3 = fuzz.token_sort_ratio(item[1], word)
                    if similarity1 >= 40 or similarity3 >= 40 or similarity2 >= 40:
                        game_check = 1
                        break
                for word in yellowwordlist:
                    similarity1 = fuzz.token_set_ratio(item[1], word)
                    similarity2 = fuzz.partial_ratio(item[1], word)
                    similarity3 = fuzz.token_sort_ratio(item[1], word)
                    if similarity1 >= 40 or similarity3 >= 40 or similarity2 >= 40:
                        yellow_check = 1
                        break
                for word in otherwordlist:
                    similarity1 = fuzz.token_set_ratio(item[1], word)
                    similarity2 = fuzz.partial_ratio(item[1], word)
                    similarity3 = fuzz.token_sort_ratio(item[1], word)
                    if similarity1 >= 40 or similarity3 >= 40 or similarity2 >= 40:
                        other_check = 1
                        break
        # for item in out:
        #     if item['score']>=0.1:   
        #         txt += item["text"].strip() + '###'       
        #         for word in gamewordlist:
        #             similarity1 = fuzz.token_set_ratio(item['text'], word)
        #             similarity2 = fuzz.partial_ratio(item['text'], word)
        #             similarity3 = fuzz.token_sort_ratio(item['text'], word)
        #             if similarity1 >= 60 or similarity3 >= 60 or similarity2 >=70:
        #                 #print('####',True,item['text'], item['score'], word,similarity1,similarity2,similarity3,'####')
        #                 game_check = 1
        #                 break
        #         for word in yellowwordlist:
        #             similarity1 = fuzz.token_set_ratio(item['text'], word)
        #             similarity2 = fuzz.partial_ratio(item['text'], word)
        #             similarity3 = fuzz.token_sort_ratio(item['text'], word)
        #             if similarity1 >= 60 or similarity3 >= 60 or similarity2 >=70:
        #                 #print('####',True,item['text'], item['score'], word,similarity1,similarity2,similarity3,'####')
        #                 yellow_check = 1
        #                 break
        #         for word in otherwordlist:
        #             similarity1 = fuzz.token_set_ratio(item['text'], word)
        #             similarity2 = fuzz.partial_ratio(item['text'], word)
        #             similarity3 = fuzz.token_sort_ratio(item['text'], word)
        #             if similarity1 >= 60 or similarity3 >= 60 or similarity2 >=70:
        #                 #print('####',True,item['text'], item['score'], word,similarity1,similarity2,similarity3,'####')
        #                 other_check = 1
        #                 break
        #         ad_check = yellow_check + game_check + other_check
        #         if (ad_check>1):
        #             ad_check = 1
    return ad_check, game_check, other_check, yellow_check, txt


def complete_evaluate(test_path):
    """_summary_
    输出五元组:a:是否为广告
    b、c、d:gaming、regular、yellow是哪一种广告
    txt:广告里的文字
    """
    try:
        a, b, c, d, txt = ocrcheck(test_path)
        # e = cnn_evaluate(test_path).item()
        e = 1
        if a == 1:
            if b == 1 and e == 0:  # 赌博
                return 1, 1, 0, 0, txt
            elif c == 1 and e == 1:  # 常规
                return 1, 0, 1, 0, txt
            elif d == 1 and e == 2:   # 色情
                return 1, 0, 0, 0, txt
        # if ( e==0):  #赌博
        #     return 1,1,0,0,txt
        # elif (e==1):  #常规
        #     return 1,0,1,0,txt
        # elif (e==2):   #色情
        #     return 1,0,0,0,txt
        # else:
        #     return 0,0,0,0,txt
    except Exception as e:
        # 处理异常并输出错误信息
        print("An error occurred:", e)
        return 0, 0, 0, 0, ''  # 或者返回其他合适的值


def get_information(test_path):
    """
    test_path是图片路径
    打印很多东西,你看哪些有用就留下来
    """
    try:
        img = cv2.imread(test_path)
        if img is None:
            print("读取图片失败：无法解码图片文件或图片文件不存在")
            return 0, 0, 0, 0
        height, width, channels = img.shape
    except Exception as e:
        print(f"读取图片失败：{e}")
        height = 0
        width = 0
    
    # 获取图片亮度
    try:
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        brightness = cv2.mean(gray_img)[0]/255
    except Exception as e:
        print(f"获取图片亮度失败：{e}")
        brightness = 0
        
    # 获取图片饱和度
    try:
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        saturation = hsv[..., 1].mean()/255
    except Exception as e:
        print(f"获取图片饱和度失败：{e}")
        saturation = 0
    # 获取图片最小和最大像素
    try:
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        minmax = cv2.minMaxLoc(gray_img)
        
    except Exception as e:
        print(f"获取图片最小最大像素失败：{e}")
        minmax = (-1, -1, (-1, -1), (-1, -1))

    try:
        # 将图像转换为 RGB 格式
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # 将图像转换为一维数组
        pixels = image_rgb.reshape(-1, 3)

        # 使用 numpy.unique 函数获取颜色种类和对应的像素数量
        colors, counts = np.unique(pixels, axis=0, return_counts=True)
        numcolors = len(colors)
        # 找到数量最多的颜色值
        max_count_index = np.argmax(counts)
        most_common_color = colors[max_count_index]
        most_common_count = counts[max_count_index]

        # 计算最多颜色所占的比例
        total_pixels = pixels.shape[0]
        most_common_ratio = most_common_count / total_pixels
    except Exception as e:
        print(f"获取图片颜色种类失败：{e}")
        numcolors = -1
        most_common_ratio = -1
        most_common_color = -1
    return height, width, brightness, saturation, minmax, numcolors, most_common_ratio, most_common_color
