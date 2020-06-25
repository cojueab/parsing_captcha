from bs4 import BeautifulSoup
import os
import requests
import sys, csv
import string
from threading import Thread
from PIL import Image
import time
from selenium import webdriver


url = 'http://103.23.150.139/marathi/'
state={
	"view" : "",
	"event": "",
	"data": {}
}

def renderEmptyData(state):
	sletters = list(string.ascii_lowercase)
	for i in sletters:
		state['data'][i]=[]

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:56.0) Gecko/20100101 Firefox/56.0', 'DNT':'1','Upgrade-Insecure-Requests' : '1'}

def initial(state):

	for key, value in enumerate(headers):
		capability_key = 'phantomjs.page.customHeaders.{}'.format(key)
		webdriver.DesiredCapabilities.PHANTOMJS[capability_key] = value


	driver.set_window_size(1120, 550)
	driver.get("http://103.23.150.139/marathi/")
	# now that we have the preliminary stuff out of the way time to get that image :D
	element = driver.find_element_by_id('ContentPlaceHolder1_RadioButton1')  # find part of the page you want image of
	element.click()
	time.sleep(3)
	element = driver.find_element_by_id('ContentPlaceHolder1_RadioButton3')  # find part of the page you want image of
	element.click()
	# location = element.location
	# size = element.size
	# driver.save_screenshot('screenshot.png')  # saves screenshot of entire page

	driver.save_screenshot("12.png")
	driver.quit()

	# im = Image.open('screenshot.png')  # uses PIL library to open image in memory
    #
	# left = location['x']
	# top = location['y']
	# right = location['x'] + size['width']
	# bottom = location['y'] + size['height']
    #
	# im = im.crop((left, top, right, bottom))  # defines crop points
	# im.save('screenshot.png')  # saves new cropped image
	conn = requests.get(url, headers=headers)
	html = conn.text
	soup = BeautifulSoup(html,"html.parser")
	state['view'] = soup.find(id='__VIEWSTATE').get('value')
	state['event'] = soup.find(id='__EVENTVALIDATION').get('value')

	formdata = {
		'__EVENTTARGET':'ctl00$ContentPlaceHolder1$RadioButton1',
		'__EVENTARGUMENT': '',
		'__LASTFOCUS' : '',
		'__VIEWSTATE' : state.get('view'),
		'__EVENTVALIDATION': state.get('event'),
		'ctl00$ContentPlaceHolder1$gr1' : 'RadioButton1'
	}
	
	req = requests.post(url, data = formdata, headers= headers)
	soup = BeautifulSoup(req.text,"html.parser")
	state['view'] = soup.find(id='__VIEWSTATE').get('value')
	state['event'] = soup.find(id='__EVENTVALIDATION').get('value')




def findDistricts(state):
	formdata = {
		'__EVENTTARGET':'ctl00$ContentPlaceHolder1$RadioButton4',
		'__EVENTARGUMENT': '',
		'__LASTFOCUS' : '',
		'__VIEWSTATE' : state.get('view'),
		'__EVENTVALIDATION': state.get('event'),
		'ctl00$ContentPlaceHolder1$gr1' : 'RadioButton1',
		'ctl00$ContentPlaceHolder1$gr2' : 'RadioButton4',
	}
	req = requests.post(url, data = formdata, headers= headers)
	soup = BeautifulSoup(req.text,"html.parser")
	districts  = soup.find(id='ContentPlaceHolder1_Drop2')
	dists = list(districts.stripped_strings)[1:]
	state['view'] = soup.find(id='__VIEWSTATE').get('value')
	state['event'] = soup.find(id='__EVENTVALIDATION').get('value')
	return dists

def findAssembly(state,district):
	formdata = {
		'__EVENTTARGET':'ctl00$ContentPlaceHolder1$Drop2',
		'__EVENTARGUMENT': '',
		'__LASTFOCUS' : '',
		'__VIEWSTATE' : state.get('view'),
		'__EVENTVALIDATION': state.get('event'),
		'ctl00$ContentPlaceHolder1$gr1' : 'RadioButton1',
		'ctl00$ContentPlaceHolder1$gr2' : 'RadioButton4',
		'ctl00$ContentPlaceHolder1$Drop2' : district,
		'ctl00$ContentPlaceHolder1$TextBox1' : '',
		'ctl00$ContentPlaceHolder1$TextBox2' : '',
		'ctl00$ContentPlaceHolder1$TextBox3' : '',
	}

	req = requests.post(url, data = formdata, headers= headers)
	soup = BeautifulSoup(req.text,"html.parser")
	acc  = soup.find(id='ContentPlaceHolder1_Drop3')
	assembly = list(acc.stripped_strings)
	state['view'] = soup.find(id='__VIEWSTATE').get('value')
	state['event'] = soup.find(id='__EVENTVALIDATION').get('value')
	return assembly

