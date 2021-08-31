# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |

import json
import requests
import re
import pandas as pd

# Build DB of public partners
# Using 'Register partnerov verejneho sektora'
link = 'https://rpvs.gov.sk/OpenData/PartneriVerejnehoSektora'

page = 0
partners = 0
row_list = []

while link != '':
	resp = requests.get(link)
	content = resp.json()

	page += 1
	partners += len(content['value'])

	print('Page:',page,' Partners:',partners)

	for row in content['value']:
		row_list.append(row)

	try:
		link = content['@odata.nextLink']
	except:
		link = ''

	if (partners % 100 == 0):
		DB = pd.DataFrame(row_list)
		DB.to_csv('DB_partners.csv', sep = '|')

DB = pd.DataFrame(row_list)
DB.to_csv('DB_partners.csv', sep = '|')
