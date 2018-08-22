# -*- coding: utf-8 -*-
import csv
from pyecharts import Line, Bar, Overlap, Grid, Pie, Radar
from pyecharts import Geo
# from pyecharts_snapshot.main import make_a_snapshot
from pyecharts import Style
from toDataBase import fetch_db
import webbrowser
import os
import threading
from concurrent.futures import ThreadPoolExecutor
import time
import datetime

_LEVEL=[
    {"max": 50, "min": 0, "label": "优"},
    {"max": 100, "min": 50, "label": "优"},
    {"max": 150, "min": 100, "label": "轻度污染"},
    {"max": 200, "min": 150, "label": "中度污染"},
    {"max": 300, "min": 200, "label": "重度污染"},
    {"min": 300, "label": "严重污染"},
]

style1 = Style(
    title_color="#fff",
    title_pos="center",
    #title_top="5%",
    title_text_size=45,
    subtitle_text_size=40,
    # width=8000,
    # height=1000,
    background_color='#404958'
)
style2 = Style(
    width=7000,
    height=500,
)

def get_days(str1, str2):
    date1=datetime.datetime.strptime(str1[0:10],"%Y-%m-%d")
    date2=datetime.datetime.strptime(str2[0:10],"%Y-%m-%d")
    num=(date2-date1).days
    return num


