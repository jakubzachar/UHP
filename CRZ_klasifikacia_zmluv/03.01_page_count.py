# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, re, os, pandas, Camelot, OpenCV             |
#                    pdfminer.six -- requirement already for Camelot    |
# --------------------------------------------------------------------  |
# Extract tables from already tagged and filtered relevant contracts    |
# --------------------------------------------------------------------  |

import os
import subprocess
import re
import numpy as np
import pandas as pd
import camelot
import time
import sys

# pdfminer for extracting information about number of pages
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import resolve1

working_dir = os.getcwd()+'/contracts_mandayrates/'

# Open tagged spreadsheet and read information, sorted
DB_clean_tagged = pd.read_csv('CRZ_DB_clean_text_tagged.csv', delimiter = '|')
DB_clean_tagged = DB_clean_tagged.drop('Unnamed: 0', 1)

number_of_contracts = len(DB_clean_tagged.index)

# If column with number of PDF pages in contract do not exist
# then calculate it ...
if not 'Pocet_stran' in DB_clean_tagged.columns:
	DB_clean_tagged.insert(25, 'Pocet_stran', np.zeros(number_of_contracts))

	# Identify how many pages are in every contract
	# useful to estimate time needed to extract all tables from PDF
	print('Counting pages in PDFs ...')
	i = 0
	for index, row in DB_clean_tagged.iterrows():
		try:
			i += 1

			contract = "CRZ_" + str(row['ID']) + '_' + str(row['Priloha_ID']) + '_contract.pdf'
			print('Processing contract ', contract,' ', i, 'out of', number_of_contracts)

			contract_file = open(working_dir + contract, 'rb')

			parser = PDFParser(contract_file)
			document = PDFDocument(parser)

			pages = resolve1(document.catalog['Pages'])['Count']
			DB_clean_tagged.at[index,'Pocet_stran'] = int(pages)

			contract_file.close()
		except TypeError:
			DB_clean_tagged.at[index,'Pocet_stran'] = "chyba"
		except KeyError:
			DB_clean_tagged.at[index,'Pocet_stran'] = "chyba"
#úprava použitom kóde bolo namiesto chyby 0
	# Save partial result
	DB_clean_tagged.to_csv('CRZ_DB_clean_text_tagged.csv', sep='|')

sys.stdout.flush()

# úprava - tento kód bol využitý no nie je nevyhnutný
