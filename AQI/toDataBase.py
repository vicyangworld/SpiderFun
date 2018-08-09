# -*- coding: utf-8 -*-

from pyecharts import Geo
import os
import csv
import sqlite3 as sql
import json

def creat_db(dbName):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE Date
                (id int primary key, 
                 date text)''')
    cursor.execute('''CREATE TABLE City
                (id int primary key, 
                 name text,
                 province text,
                 date text,
                 level text,
                 aqi int,
                 range int,
                 pm25 int,
                 pm10 int,
                 FOREIGN KEY (date) REFERENCES Date(date))''')
    connect.commit()
    connect.close()

def insert_db(dbName, date, city):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    if not date:
        cursor.execute("INSERT INTO Date VALUES (?, ?)",date)
    #cursor.execute("INSERT INTO City VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", city)
    cursor.executemany("INSERT INTO City VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", city)
    connect.commit()
    connect.close()

def fetch_db(dbName, date):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM City WHERE City.date=?",(date,))
    data = cursor.fetchall()
    connect.close()
    return data
    
def delete_db(dbName, city, date):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    cursor.execute('DELETE FROM City WHERE date=?',date)
    connect.close()


def load_all_city_links(informat='json', filename='./city_name_link'):
    with open(filename+'.'+informat,'r') as infile:
        cityDic = json.loads(infile.read())
    return cityDic

def saveDataToDatabase(filesPath = './', dataBaseName='AQI.db'):
    dbName = os.path.join(filesPath, dataBaseName)
    if not os.path.exists(dbName):
        creat_db(dbName)
    idxCity = 0
    idxDate = 0
    cityDic = load_all_city_links()
    cityDicNew = {}
    for item in cityDic.items():
        cityName_zh = item[0].split('-')[1]
        cityName_py = item[1].split('/')[-1].split('.')[0]
        cityDicNew[cityName_py] = cityName_zh
    for province in os.listdir(filesPath):
        if not os.path.isdir(province):
            continue
        for file in os.listdir(province):
            City = []
            Date = []
            _cityName_py = file.split('_')[1].split('.')[0]
            _cityName_zh = cityDicNew.get(_cityName_py)
            print(_cityName_zh)
            absFileName = os.path.join(filesPath,province,file)
            print("get data from ", absFileName, "......")
            cf = open(absFileName,'r')
            # with open(absFileName,'r') as cf:
            lines = csv.reader(cf)
            for line in lines:
                if len(line)!=10 or line[0] == "日期":
                    continue
                # print(absFileName+" "+cityName_zh, line)
                tempDate = (idxDate, line[0])
                if tempDate not in Date:
                    Date.append(tempDate)
                    idxDate = idxDate + 1
                tempCity = (idxCity, _cityName_zh, province, 
                            line[0], line[1], 
                            int(line[2]), int(line[3]),
                            int(line[4]), int(line[5])
                )
                City.append(tempCity)
                idxCity = idxCity + 1

            cf.close()
            print("insert ", absFileName, "data to database: ", dbName)
            insert_db(dbName, Date, City)
            print("fetch 2014-11-10 data from "+dbName)
            print(fetch_db(dbName,'2014-11-10'))
        

if __name__ == "__main__":
    saveDataToDatabase()