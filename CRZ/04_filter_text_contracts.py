# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, re                                          |
# --------------------------------------------------------------------  |
# Parsing downloaded data from CRZ GOV obtained by download_dump script |

import os
import re

if not os.path.exists('contracts_text'):
	os.makedirs('contracts_text')

if not os.path.exists('contracts_scan'):
	os.makedirs('contracts_scan')

raw_dir   = os.getcwd()+'\\contracts\\'
text_dir = os.getcwd()+'\\contracts_text\\'
scan_dir = os.getcwd()+'\\contracts_scan\\'

contracts = [f for f in os.listdir(raw_dir) if os.path.isfile(os.path.join(raw_dir, f))]

i = 0
n = len(contracts)

for contract in contracts:
	i += 1
	print('Processing contract ',contract,' ',i,' out of ',n)

	try:
		os.system('pdftotext '+raw_dir+contract+' output.txt')

		fo = open('output.txt','r', encoding='utf8')
		lines = fo.readlines()
		fo.close()

		file = ''
		for line in lines:
			file += line

		del lines

		check_file   = re.sub(r'\s+', '', file, flags=re.UNICODE)

		if (len(check_file)>0):
			os.system('move '+raw_dir+contract+' '+text_dir+contract)
			os.system('move output.txt '+text_dir+contract.replace('.pdf','.txt'))
			print('Moved to '+text_dir)
		else:
			os.system('move '+raw_dir+contract+' '+scan_dir+contract)
			print('Moved to '+scan_dir)

	except:
		os.system('move '+raw_dir+contract+' '+scan_dir+contract)
		print('Moved to '+scan_dir)

