# -*- coding:utf-8 -*-
from urllib.request import urlopen
from requests.exceptions import RequestException
from bs4 import BeautifulSoup
from time import sleep
import csv
import json
# import pymongo

def get_all_distribution(baseURL):
    html = urlopen(baseURL+r'/zufang/')
    soup = BeautifulSoup(html,'lxml')
    divs = soup.find(class_="option-list").find_all('a')
    dic = {}
    for item in divs[1:-2]:
        dic[item.text] = item['href']
    return dic

def get_all_links_in_a_distribution(dis, baseURL, url):
    html = urlopen(baseURL+url)
    soup = BeautifulSoup(html,'lxml')
    divs = soup.find(class_="option-list sub-option-list").find_all('a')
    dic = {}
    for item in divs[1:]:
        key = dis + '-' + item.text
        dic[key] = baseURL + item['href']
    return dic

def get_all_links(baseurl):
    distribution = get_all_distribution(baseurl)
    dic = {}
    for item in distribution.items():
        dic.update(get_all_links_in_a_distribution(item[0], baseurl, item[1]))
    return dic

def save_links(data, outformat='json', filename='./links'):
    with open(filename+'.'+outformat,'w') as outfile:
        outfile.write(json.dumps(data))
    print("write OK:"+filename+'.'+outformat)
        
def load_links(informat='json', filename='./links'):
    with open(filename+'.'+informat,'r') as infile:
        data = json.loads(infile.read())
    print("load OK:"+filename+'.'+informat)
    return data

def get_pages(url, id):
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find(class_="house-lst-page-box")['page-data']
    pages = pages.split(':')[1].split(',')
    pages_num = pages[0]
    return pages_num

def parse_one_page(url, id):
    print(url)
    html = urlopen(url)
    soup = BeautifulSoup(html, 'lxml')
    for item in soup.select('.info-panel'):
        try:
            houseUrl = item.find("h2").a["href"]
            title = item.find("h2").a["title"]
            spans = item.find(class_="where").find_all("span")
            # region, zone, meters = spans.find(class_="region").text, spans.find(class_="zone").text, spans.find(class_="meters").text
            region, zone, meters = spans[0].text.split('\xa0')[0], spans[1].text.split('\xa0')[0], spans[3].text.split('\xa0')[0]
            # cons = item.find(class_="con").find_all("a")
            # area, sub_area = cons[0].string, cons[1].string
            # subway = item.find(class_="fang-subway-ex").string
            price = item.find(class_="price").find(class_="num").text
            date = item.find(class_="price-pre").string.split()[0]
            watched = item.find(class_="square").find(class_="num").string
            id += 1
            yield {
                'id': id,
                'houseUrl': houseUrl,
                'houseDescription': title,
                'region': region,
                'zone': zone,
                'meters': meters,
                # 'area': area,
                # 'sub_area': sub_area,
                # 'traffic': subway,
                'price': price,
                'date': date,
                'watchedPersons': watched
            }
        except:
            continue

def crawl(links):
    index = 0
    for link in links.items():
        try:
            pages_num = get_pages(link[1], index)
        except:
            continue
        for i in range(1,int(pages_num)+1):
            if i>=2:
                url = link[1]+'/pg' + str(i)
            else:
                url = link[1]
            try:
                info = parse_one_page(url, index)
                for item in info:
                    print(item)
            except:
                continue

if __name__ == '__main__':
    # client = pymongo.MongoClient('mongodb://localhost:27017')
    # db_name = 'lianjia_zufang_shanghai'
    # db = client[db_name]
    # collection_set01 = db['set01']
    # index = 0
    # for page in range(100):
    #     sleep(1)
    #     url = 'https://bj.lianjia.com/zufang/pg' + str(page)
    #     html = urlopen(url)
    #     # html = get_one_page(url)
    #     for item, index in parse_one_page(html, index):
    #         print(item)
    #         # collection_set01.save(item)
    
    # baseURL = 'https://bj.lianjia.com'
    # links = get_all_links(baseURL)
    # save_links(links)
    links = load_links()
    crawl(links)