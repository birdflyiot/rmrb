#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# __author__ = 'bird'
# 作用：获取近一周人民日报所有文章，人民日报地址：http://paper.people.com.cn/
# 时间：2017年3月19日16:09:09


from bs4 import BeautifulSoup
from datetime import datetime
from datetime import timedelta
import requests
import traceback
import csv
import time
import re


# def get_time(days):
#     return datetime.now() - timedelta(days= days)


def get_original_time(original_times):
    # 用time.strptime(original_time,"%Y-%m-%d")获得的是timestruct类型的，
    # 不是下面original_time - timedelta(days= period)所需的timedate类型的，
    # 所以用datetime.strptime(original_time, "%Y-%m-%d")
    original_times = datetime.strptime(original_times, "%Y-%m-%d")
    return original_times


def get_previous_time(original_times, p):
    previous_times = str(original_times - timedelta(days= p))
    # 获取适合人民日报网址的时间2017-02/17
    previous_times = previous_times[0:7] + '/' + previous_times[8:10]
    return previous_times


def get_tittle_time(original_times,p):
    tittle_times = str(original_times - timedelta(days= p))
    tittle_times = tittle_times[0:4] + tittle_times[5:7] + tittle_times[8:10]
    return tittle_times


def get_previous_url(previous_times):
    # 网址类型为http://paper.people.com.cn/rmrb/html/2017-03/19/node_1921.html 每一期版面导航地址
    previous_urls = 'http://paper.people.com.cn/rmrb/html/{}/node_1921.htm'.format(previous_times)
    return previous_urls


def get_tittle_url(tittle_times):
    # 网址类型为http://58.68.146.102/rmrb/20010302/1
    tittle_urls = "http://58.68.146.102/rmrb/{}/1".format(tittle_times)
    return tittle_urls


def get_news_text(news_urls):
    news = ''
    try:
        news_html = requests.get(news_urls,timeout = 20)
        news_html.raise_for_status()
        soup = BeautifulSoup(news_html.text,'html.parser')
        # news_text = soup.find('div',id = 'FontZoom')
        news_text = soup.find_all('p')
        for item in news_text:
             news += str(item.string)
        #print(news_text)
    except:
        traceback.print_exc()
        news = "无法获得新闻内容，可能是一周前的新闻，暂不支持查询"
    return news


def get_future_time(original, p1):
    return ''


def csv_create(filenames,columns):
    # 创建CSV文件
    with open(filenames, "a+", newline="") as datacsv:
        # dialect为打开csv文件的方式，默认是excel，delimiter="\t"参数指写入的时候的分隔符
        csvwriter = csv.writer(datacsv, dialect=("excel"))
        # csv文件插入一行数据，把下面列表中的每一项放入一个单元格（可以用循环插入多行）
        csvwriter.writerow(columns)


def csv_write(filenames,rows):
    with open(filenames, 'a+', newline='', encoding='gb18030') as datacsv:
        csvwriter = csv.writer(datacsv, dialect=("excel"))
        csvwriter.writerow(rows)


if __name__ == '__main__':
    # original_time = str(input('请输入起始日期（如2017-03-19）：'))
    # period = int(input('请输入获取起始日期之前多少期数（输入1则为当期）:'))
    # original_time = get_original_time(original_time)
    #
    # n = 0
    # while n < period:
    #     # previous_time = get_time(int(n))
    #     # print(str(previous_time)[0:10])
    #     previous_time = get_previous_time(original_time,n)
    #     previous_url = get_previous_url(previous_time)
    #     print(previous_url)
    #     n += 1

    today = datetime.today() - timedelta(days= 1)
    # print(str(today)[0:10])
    tips = '请输入起始日期，如{}（无法获取今天的）：'.format(str(today)[0:10])
    original_time = str(input(tips))
    period = int(input('请输入获取起始日期之前多少期数（输入1则为当期）:'))
    original_time = get_original_time(original_time)


    n = 0
    while n < period:
        # previous_time = get_time(int(n))
        # print(str(previous_time)[0:10])
        previous_time = get_tittle_time(original_time,n)
        previous_url = get_tittle_url(previous_time)

        column = ['期数','版次','版面','标题','内容']

        try:
            r = requests.get(previous_url,timeout = 20)
            r.raise_for_status()
            demo = r.text
            soup = BeautifulSoup(demo, "html.parser")
            user_rmrb_page_num = soup.find(id="UseRmrbPageNum")
            tag_page_num = int(user_rmrb_page_num.string)

            filename = '第{}期报纸共{}版.csv'.format(previous_time, tag_page_num)
            print(filename)
            csv_create(filename, column)
        except:
            traceback.print_exc()
            continue

        while tag_page_num > 0 :
            page_url = "http://58.68.146.102/rmrb/{}/{}".format(previous_time,tag_page_num)
            time.sleep(1)
            try:
                r = requests.get(page_url,timeout = 20)
                r.raise_for_status()
                demo = r.text
                soup = BeautifulSoup(demo, "html.parser")
                page_tittle = soup.find('div', 'info') # 返回一个bs4的tag
                page_info = page_tittle.find_all('span')# 返回span的列表
                # print(page_info[1].string)# 返回列表第二个元素的字符串内容
                # date_and_tittle = [previous_time, tag_page_num,page_info[1].string]
                tittle_list = soup.ul.find_all('a')
                # print('第{}版标题如下'.format(tag_page_num))

                for tittle in tittle_list:
                    # date_and_tittle = [previous_time, tag_page_num, page_info[1].string]
                    # print(re.findall(r'href=\".*?\"',str(tittle))[0][6:-1])
                    news_url = "http://58.68.146.102" + re.findall(r'href=\".*?\"',str(tittle))[0][6:-1]
                    # print(news_url)
                    news = get_news_text(news_url)
                    date_tittle = list([previous_time,tag_page_num,page_info[1].string,tittle.string,news])  # 更规范的
                    print(date_tittle)
                    csv_write(filename, date_tittle)

            except:
                print('当前版面获取失败')
                traceback.print_exc()
            tag_page_num -= 1

        n += 1
