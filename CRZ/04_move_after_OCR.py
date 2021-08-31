# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, re                                          |
# --------------------------------------------------------------------  |
# Move after OCR all files into IT_contracts_text                       |

import os
import re

text_dir = os.getcwd()+'\\contracts_text\\'
scan_dir = os.getcwd()+'\\contracts_scan\\'

contracts_pdf = [f for f in os.listdir(scan_dir) if os.path.isfile(os.path.join(scan_dir, f)) and 'pdf' in f]
contracts_txt = [f for f in os.listdir(scan_dir) if os.path.isfile(os.path.join(scan_dir, f)) and 'txt' in f]

for contract in contracts_txt:
	os.system('move '+scan_dir+contract+' '+text_dir+contract)
	os.system('move '+scan_dir+contract.replace('txt','pdf')+' '+text_dir+contract.replace('txt','pdf'))