def scrapData(state,headers,district,account,alphabet):
	print('Starting scrappint alphabet : ' + alphabet)
	formdata = {
		'__EVENTTARGET':'ctl00$ContentPlaceHolder1$Drop2',
		'__EVENTARGUMENT': '',
		'__LASTFOCUS' : '',
		'__VIEWSTATE' : state.get('view'),
		'__EVENTVALIDATION': state.get('event'),
		'ctl00$ContentPlaceHolder1$gr1' : 'RadioButton1',
		'ctl00$ContentPlaceHolder1$gr2' : 'RadioButton4',
		'ctl00$ContentPlaceHolder1$Drop2' : district,
		'ctl00$ContentPlaceHolder1$Drop3' : account,
		'ctl00$ContentPlaceHolder1$TextBox1' : alphabet,
		'ctl00$ContentPlaceHolder1$TextBox2' : '',
		'ctl00$ContentPlaceHolder1$TextBox3' : '',
		'ctl00$ContentPlaceHolder1$Button2' : 'Search',
	}

	req = requests.post(url, data = formdata, headers= headers)
	soup = BeautifulSoup(req.text,"html.parser")
	table  = soup.find(id='ContentPlaceHolder1_GridView1')
	rows = table.find_all('tr')
	head_text = [[header.get_text() for header in rows[0].find_all('th')[:-3]]]
	#head_text[0] = head_text[0][:3] + ['First_Name'] +['Last_Name'] + head_text[0][4:]

	# content = [[item.get_text() for item in row.find_all('td')[:-3]] for row in rows[1:]]
	content =[]
	for row in rows[1:]:
		td = [item.get_text() for item in row.find_all('td')[:-3]]
		td[3] = td[3].replace("\0", "") #[item.get_text() for item in row.find_all('td')[:-3]]
		while td[3].find("  ")!=-1:
		    td[3] = td[3].replace("  ",'')
		# nameArray = td[3].split(' ')
		#nameArray = '  '.join(td[3].split()).replace('\0','').split(' ')
		#nName = []
		#for name in nameArray:
		#	if name and len(name) > 1:			
		#		nName.append(name)
		#td = td[:3] + [nName[0].strip(), nName[len(nName)-1].strip()] + td[4:]
		content.append(td)

	
	parse = head_text + content

	state['view'] = soup.find(id='__VIEWSTATE').get('value')
	state['event'] = soup.find(id='__EVENTVALIDATION').get('value')
	state['data'][alphabet] = parse if len(parse[0]) else []
	# if len(parse[0]):
	# 	writeFile(account, alphabet + '.csv', parse)
	# 	print('Scrapping ' + alphabet + ' finished')



def startScrap(state,headers,district,account,alphabet):
	letters = list(string.ascii_lowercase)
	index = letters.index(alphabet)
	thrd = []
	for alpha in letters[index:]:
		thrd.append(Thread(target=scrapData, args=(state, headers, district, account, alpha,)))
	return thrd




def writeFile(dir,name,content):
	if not os.path.exists(dir):
		os.makedirs(dir)
	with open(dir+'/'+str(name), 'w') as csvfilie:
		writter = csv.writer(csvfilie,delimiter='|')
		for row in content:
			writter.writerow(row)

def writeSingleCSV(name,content):
	letters = list(string.ascii_lowercase)
	with open(str(name)+'.csv', 'w') as csvfilie:
		writter = csv.writer(csvfilie,delimiter='|')
		wroteHeader = False
		for letter in letters:
			if len(content[letter]):
				if not wroteHeader:
					writter.writerow(content[letter][0])
					wroteHeader = True
				for row in content[letter][1:]:
					writter.writerow(row)





if __name__ == '__main__':
	driver = webdriver.PhantomJS(executable_path='./phantomjs.exe')
	acc = 0
	try:
		acc = sys.argv[1]
	except IndexError:
		acc = 0


	#reload(sys)
	#sys.setdefaultencoding('utf-8')

	initial(state)
	renderEmptyData(state)
	dists = findDistricts(state)

	print("Please select an index of district")
	print('-----------------------------------')
	for dist in dists:
		print(dist)
	dist = input('Enter  : ')
	dist = int(dist)-1

	print("\nPlease select an index of Assembly")
	print('-----------------------------------')
	assembly = findAssembly(state,dists[dist])
	for idx,asc in enumerate(assembly):
		print(str(idx+1) +' - ' +asc)

	acc = input('Enter  : ')
	acc = int(acc) - 1
	
	print("\nPlease Enter an Alphabet")
	print('-----------------------------------')
	alphabet = input('Enter  : ')

	if alphabet is '':
		alphabet = "a"

	if dists[dist] and assembly[acc]:
		thrds = startScrap(state,headers,dists[dist], assembly[acc], alphabet)	

		count = len(thrds)

		for thr in thrds:
			thr.start()
		for thr in thrds:
			thr.join()

		writeSingleCSV(assembly[acc], state['data'])
		print('Scrapping finished ....')
