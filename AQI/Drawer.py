# -*- coding: utf-8 -*-
import csv
from pyecharts import Line
from pyecharts import Bar
import webbrowser

class Drawer:
    def __init__(self, inputFile):
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


    def draw(self, title, level = True, value = True, rrange = True, pm25 = True, pm10 = True):
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

if __name__="__main__":
    input_filename = os.path.join("Dataset_"+city+".csv")
    pic = Drawer(input_filename)
    pic.draw(city + " AQI")