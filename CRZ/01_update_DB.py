# Matej Badin | UHP | 2019                                             |
# -------------------------------------------------------------------- |
# Packages needed :  numpy, xml.etree.ElementTree, os                  |
# -------------------------------------------------------------------- |

import requests
import lxml.html as lh
import pandas as pd
import re

DB   		   = pd.read_csv('CRZ_DB.csv', sep = '|')
DB_supplements = pd.read_csv('CRZ_DB_supplements.csv', sep = '|')

DB['Dodatky']  = ''

# Structure dictionary (ID_contract,[list of supplements])
supplements = dict()

count = 0
n_supplements = DB_supplements.shape[0]

# Crawl DB_supplements
for index, row in DB_supplements.iterrows():
	count += 1
	print('Merging metadata for supplemental agreement',count,'out of',n_supplements)

	ID_contract = row['ID_zmluva']

	header_import   = ['Nazov','ID_supplement','Inner-ID','Objednavatel','Dodavatel','Datum_podpisu','Datum_platnosti','Datum_ucinnosti','Poznamka','Prilohy']
	supplement_data = []

	for item in header_import:
		supplement_data.append(row[item])

	supplement_data.append('https://www.crz.gov.sk/index.php?ID='+str(row['ID_supplement'])+'&l=sk')

	if ID_contract in supplements:
		supplements[ID_contract].append(supplement_data)
	else:
		supplements[ID_contract] = [supplement_data]

n_supplements = len(supplements)
not_find = 0

for index, ID_contract in enumerate(supplements):
	print('Saving data for contract ',index+1,'out of',n_supplements)
	location = DB.index[DB['ID'] == ID_contract]
	if len(location) == 0:
		not_find += 1
	else:
		DB.at[location[0], 'Dodatky'] = supplements[ID_contract]

print(not_find,'contracts not merged since contracts are from corrupted XML files ...')
DB.to_csv('CRZ_DB_with_supplements.csv', sep = '|')