class Drawer:
    def __init__(self, inputFile, is_from_datebase = False):
        if is_from_datebase:
            self.dbName = inputFile
        if not is_from_datebase:
            self.AQIdate  = []
            self.AQIlevel1 = []
            self.AQIlevel2 = []
            self.AQIlevel3 = []
            self.AQIlevel4 = []
            self.AQIlevel5 = []
            self.AQIlevel6 = []
            self.AQIvalue = []
            self.AQIrange = []
            self.AQIPM25 = []
            self.AQIPM10  = []
            self.dateValueLevel = []
            cnt = 0
            interval = 7
            temp_index = 0
            with open(inputFile) as cf:
                    lines = csv.reader(cf)
                    for line in lines:
                        if temp_index%interval == 0:
                            if len(line)==10:
                                cnt = cnt + 1
                                self.AQIdate.append(line[0])
                                self.AQIvalue.append(line[2])
                                self.AQIrange.append(line[3])
                                self.AQIPM25.append(line[4])
                                self.AQIPM10.append(line[5])
                        temp_index = temp_index + 1

                    self.AQIlevel1 = cnt * [50]
                    self.AQIlevel2 = cnt * [100]
                    self.AQIlevel3 = cnt * [150]
                    self.AQIlevel4 = cnt * [200]
                    self.AQIlevel5 = cnt * [300]
                    self.AQIlevel6 = cnt * [500]


    def draw_line(self, title, level = True, value = True, rrange = True, pm25 = True, pm10 = True):
        line = Line(title)
        line.add("", self.AQIdate, self.AQIlevel6, line_opacity=0, is_splitline_show=False, is_fill=True, area_color='#9C0A4E', area_opacity=1, is_smooth=True)
        line.add("", self.AQIdate, self.AQIlevel5, line_opacity=0, is_splitline_show=False, is_fill=True, area_color='#D20040', area_opacity=1, is_smooth=True)
        line.add("", self.AQIdate, self.AQIlevel4, line_opacity=0, is_splitline_show=False, is_fill=True, area_color='#FF401A', area_opacity=1, is_smooth=True)
        line.add("", self.AQIdate, self.AQIlevel3, line_opacity=0, is_splitline_show=False, is_fill=True, area_color='#FFAA00', area_opacity=1, is_smooth=True)
        line.add("", self.AQIdate, self.AQIlevel2, line_opacity=0, is_splitline_show=False, is_fill=True, area_color='#EFDC31', area_opacity=1, is_smooth=True)
        line.add("", self.AQIdate, self.AQIlevel1, line_opacity=0, is_splitline_show=False, is_fill=True, area_color='#43CE17', area_opacity=1, is_smooth=True)
        if value:
            line.add("AQI指数", self.AQIdate, self.AQIvalue, line_color='#009FE6', is_splitline_show=False, is_smooth=True)
        if rrange:
            line.add("AQI排名", self.AQIdate, self.AQIrange, line_color='#FFFFFF', is_splitline_show=False, is_smooth=True)
        if pm25:
            line.add("PM2.5", self.AQIdate, self.AQIPM25, is_splitline_show=False, is_smooth=True)
        if pm10:
            line.add("PM10", self.AQIdate, self.AQIPM10, line_color='#AEA7D1', is_splitline_show=False, is_smooth=True)
        
        #line.show_config()
        line.render(title + '.html')
        webbrowser.open(title + '.html')

    def __take_second__(self, elem):
        return elem[1]

    def __draw_geo_heatmap_core__(self, date):
        outname1 = ''.join([date,'.jpeg'])
        outname2 = ''.join([date,'-s.jpeg'])
        if os.path.exists(outname1):
            print(outname1," is existed.")
            return
        if os.path.exists(outname2):
            print(outname2," is existed.")
            return

        command = "SELECT * FROM City WHERE City.date=?"
        args = date
        data = []
        for item in fetch_db(self.dbName, command, args):
            data.append((item[0], item[4]))
            # if item[4] > 300:
            #     print((item[0], item[4]))
        #data.sort(key=self.__take_second__)

        year = date.split('-')[0]
        mouth = date.split('-')[1]
        day = date.split('-')[2]
        geotitle = year + '年' + mouth + '月' + day +'日' + "全国主要城市空气质量"
        geo1 = Geo(geotitle, "Data from AQI", **style.init_style)
        geo2 = Geo(geotitle, "Data from AQI", **style.init_style)        
        attr, value = geo1.cast(data)
        geo1.add("", attr, value, 
                type="heatmap", 
                is_visualmap=True, 
                #visual_range_color=['#4BDE1C','#FAEA67','#FABF43','#FA502E','#D20040','#3B0512'], 
                visual_range=[0, 300],
                #visual_range_size=[50,100],
                visual_text_color='#fff',
               # visual_split_number=6,
                visual_range_text=['',''],
                # visual_orient="horizontal",
                visual_pos="10%",
                #is_piecewise=True,
                #pieces=_LEVEL,
                #geo_normal_color='#323C48',
                #symbol_size=10,
                # is_label_show=True
                )
        geo2.add("", attr, value, 
                #type="heatmap", 
                is_visualmap=True, 
                #visual_range_color=['#4BDE1C','#FAEA67','#FABF43','#FA502E','#D20040','#830840'], 
                visual_range=[0, 300],
                #visual_range_size=[50,100],
                visual_text_color='#fff',
                #visual_split_number=6,
                visual_range_text=['',''],
                # visual_orient="horizontal",
                visual_pos="10%",
                #is_piecewise=True,
               # pieces=_LEVEL,
                #geo_normal_color='#323C48',
                symbol_size=25,
                # is_label_show=True
                )

        geo1.render(outname1)
        geo2.render(outname2)
        # outpicName = ''.join([outname1.split('.')[0]]+['.png'])
        # make_a_snapshot(outname1, outpicName)   #需要phantomjs支持 不支持中文
        # outpicName = ''.join([outname2.split('.')[0]]+['.png'])
        # make_a_snapshot(outname2, outpicName)   #需要phantomjs支持 不支持中文

        print(outname1 +' has been saved')
        #webbrowser.open(title)
    def draw_geo_heatmap(self, dbName, thread_num=10):
        command = "SELECT * FROM Date"
        args = None
        allData = fetch_db(dbName, command, args)

        pool = ThreadPoolExecutor(thread_num) 
        for item in allData:
            pool.submit(self.__draw_geo_heatmap_core__,item[0])

    def __draw_bar_core__(self,data,count=20):
        maxvalue = []
        value = []
        name  = []
        for i in range(len(data)):
            if i < count:
                value.append(data[i][0])
                name.append(data[i][1])
                maxvalue.append(1682-data[i][0])
        
        bar = Bar("最\"污\"城市排行榜")
        bar.add("", name, value, xaxis_type="category",xaxis_interval=0,yaxis_max=1682,is_label_show=True, is_stack=True)
        bar.add("", name, maxvalue, xaxis_type="category",xaxis_interval=0,yaxis_max=1682, is_stack=True)
        bar.render()

    def __sort_by_value__(self, dic, reverse=True): 
        sortedList = [[item[1],item[0]] for item in dic.items()]
        sortedList.sort(reverse=reverse)
        return sortedList

    def __get_draw_bar_data_core__(self, dbName, begDate, para1, para2=None):
        if para2 == None:
            command = "SELECT * FROM City WHERE City.aqi"+para1[0]+str(para1[1])
        else:
            command = "SELECT * FROM City WHERE City.aqi"+para1[0]+str(para1[1]) + " AND City.aqi"+para2[0]+str(para2[1])
        
        args = None
        citAQI200Dic={}
        allData = fetch_db(dbName, command, args)
        for item in allData:
            #print(item)
            if item[2] < begDate:
                continue
            key = item[0]+'-'+item[1]
            if '伊犁' in key:
                key = '伊犁-新疆'
            if '甘南-黑龙江' in key: 
                continue
            if key in citAQI200Dic.keys():
                citAQI200Dic[key] = citAQI200Dic[key] + 1
            else:
                citAQI200Dic[key] = 1

        return self.__sort_by_value__(citAQI200Dic)

    def get_date_begin_end(self):
        command = "SELECT * FROM Date"
        args = None
        allData = fetch_db(dbName, command, args)
        allData.sort()
        return allData[0],allData[-1]

    def __get_value_name_bar__(self, data, count = 20):
        value = []
        name  = []
        for i in range(len(data)):
            if i < count:
                value.append(data[i][0])
                name.append(data[i][1])

        return value, name

    def draw_bar(self, dbName, begDate=None):
        Beg, End = self.get_date_begin_end()
        if begDate==None:
            begDate = Beg[0]
        maxvalue = get_days(begDate, End[0])
        data1  = self.__get_draw_bar_data_core__(dbName, begDate, ('<', 50))
        dataBase = self.__get_draw_bar_data_core__(dbName,begDate,  ('<', 100))
        data3 = self.__get_draw_bar_data_core__(dbName, begDate, ('<', 150), ('>=', 100))#轻度
        data4 = self.__get_draw_bar_data_core__(dbName, begDate, ('<', 200), ('>=', 150))
        data5  = self.__get_draw_bar_data_core__(dbName,begDate,  ('<', 300), ('>=', 200))
        data6  = self.__get_draw_bar_data_core__(dbName, begDate, ('>=', 300))

        count = max(len(data1),len(dataBase),len(data3),len(data4),len(data5),len(data6))
        # print(len(data1),len(dataBase),len(data3),len(data4),len(data5),len(data6))
        valueBase, nameBase = self.__get_value_name_bar__(dataBase, count)

        def __re_arrange(count, nameBase, dataInput):
            valuetemp = count*[0]
            idx = 0
            for item in nameBase:
                for i in dataInput:
                    if item == i[1]:
                        valuetemp[idx] = i[0]
                        break
                idx = idx + 1
            return valuetemp

        def label_formatter(params):
            return params.name+' '+str(params.value)+'%'

        grid = Grid(**style2.init_style)
        grid.use_theme("dark")
        bar = Bar("",**style1.init_style)
        value1 = __re_arrange(count, nameBase, data1)
        bar.add("优", nameBase[:-1], value1[:-1], is_stack=True )
        # list(map(lambda x: x[0]-x[1], zip(valueBase, valuetemp)))
        bar.add("良", nameBase[:-1], list(map(lambda x: x[0]-x[1]-x[2], zip(valueBase[:-1], value1[:-1],count*[3]))), is_stack=True)
        value3 = __re_arrange(count, nameBase, data3)
        bar.add("轻度污染", nameBase[:-1], value3[:-1], is_stack=True )
        value4 = __re_arrange(count, nameBase, data4)
        bar.add("中度污染", nameBase[:-1], value4[:-1], is_stack=True )
        value5 = __re_arrange(count, nameBase, data5)
        bar.add("重度污染", nameBase[:-1], value5[:-1], is_stack=True )
        value6 = __re_arrange(count, nameBase, data6)
        bar.add("严重污染", nameBase[:-1], value6[:-1], is_stack=True,
                # yaxis_name="天",
                # yaxis_name_size='16',
                # yaxis_name_gap='25',
                # yaxis_name_pos='top',
                xaxis_type="category",
                xaxis_interval=0,
                yaxis_interval=0,
                xaxis_pos='top',
                yaxis_max=maxvalue,
                # is_label_show=True, 
                #bar_category_gap="30%",
                xaxis_label_textsize=12, 
                yaxis_label_textsize=12,
                xaxis_rotate=90,
                yaxis_rotate=90,
                # label_formatter=label_formatter,
                is_legend_show=True,
                legend_pos='91%',
                legend_top='center',
                legend_orient='horizontal',
                label_pos='bottom',
                label_text_size=16,
                label_color=['#43CE17','#EFDC31','#FFAA00','#FF401A','#D20040','#9C0A4E']
                )

        idxList = [str(x) for x in range(1,len(valueBase))]
        line = Line()
        meanList = len(idxList)*[sum(valueBase[:-1])/len(idxList)]
        line.add("", idxList, meanList, line_width=3, symbol=None, line_color='#0078D7',mark_line=["average"])
        line.add("", idxList, valueBase[:-1],
                is_smooth=True,
                symbol=None,
                line_width=3,
                xaxis_label_textsize=16,
                xaxis_rotate=90, 
                line_color='#FF401A'
                )
        overlap = Overlap()
        overlap.add(bar)
        overlap.add(line, is_add_xaxis=True, xaxis_index=1)
        grid.add(overlap, grid_top="21%")
        grid.render()
        grid.render("最优城市排行榜.jpeg")


        #低于均值城市的饼状图

        lowThanMeanDic = {}
        for v in nameBase[-101:-1]:
            # if v < meanList[0]:
            key = v.split('-')[1]
            if key in lowThanMeanDic.keys():
                lowThanMeanDic[key] = lowThanMeanDic[key] + 1
            else:
                lowThanMeanDic[key] = 1
        data = self.__sort_by_value__(lowThanMeanDic)
        value, name = self.__get_value_name_bar__(data, len(data))
        pie = Pie()
        pie.use_theme("dark")
        pie.add("", name,value, is_legend_show=False, is_label_show=True, label_text_size=10)
        pie.render("最污百城省份分布.jpeg")

    def draw_rader(self, dbName, begDate=None):
        def get_rader_data(dbName, city, begDate):
            args = None
            command = "SELECT * FROM City WHERE City.name=\'"+str(city)+"\' AND City.aqi>="+str(begDate) + ' ORDER BY City.aqi DESC'
            allFetchData = fetch_db(dbName, command, args)
            data_list=[]
            for item in allFetchData[:5]:
                d_list = list(item)
                d_list.pop(0)
                d_list.pop(0)
                d_list.pop(0)
                d_list.pop(0)
                d_list.pop(0)
                d_list.pop(0)
                if d_list[0]>500:   #PM2.5
                    d_list[0] = 500
                if d_list[1]>1500:   #PM10
                    d_list[1] = 1500
                if d_list[2]>100:   #SO2
                    d_list[2] = 100
                if d_list[3]>200:   #NO2
                    d_list[3] = 200
                if d_list[4]>5:     #Co
                    d_list[4] = 5
                if d_list[5]>200:   #O3
                    d_list[5] = 200
                data_list.append(d_list)
            return data_list

        #五城最新雷达图
        begDate = 300
        hetian  = get_rader_data(dbName, '和田', begDate)
        xingtai = get_rader_data(dbName, '邢台', begDate)
        dezhou  = get_rader_data(dbName, '德州', begDate)     
        zhengzhou = get_rader_data(dbName, '郑州', begDate)
        xianyang = get_rader_data(dbName, '咸阳', begDate)
        def __draw_radar_core__(city,data,color):
            c_schema= [
                        {"name": "PM2.5\nmax=500μg/m3", "max": 500, "min": 0},
                        {"name": "PM10\nmax=1500μg/m3", "max": 1500, "min": 0},
                        {"name": "SO2\nmax=100μg/m3", "max": 100},
                        {"name": "NO2\nmax=200μg/m3", "max": 200},
                        {"name": "CO\nmax=5.0mg/m3", "max": 5},
                        {"name": "O3\nmax=200μg/m3", "max": 200, "min": 0}
                    ]
            radar = Radar(background_color='#333')
            radar.config(c_schema=c_schema, shape='polygon',radar_text_color="#FFF",)
            # radar.use_theme("dark")
            radar.add(city, data, 
                        is_area_show=True,
                        area_color=color,#'#F0891F',
                        area_opacity=0.3,
                        line_curve=0.1,
                        line_opacity=0,
                        symbol=None,
                        legend_text_color='#FFF',
                        # legend_orient='vertical',
                        legend_top ='4%',
                        legend_pos='25%',
                        legend_text_size=15,
                        legend_selectedmode=False,
                        label_color=[color]#,'#3F4A97','#F05F8D','#6A9EA3']
            )
            radar.render()
            radar.render(city+'雷达图.jpeg')

        __draw_radar_core__("和田",hetian,'#F0891F')
        __draw_radar_core__("邢台",xingtai,'#3F4A97')
        __draw_radar_core__("德州",dezhou,'#F05F8D')
        __draw_radar_core__("郑州",zhengzhou,'#1C7E89')
        __draw_radar_core__("咸阳",xianyang,'#b3e4a1')     
        # radar.add("邢台", xingtai, 
        #             is_area_show=True,
        #             area_color='#3F4A97',
        #             area_opacity=0.3,
        #             line_curve=0.1,
        #             line_opacity=0,
        #             symbol=None,
        #             legend_text_color='#FFF',
        #             # legend_orient='vertical',
        #             legend_pos='left',
        #             legend_selectedmode=False,
        #             label_color=["#EE8B24",'#3F4A97','#F05F8D','#6A9EA3']
        # )
        # radar.add("德州", dezhou,
        #             is_area_show=True,
        #             area_color='#F05F8D',
        #             area_opacity=0.3,
        #             line_curve=0.1,
        #             line_opacity=0,
        #             symbol=None,
        #             legend_text_color='#FFF',
        #             # legend_orient='vertical',
        #             legend_pos='left',
        #             legend_selectedmode=False,
        #             label_color=["#EE8B24",'#3F4A97','#F05F8D','#6A9EA3']
        # )
        # radar.add("郑州", zhengzhou,
        #             is_area_show=True,
        #             area_color='#6A9EA3',
        #             area_opacity=0.3,
        #             line_curve=0.1,
        #             line_opacity=0,
        #             symbol=None,
        #             legend_text_color='#FFF',
        #             # legend_orient='vertical',
        #             legend_pos='left',
        #             legend_selectedmode=False,
        #             label_color=["#EE8B24",'#3F4A97','#F05F8D','#6A9EA3']
        # )
        # # radar.add("咸阳", xianyang, item_color="#b3e4a1", symbol=None,
        # #         legend_selectedmode='single')
        # radar.render()
        # radar.render('五城最新雷达图.jpeg')


if __name__ == "__main__":
    start=time.time()

    dbName = 'AQI.db'
    pic = Drawer(dbName, is_from_datebase = True)

    #pic.draw_geo_heatmap(dbName)
    # pic.draw_bar(dbName,'2015-01-01')
    pic.draw_rader(dbName,'2018-08-19')

    end=time.time()
    print("time consume: "+str(end-start), " second.")
