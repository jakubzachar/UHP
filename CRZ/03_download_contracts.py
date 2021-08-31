# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, pandas, os, urllib.request, re              |
# --------------------------------------------------------------------  |
# Parsing downloaded data from CRZ GOV obtained by download_dump script |

import os
import urllib.request
import numpy as np
import pandas as pd
import ast
import re

if not os.path.exists('contracts'):
	os.makedirs('contracts')

working_dir = os.getcwd()+'\\contracts\\'

DB_clean    = pd.read_csv('CRZ_DB_clean.csv', delimiter = '|')
number_of_contracts = DB_clean.shape[0]

download_link = []
download_name = []
download_size = []

size     = 0

for i in range(0, number_of_contracts):

	attachments = ast.literal_eval(DB_clean.iloc[i,20])
	contract_ID = str(DB_clean.iloc[i,2])

	for attachment in attachments:

		contract_attachment_ID        = str(attachment[0])
		contract_attachment_PDF       = attachment[2]
		contract_attachment_size      = int(attachment[3])

		size += contract_attachment_size/1000000

		download_name.append('CRZ_'+contract_ID+'_'+contract_attachment_ID+'_contract.pdf')
		download_link.append(contract_attachment_PDF)
		download_size.append(size)

	supplements = []
	if not pd.isnull(DB_clean.iloc[i,21]):
		supplements = ast.literal_eval(DB_clean.iloc[i,21].replace(' nan,',' "nan",'))

	for supplement in supplements:
		supplement_ID = str(supplement[1])

		supplement_attachment_number = 0
		supplement_attachments = ast.literal_eval(supplement[9])

		for attachment in supplement_attachments:
			supplement_attachment_number += 1
			download_name.append('CRZ_'+contract_ID+'_'+supplement_ID+'_'+str(supplement_attachment_number)+'_supplement.pdf')
			download_link.append(attachment[0])
			download_size.append(0)

number_of_attachments = len(download_link)

print('Documents to download :', number_of_attachments)
print('Total size            : %.2f MB' % (size),' (without supplemenents)')

print('Download started ...')

prob = []

# úprava - doplnené o try a except - kde v prípade HTTPErroru zapíše názov problémovej zmluvy a filu - potrebné vyriešiť samostatne

for i in range(0, number_of_contracts):
	try:
		print('Downloading document: %d out of %d | Rest size: %.2f MB' % (i+1,number_of_attachments,size-download_size[i]))
		urllib.request.urlretrieve(download_link[i], working_dir+download_name[i])
	except urllib.error.HTTPError:
		prob.append(download_name[i])
		f = open('missing.txt', 'a')
		for ID in prob:
			f.write(ID + '\n')
		f.close()

