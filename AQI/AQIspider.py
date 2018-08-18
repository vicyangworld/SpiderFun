# -*- coding: utf-8 -*-

from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import csv
import os
import json
from toDataBase import fetch_db
import datetime

def get_date_begin_end(dbName):
    command = "SELECT * FROM Date"
    args = None
    allData = fetch_db(dbName, command, args)
    allData.sort()
    return allData[0],allData[-1]

class AQIspider:
    def __init__(self):

        self.baseURL  = "http://www.tianqihoubao.com"
        self.dataList = []
        self.cityDic = {}
        self.subLink = "/aqi/"
        self.__dbName = "AQI.db" 
        _, self.__lastDateInDB = get_date_begin_end(self.__dbName)
        self.__update = False


    def __get_city_contents_recurise__(self, city, provinceName):
        try:
            cityName = city.get_text().split()
            if len(cityName) == 1:
                cname = ''.join(cityName)
                clink = ''.join(city['href'].split())
                if provinceName == r"直辖市" and (cname not in ['北京','天津','上海', '重庆']):
                    return
                if len(clink.split('_')) != 1:
                    print(clink.split('_'))
                    return
                self.cityDic[provinceName + "-" + cname] = clink
                print("get OK: " + provinceName + " " + clink)
                return
            else:
                for acity in city.contents:
                    self.__get_city_contents_recurise__(acity, provinceName)
        except:
            return None

    def get_all_city_links(self):
        allCityUrl = self.baseURL+self.subLink
        try:
            html = urlopen(allCityUrl)
        except:
            print("ERROR: open " + allCityUrl + " is invalid!")
            os._exit(0)
        soup = BeautifulSoup(html, 'lxml')
        allLinks = soup.find_all('dl')
        self.cityDic = {}
        provinceName = ""
        for province in allLinks:
            if province.contents != None:
                for provinceContentsItem in province.contents:
                    if provinceContentsItem.name == 'dt':
                        provinceName = provinceContentsItem.get_text()
                        if provinceName == r"热门城市":
                            provinceName = r"直辖市"
                    if provinceContentsItem.name == 'dd':
                        for city in provinceContentsItem.contents:
                            self.__get_city_contents_recurise__(city,provinceName)
                           
    def save_all_city_links(self, outformat='json', filename='./city_name_link'):
        with open(filename+'.'+outformat,'w') as outfile:
            outfile.write(json.dumps(self.cityDic))

        print("write OK:"+filename+'.'+outformat)
            
    def load_all_city_links(self, informat='json', filename='./city_name_link'):
        with open(filename+'.'+informat,'r') as infile:
            self.cityDic = json.loads(infile.read())

        print("load OK:"+filename+'.'+informat)

    def __getdata__(self, url, cityName, withHead=False):
        """ get data from website url """
        html=urlopen(url)
        soup=BeautifulSoup(html,"lxml")
        tablelist=soup.findAll("tr") # get all tables
        if withHead:
            tablehead=tablelist[0].get_text().strip("\n").split("\n\n")
            self.dataList.append(tablehead) # table head

        for datalist in tablelist[1:]:
            data = [x for x in datalist.get_text().split() if x!='']
            if self.__update and data[0] <= self.__lastDateInDB[0]:
                continue
            self.dataList.append(data)
            print(cityName, data)

    def __crawl_a_city__(self, url, city_zh, toSave, outFilename):
        self.dataList = [] 
        try:
            html=urlopen(url)
        except:
            print("ERROR: wrong input city name or the website " + url + " is invalid!")
            os._exit(0)

        cityName = url.split('/')[-1].split('.')[0]
        soup=BeautifulSoup(html,"lxml")
        # find all links
        Sites=[]
        if self.__update:
            re_str = "^("+self.subLink+str(cityName)+"-"+''.join(self.__lastDateInDB[0].split('-')[0:2])+")"  #get all history data link of this city
        else:
            re_str = "^("+self.subLink+str(cityName)+"-)" 

        for link in soup.findAll(href=re.compile(re_str)):
            site=self.baseURL+link.attrs['href']
            Sites.append(site)
        Sites.reverse()

        if not self.__update:
            self.__getdata__(Sites[0], city_zh, True)
            for url in Sites[1:]:
                self.__getdata__(url, city_zh)
        else:
            for url in Sites[0:]:
                self.__getdata__(url, city_zh)

        if toSave:
            csvfile=open(outFilename,"a+")
            try:
                writer=csv.writer(csvfile)
                for line in self.dataList:
                    if len(line):
                        writer.writerow(line)
            finally:
                csvfile.close()

    def crawl(self, toSave=True, savePath="./", city='', update=False): 
        """ get all data and save """ 
        self.__update = update
        if city != '':
            filenameDateset = os.path.join(savePath,"Dataset_"+str(city)+".csv")
            if os.path.exists(filenameDateset):
                return
            startURL = self.baseURL+self.subLink + city + '.html'
            
            self.__crawl_a_city__(startURL, city ,toSave, filenameDateset)
        else:
            if self.cityDic == {}:
                print("please load city links first by load_all_city_links(*)")
                os._exit(0)
            
            for item in self.cityDic.items():
                cityName = item[1].split('/')[-1].split('.')[0]
                print('crawling '+ item[0] + '......')
                savePathDataset = os.path.join(savePath, item[0].split('-')[0])
                if not os.path.exists(savePathDataset):
                    os.makedirs(savePathDataset)
                filenameDateset = os.path.join(savePathDataset,"Dataset_"+cityName+".csv")
                # if os.path.exists(filenameDateset):
                #     continue
                startURL = self.baseURL+item[1]
                self.__crawl_a_city__(startURL, item[0], toSave, filenameDateset)
            

if __name__ == '__main__':
    spider = AQIspider()
    # spider.get_all_city_links()
    # spider.save_all_city_links()
    spider.load_all_city_links()
    spider.crawl(update=True)