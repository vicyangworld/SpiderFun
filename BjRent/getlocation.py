from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from urllib.request import urlopen
from bs4 import BeautifulSoup

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
driver = webdriver.Chrome(executable_path=r'C:\Users\orion\Downloads\chromedriver_win32\chromedriver.exe', chrome_options=chrome_options)
driver.get("http://map.yanue.net/")
driver.find_element_by_id('addrs').send_keys('北京朝阳石佛营东里109号楼')

driver.find_element_by_id('toLatLngBtn').click()
sleep(5)

# sreach_window=driver.current_window_handle
page_source = driver.page_source


# html = urlopen(page_source)
soup = BeautifulSoup(page_source, 'lxml')
lacation = soup.findAll(id="showResults")
coorinate = lacation.contents[2].split(':')[1]
print(coorinate)
driver.close()