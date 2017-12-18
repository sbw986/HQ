""" HQ_tess.py: Extracts HQ Trivia question and answers text.  
                Performs online queries of extracted information to predict correct answer."""

import requests
import argparse
import multiprocessing
import pyscreenshot as ImageGrab
import pytesseract
from bs4 import BeautifulSoup
from joblib import Parallel, delayed
from ScriptingBridge import SBApplication
from PIL import Image


def process_query(answer):
	""" Performs online query of question and answers
		Predicts correct answer from query return values"""

	query = question + ' ' + '\'' + answer + '\''
	print('query: ', query)
	session = requests.Session()
	session.trust_env = False  # Don't read proxy settings from OS
	r = session.get('http://www.google.com/search', params={'q':query})
	soup = BeautifulSoup(r.text, "html.parser")
	return_val = soup.find('div',{'id':'resultStats'}).text
	return_list = return_val.split(' ')
	if 'About' in return_list:
		temp = return_list[1].replace(',','')
		total_return = float(temp)
	else:
		temp = return_list[0].replace(',','')
		total_return = float(temp)
	answer_loc = '\'' + answer + '\''
	session = requests.Session()
	session.trust_env = False  # Don't read proxy settings from OS
	r = session.get('http://www.google.com/search', params={'q':answer_loc})
	soup = BeautifulSoup(r.text, "html.parser")
	return_val2 = soup.find('div',{'id':'resultStats'}).text
	return_list2 = return_val2.split(' ')
	if 'About' in return_list2:
		temp = return_list2[1].replace(',','')
		ans_return = float(temp)
	else:
		temp = return_list2[0].replace(',','')
		ans_return = float(temp)

	print(answer, total_return, total_return/ans_return)

def get_window_image():
	""" Generates black and white image of text area within HQ game window"""

	#Grab Quicktime Window
	app = SBApplication.applicationWithBundleIdentifier_("com.apple.QuicktimePlayerX")
	finderWin = app.windows()[0]

	#Reposition and resize Quicktime window
	x, y, x_len, y_len = 50,50,400,800
	finderWin.setBounds_([[x,y],[x_len,y_len]])	

	#Grab text area of Quicktime window and convert image to B&W
	im = ImageGrab.grab(bbox=(x, y+150, x_len+x, y_len+y-200))
	im = im.convert('L')
	im = im.point(lambda x: 0 if x<200 else 255, '1')
	im.save('BW.PNG')

	return im

def img_to_queries(im):
	"""Converts text image to list of question and answers"""

	tessdata_dir_config = '--tessdata-dir "/usr/local/Cellar/tesseract/3.05.01/share"'
	text = pytesseract.image_to_string(im, config=tessdata_dir_config)
	text = text.split('\n')

	str_val = ''
	str_list = []

	for line in text:
		if line == '':
			str_list.append(str_val)
			str_val = ''
		else:
			str_val = str_val + ' ' + line
	str_list.append(str_val)

	question_addressed = False
	str_list_parsed = []
	for line in str_list:
		if '?' in line and len(line) > 15:
			str_list_parsed.append(line)
			question_addressed = True
		elif question_addressed == True:
			str_list_parsed.append(line)

	question = str_list_parsed[0]
	answers = str_list_parsed[1:4]

	return question, answers

if __name__ == '__main__':

	im = get_window_image()
	question, answers = img_to_queries(im)

	num_cores = multiprocessing.cpu_count()
	Parallel(n_jobs=num_cores)(delayed(process_query)(answer) for answer in answers)