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
	# Save partial result
	DB_clean_tagged.to_csv('CRZ_DB_clean_text_tagged.csv', sep='|')

sys.stdout.flush()
# Analyse PDF pages and extract tables
if not 'Pocet_tabuliek' in DB_clean_tagged.columns:

	total_pages = 0
	# Calculate total number of pages to analyse
	for index, row in DB_clean_tagged.iterrows():
		total_pages += int(row['Pocet_stran'])

	print('Total number of pages to analyse:', total_pages)

	DB_clean_tagged.insert(25, 'Pocet_tabuliek', np.zeros(number_of_contracts))

	empty_column = [None] * number_of_contracts
	if not 'Tabulky_strany' in DB_clean_tagged.columns:
		DB_clean_tagged.insert(26, 'Tabulky_strany', empty_column)

	# Analyse PDF pages and extract tables
	i = 0
	for index, row in DB_clean_tagged.iterrows():
		i += 1

		contract = str(row['ID']) + '_' + str(row['Priloha_ID']) + '.pdf'
		contract_dir = working_dir + contract.replace('.pdf','_tables')
		sys.stdout.flush()

		if not os.path.exists(contract_dir):
			os.makedirs(contract_dir)

			number_of_pages = int(row['Pocet_stran'])

			print('Processing contract ', contract,' ', i, 'out of', number_of_contracts)
			print('Going to process', number_of_pages, 'pages ...')
			sys.stdout.flush()

			number_of_tables = 0
			tables_pages = []

			start_time = time.time()
			for page in range(1,number_of_pages):

				print('\tProcessing page', page, 'out of', number_of_pages)
				tables = camelot.read_pdf(working_dir + contract, pages = str(page))
				sys.stdout.flush()

				if (len(tables)>0):

					for j in range(0,len(tables)):
						tables[j].to_csv(contract_dir + '/table_' + str(number_of_tables + j + 1) + '.csv')
						tables_pages.append(page)
						print(tables[j].parsing_report)

					number_of_tables += len(tables)

			end_time = time.time()
			print('Processed ', number_of_pages, ' pages in ',(end_time-start_time))

			DB_clean_tagged.at[index,'Pocet_tabuliek'] = int(number_of_tables)
			DB_clean_tagged.at[index,'Tabulky_strany'] = str(tables_pages)

			# Save information about number of pages
			DB_clean_tagged.to_csv('CRZ_DB_clean_text_tagged.csv', sep='|')

# úprava - tento kód už nebol využitý - bol rozdelený na 2 časti