# -*- coding: utf-8 -*-

import os
import csv
import sqlite3 as sql
import json

PROVINCES_TODATABASE = ['直辖市','河北','山西','辽宁','吉林','黑龙江', \
                        '江苏','浙江','安徽','福建','江西','山东', \
                        '河南','湖北','湖南','广东','海南','四川', \
                        '贵州','云南','陕西','甘肃','青海','台湾', \
                        '内蒙古','广西','西藏','宁夏','新疆']

def get_date_begin_end(dbName):
    command = "SELECT * FROM Date"
    args = None
    allData = fetch_db(dbName, command, args)
    allData.sort()
    return allData[0],allData[-1]


def creat_db(dbName):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    cursor.execute('''CREATE TABLE Date
                (
                 date text)''')
    cursor.execute('''CREATE TABLE City
                ( 
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
    if date != None:
        cursor.executemany("INSERT INTO Date VALUES (?)",date)
    if city != None:
        #cursor.execute("INSERT INTO City VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", city)
        cursor.executemany("INSERT INTO City VALUES (?, ?, ?, ?, ?, ?, ?, ?)", city)
    connect.commit()
    connect.close()

# def fetch_db(dbName, date, all_date=False):
#     connect = sql.connect(dbName)
#     cursor = connect.cursor()
#     if date!=None and all_date==False:
#         cursor.execute("SELECT * FROM City WHERE City.date=?",(date,))
#     elif date==None and all_date:
#         cursor.execute("SELECT * FROM Date")
#     else:
#         raise("Wrong Para")
        
#     data = cursor.fetchall()
#     connect.close()
#     return data

def fetch_db(dbName, command, args):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    
    if args == None:
        cursor.execute(command)
    else:
        cursor.execute(command,(args,))
 
    data = cursor.fetchall()
    connect.close()
    return data


def delete_db(dbName, city, date):
    connect = sql.connect(dbName)
    cursor = connect.cursor()
    cursor.execute('DELETE FROM City WHERE date=?',date)
    connect.close()

def delete_db(dbName):
    os.remove(dbName) 

def load_all_city_links(informat='json', filename='./city_name_link'):
    with open(filename+'.'+informat,'r') as infile:
        cityDic = json.loads(infile.read())
    return cityDic

def saveDataToDatabase(filesPath = './', dataBaseName='AQI.db', update=False):
    dbName = os.path.join(filesPath, dataBaseName)
    if not update and os.path.exists(dbName):
        delete_db(dbName)

    if not os.path.exists(dbName):
        creat_db(dbName)

    if update:
        _, lastDateInDB = get_date_begin_end(dataBaseName)

    # idxCity = 0
    #idxDate = 0
    cityDic = load_all_city_links()
    cityDicNew = {}
    Date = []
    for item in cityDic.items():
        cityName_zh = item[0].split('-')[1]
        cityName_py = item[1].split('/')[-1].split('.')[0]
        cityDicNew[cityName_py] = cityName_zh
    for province in os.listdir(filesPath):
        if not os.path.isdir(province) or (province not in PROVINCES_TODATABASE):
            continue
        for file in os.listdir(province):
            City = []
            _cityName_py = file.split('_')[1].split('.')[0]
            _cityName_zh = cityDicNew.get(_cityName_py)
            absFileName = os.path.join(filesPath,province,file)
            #print("get data from ", absFileName,"  ", _cityName_zh,"......")
            cf = open(absFileName,'r')
            # with open(absFileName,'r') as cf:
            lines = csv.reader(cf)
            for line in lines:
                if len(line)!=10 or line[0] == "日期":
                    continue
                if update and line[0] < lastDateInDB[0]:
                    continue
                # print(absFileName+" "+cityName_zh, line)
                try:
                    tempDate = (line[0],)
                    if tempDate not in Date:
                        Date.append(tempDate)
                        #idxDate = idxDate + 1
                    tempCity = ( _cityName_zh, province, 
                                line[0], line[1], 
                                int(line[2]), int(line[3]),
                                int(line[4]), int(line[5])
                    )
                    City.append(tempCity)
                except:
                    raise('wrong!')

                # idxCity = idxCity + 1

            cf.close()
            insert_db(dbName, None, City)
            print("insert OK:\t", absFileName, "\t\tdata to database:\t", dbName, "\t", _cityName_zh)
    insert_db(dbName, Date, None)
    #print("fetch 2014-11-10 data from "+dbName)
    #print(fetch_db(dbName,'2014-11-10'))

if __name__ == "__main__":
    dbName = 'AQI.db'
    
    #saveDataToDatabase(update=False)

    # command = "SELECT * FROM City WHERE City.date=?"
    # args = '2018-08-15'
    # command = "SELECT * FROM City WHERE City.aqi>=200"
    # args = None
    print(get_date_begin_end('AQI.db'))