# -*-coding-*-:utf-8
import json
from urllib.request import urlopen, quote
import requests
 

def getLngLat(address):
    url = 'http://api.map.baidu.com/geocoder/v2/'
    output = 'json'
    ak = 'HeR6bZCKoZFnS3GSTgNPreEcNQhwcH6q' # 浏览器端密钥
    address = quote(address) # 由于本文地址变量为中文，为防止乱码，先用quote进行编码
    uri = url + '?' + 'address=' + address  + '&output=' + output + '&ak=' + ak

    req = urlopen(uri)
    res = req.read().decode() 
    temp = json.loads(res)
    lat = temp['result']['location']['lat']
    lng = temp['result']['location']['lng']
    return lng, lat 

if __name__=='__main__':
    lacation = r"北京市朝阳区石佛营东里109号"
    lng, lat = getLngLat(lacation)
    print(lng, lat)