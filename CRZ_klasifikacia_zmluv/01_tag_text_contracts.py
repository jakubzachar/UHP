# Matej Badin | UHP | 2019                                             |
# -------------------------------------------------------------------- |
# Packages needed :  numpy, re, os, pandas, ast                        |
# -------------------------------------------------------------------- |
# Tag interesting contracts based on keywords                          |
# -------------------------------------------------------------------- |

import os
import re
import numpy as np
import pandas as pd
import ast

find_txt    = re.compile('txt')
working_dir = os.getcwd()+'\\contracts_text\\'

extract_ID = re.compile(r'\d+')

contracts = [f for f in os.listdir(working_dir) if os.path.isfile(os.path.join(working_dir, f))]
contracts_txt = [f for f in contracts if (len(find_txt.findall(f))>0)]

# Import clean table to extract metadata from it
DB_clean = pd.read_csv('CRZ_DB_clean.csv', delimiter = '|')

# Keywords are stored in keywords.txt provided in rows as categories separated by comma, first word is name of the category
# Script searches for keywords, keywords are prepared by lowercasing

fo = open('keywords.txt', 'r', encoding = 'utf-8')
lines = fo.readlines()
fo.close()

categories = []

# Import keywords from keywords.txt and prepare data structure
for line in lines:
	line = line.split(',')

	category_name = line[0]
	keywords = []
	hits     = []
	hits_per_category = 0

	for i, item in enumerate(line):
		if (i>0):
			keywords.append(item.strip().casefold())
			hits.append(0)

	categories.append([category_name,keywords,hits,hits_per_category])

# Prepare header for export
header_metadata = ['Nazov','ID','Inner-ID','Objednavatel_ICO','Objednavatel','Objednavatel_adresa','Dodavatel_ICO','Dodavatel','Dodavatel_adresa',
					'Datum_zverejnenia','Datum_podpisu','Datum_platnosti','Datum_ucinnosti','Posledna_zmena','Cena_konecna','Cena_podpisana','Rezort','Typ',
					'Priloha_ID','Priloha_nazov','Link','Velkost','Datum','Text']

header_sum_cat    = ['Výskyty']
header_categories = [category[0] for category in categories]
header_keywords   = []

for category in categories:
	header_keywords = header_keywords + category[1]

header = header_metadata + header_sum_cat + header_categories + header_keywords

row_list = []
N = len(contracts_txt)

number_of_characters = []

# Go through all processed text files, lowercase it, for every keyword count number of occurrences
for i, contract in enumerate(contracts_txt):
	print('Analysing contract: ', contract, ' ', i, 'out of', N)

	fo = open(working_dir+contract, 'r', encoding = 'utf-8')
	lines = fo.readlines()
	fo.close()

	text = ''

	for line in lines:
		text += line.casefold().replace('\n',' ')

	del lines

	for category in categories:
		category[3] = 0
		for j, keyword in enumerate(category[1]):
			category[2][j] = text.count(keyword.casefold())
			category[3] += category[2][j]

	# Extract metadata and join it with counted hits
	row = DB_clean.loc[DB_clean['ID'] == int(extract_ID.findall(contract)[0])]

	meta_data = [row.iloc[0,i] for i in range(1,19)]
	attachment_data = ast.literal_eval(row.iloc[0,20])[0]

	meta_data = meta_data + attachment_data
	data_hits = []

	for category in categories:
		data_hits += category[2]

	sum_data = 0
	for category in categories:
		sum_data += category[3]

	data = meta_data + [sum_data] + [category[3] for category in categories] + data_hits
	row_list.append(dict((label,data[i]) for i, label in enumerate(header)))

	# Count number of characters in contract
	number_of_characters.append(len(text))

# Save unranked csv table
DB_clean_tagged = pd.DataFrame(row_list, columns = header)
DB_clean_tagged.to_csv('DB_clean_text_tagged.csv', header = header, sep='|')

# Rank contracts according to number of keywords, number of characters in contract and price.
# Ranking is based on three categories listed above, in each category 10 points are distributed
# according to logarithmic scale and then added. Contracts are sorted by the rank.

# Insert new column -- number of characters
DB_clean_tagged.insert(24, 'Pocet_znakov', number_of_characters)
DB_clean_tagged = DB_clean_tagged.sort_values(by=['Výskyty','Pocet_znakov','Cena_konecna'], ascending = False)

# Sort rows by number of hits, number of characters and final prize
delete_rows = []
for index, row in DB_clean_tagged.iterrows():
	if ((float(row['Pozícia']) == 0) and (float(row['Popis práce']) == 0)):
		delete_rows.append(index)
	if (float(row['Výskyty']) == 0):
		delete_rows.append(index)

print('Sorted : ',N,'| Filtered out : ',len(delete_rows))

DB_clean_tagged = DB_clean_tagged.drop(delete_rows)
DB_clean_tagged.to_csv('CRZ_DB_clean_text_tagged.csv', sep='|')
