# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, xml.etree.ElementTree, os                   |
# --------------------------------------------------------------------  |
# Filter contracts from supplier list                                   |

import os
import xml.etree.cElementTree as ET
import numpy as np
import pandas as pd

DB    = pd.read_csv('CRZ_DB_with_supplements.csv', delimiter = '|')
print('DB of contracts loaded in memory.')
print('Filtering relevant contracts')
number_of_contracts = DB.shape[0]

companies = pd.read_csv('companies.csv', delimiter = '|')
companies = companies['ICO'].tolist()
companies = [str(x) for x in companies]
remove = []

# Scan the dumped DB and remove contracts in which supplier is not company from the provided list
for i in range(0, number_of_contracts):
	if (i % 1000 == 0):
		print(i,'/',number_of_contracts)

	if not(str(DB.iloc[i,8]).replace(" ","") in companies):
		remove.append(i)

print('Find relevant: ', number_of_contracts-len(remove),' out of ',number_of_contracts)

# Clean irrelevant
DB_clean = DB.drop(DB.index[remove])

# Produce the rest
header = ['Nazov','ID','Inner-ID','Objednavatel_ICO','Objednavatel','Objednavatel_adresa','Dodavatel_ICO','Dodavatel','Dodavatel_adresa',
			'Datum_zverejnenia','Datum_podpisu','Datum_platnosti','Datum_ucinnosti','Posledna_zmena','Cena_konecna','Cena_podpisana','Rezort','Typ','Stav','Prilohy','Dodatky']

DB_clean.iloc[:,2:].to_csv('CRZ_DB_clean.csv', header = header, sep='|')
