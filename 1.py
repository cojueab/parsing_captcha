from parse_captcha import parse
from PIL import Image
from selenium import webdriver
driver = webdriver.PhantomJS(executable_path='./phantomjs.exe')
driver.set_window_size(1120, 550)
driver.get("http://103.23.150.139/marathi/")
# now that we have the preliminary stuff out of the way time to get that image :D
element = driver.find_element_by_id('style13')[-1:] # find part of the page you want image of
location = element.location
size = element.size
driver.save_screenshot('screenshot.png') # saves screenshot of entire page
driver.quit()

im = Image.open('screenshot.png') # uses PIL library to open image in memory

left = location['x']
top = location['y']
right = location['x'] + size['width']
bottom = location['y'] + size['height']


im = im.crop((left, top, right, bottom)) # defines crop points
im.save('screenshot.png') # saves new cropped image