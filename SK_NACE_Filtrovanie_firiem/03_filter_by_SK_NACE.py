# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, xml.etree.ElementTree, os                   |
# --------------------------------------------------------------------  |

import os
import pandas as pd
import re
# upravenie separátora
DB_partners = pd.read_csv('DB_partners.csv', sep='|', encoding='utf-8')

fo = open('SK_NACE_codes.txt','r')
lines = fo.readlines()
fo.close()

SK_NACE_codes = []
for SK_NACE_code in lines:
	SK_NACE_code = SK_NACE_code.strip()
	SK_NACE_codes.append(int(SK_NACE_code))

row_list = []
for index, row in DB_partners.iterrows():
	if row['SK_NACE'] in SK_NACE_codes:
		new_row = dict()

		new_row['ICO']     = row['Ico']
		new_row['Nazov']   = row['ObchodneMeno']
		if row['ObchodneMeno'] == '':
			new_row['Nazov'] = row['Meno'] + ' ' + row['Priezvisko']

		new_row['SK_NACE'] = row['SK_NACE']

		row_list.append(new_row)

DB_selected_partners = pd.DataFrame(row_list)
DB_selected_partners.to_csv('companies.csv', sep='|')
