# Matej Badin | UHP | 2019                                             |
# -------------------------------------------------------------------- |
# Packages needed :  os, re                                            |
# External dependencies: Tesseract-OCR, pdftopng                       |
# -------------------------------------------------------------------- |
# OCR documents using Google Tesseract engine                          |

import os
import subprocess
import re

find_number = re.compile(r'\d+')
FNULL = open(os.devnull, 'w')

def natural_sort(l):
	convert = lambda text: int(text) if text.isdigit() else text.lower()
	alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
	return sorted(l, key = alphanum_key)

scan_dir = os.getcwd()+'\\contracts_scan\\'
contracts = [f for f in os.listdir(scan_dir) if os.path.isfile(os.path.join(scan_dir, f))]

N_contracts = len(contracts)

for i,contract in enumerate(contracts):
	print('Processing contract:',contract,' ',i+1,'out of',N_contracts)

	# Convert PDF to PNG images
	# -r specifies DPI
	# -gray is for grayscale image
	print('\tRendering pages from PDF ...')

	retcode = subprocess.call('pdftopng -q -r 350 -gray '+os.path.join(scan_dir,contract)+' '+os.path.join(scan_dir,'output'), stdout=FNULL, stderr=subprocess.STDOUT)
	output_files = [f for f in os.listdir(scan_dir) if os.path.isfile(os.path.join(scan_dir, f)) and 'output' in f]
	output_files = natural_sort(output_files)

	# Detect rotation and auto-rotate image
	# ...

	# Perform OCR by Tesseract
	text = ''
	for page in output_files:
		print('\tOCR on page:',int(find_number.findall(page)[0]))
		retcode = subprocess.call('tesseract '+os.path.join(scan_dir,page)+' '+os.path.join(scan_dir,'output')+' -l eng+ces+slk', stdout=FNULL, stderr=subprocess.STDOUT)
		fo = open(os.path.join(scan_dir,'output.txt'),'r', encoding = 'utf-8')
		lines = fo.readlines()
		fo.close()

		for line in lines:
			text += line

	# Save results
	fo = open(os.path.join(scan_dir,contract.replace('.pdf','.txt')),'w', encoding = 'utf-8')
	fo.write(text)
	fo.close()

	# Delete temporary files
	os.system('del '+os.path.join(scan_dir,'output*'))
