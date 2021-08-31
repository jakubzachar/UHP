# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |

import json
import requests
import re
import pandas as pd
from itertools import islice

DB = pd.read_csv('DB_partners.csv', sep = '|')
starting_row = 0


# If it was unsuccessful last time let's try to do it again :)
if not 'SK_NACE' in DB.columns:
	DB['SK_NACE'] = ''
else:
	# Find latest occurrence of SK_NACE
	for i in range(0,DB.shape[0]):
		if not pd.isnull(DB.at[i,'SK_NACE']):
			starting_row = i

for index, row in islice(DB.iterrows(), starting_row, None):
	print('Finding SK_NACE code for supplier',index+1,'out of',DB.shape[0])

	accounting_IDs = []
	SK_NACE_codes  = []

	# Get IDs of Accounting items
	if not pd.isnull(row['Ico']):
		if row['Ico'].isdigit():
			link = 'http://www.registeruz.sk/cruz-public/api/uctovne-jednotky?zmenene-od=2000-01-01&ico='+row['Ico']

			resp = requests.get(link)
			content = resp.json()
			# úprava podmienky kvoli pravdepodobnej zmene struktury
			if len(content['id']) > 0:
				accounting_IDs = content['id']
				last = accounting_IDs[-1]

				# úprava podmienky kvoli pravdepodobnej zmene struktury
				while content['existujeDalsieId'] == True:
					resp = requests.get(link+'?pokracovat-za-id='+str(last))
					content = resp.json()
					accounting_IDs = accounting_IDs + content['id']
					last = accounting_IDs[-1]
			else:
				accounting_IDs = []

	for ID in accounting_IDs:
		link = 'http://www.registeruz.sk/cruz-public/api/uctovna-jednotka?id='+str(ID)

		resp = requests.get(link)
		content = resp.json()

		if 'skNace' in content:
			DB.at[index,'SK_NACE'] = content['skNace']

	if (index % 50 == 0):
		DB.to_csv('DB_partners.csv', sep = '|')
