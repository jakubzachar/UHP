# Matej Badin | UHP | 2019                                             |
# -------------------------------------------------------------------- |
# Packages needed :  numpy, re, os, pandas                             |
# -------------------------------------------------------------------- |
# Tag and filter extracted tables based on keywords                    |
# -------------------------------------------------------------------- |

import os
import re
import pandas as pd
import ast
import shutil

def natural_sort(l):
	convert = lambda text: int(text) if text.isdigit() else text.lower()
	alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ]
	return sorted(l, key = alphanum_key)

find_txt    = re.compile('txt')
working_dir = os.getcwd()+'\\contracts_mandayrates\\'
final_dir   = os.getcwd()+'\\contracts_mandayrates_tables\\'
extract_number = re.compile(r'\d+')

# Check if there is directory _tables if yes, delete it, if no create it
if os.path.isdir(final_dir):
	shutil.rmtree(final_dir)
else:
	os.mkdir(final_dir)

# List all subdirectories with tables in working dir
subdirectories = [ndir for ndir in os.listdir(working_dir) if os.path.isdir(os.path.join(working_dir, ndir))]

# Import file with keywords
fo = open('keywords.txt', 'r', encoding = 'utf-8')
lines = fo.readlines()
fo.close()

categories = []

# Import keywords from keywords.txt and prepare data structures
for line in lines:
	line = line.split(',')

	category_name = line[0]
	keywords = []
	hits     = []
	hits_per_category = 0

	for i, item in enumerate(line):
		if (i>0):
			keywords.append(item.strip())
			hits.append(0)

	categories.append([category_name,keywords,hits,hits_per_category])

header_categories = [category[0] for category in categories]
header_keywords   = []

# Import metadata from text_tagged file
DB_import = pd.read_csv('DB_clean_text_tagged.csv', delimiter = '|')
DB_import = DB_import.drop('Unnamed: 0', 1)

header_import = ['Nazov','ID','Inner-ID','Objednavatel_ICO','Objednavatel','Objednavatel_adresa','Dodavatel_ICO','Dodavatel','Dodavatel_adresa',
				'Datum_zverejnenia','Datum_podpisu','Datum_platnosti','Datum_ucinnosti','Posledna_zmena','Cena_konecna','Cena_podpisana','Rezort','Typ',
				'Priloha_ID','Priloha_nazov','Link','Velkost','Datum','Text','Pocet_znakov','Pocet_stran','Pocet_tabuliek','Tabulky_strany']

header_metadata = ['Nazov','ID','Inner-ID','Objednavatel_ICO','Objednavatel','Objednavatel_adresa','Dodavatel_ICO','Dodavatel','Dodavatel_adresa',
				'Datum_zverejnenia','Datum_podpisu','Datum_platnosti','Datum_ucinnosti','Posledna_zmena','Cena_konecna','Cena_podpisana','Rezort','Typ',
				'Priloha_ID','Priloha_nazov','Link','Velkost','Datum','Text','Pocet_znakov','Pocet_stran','Tabulka_strana','Tabulka_cislo']

len_header_import = len(header_import)
DB_import = DB_import.drop(DB_import.columns.difference(header_import), axis=1)

# Produce new header for new file
header_sum_cat    = ['Výskyty']
header_categories = [category[0] for category in categories]
header_keywords   = []

for category in categories:
	header_keywords = header_keywords + category[1]

header = header_metadata + header_sum_cat + header_categories + header_keywords

# For each CSV table in each subdirectory tag tables
# Produce another CSV in which each row contain (meta)information about some table

N_dir = len(subdirectories)
row_list = []

for index, directory in enumerate(subdirectories):
	print('Processing contract', directory.strip('_tables'), '-', index+1, 'out of', N_dir)

	table_dir = os.path.join(working_dir, directory)
	tables = [f for f in os.listdir(table_dir) if os.path.isfile(os.path.join(table_dir, f))]

	# Sort tables according to number in table_number.csv
	tables = natural_sort(tables)

	for table in tables:
		fo = open(os.path.join(table_dir,table), 'r', encoding = 'utf-8')
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
				category[3]   += category[2][j]

		# Extract metadata and join it with counted hits
		row = DB_import.loc[DB_import['Priloha_ID'] == int(extract_number.findall(table_dir)[1])]

		meta_data = [row.iat[0,i] for i in range(0,len(header_import)-1)]
		meta_data.append(int(extract_number.findall(table)[0]))

		# Insert number of the page
		if (float(row['Pocet_tabuliek'])>0):
			meta_data[len(meta_data)-2] = ast.literal_eval(meta_data[len(meta_data)-2])[int(extract_number.findall(table)[0])-1]
		else:
			meta_data[len(meta_data)-2] = 0

		data_hits = []

		for category in categories:
			data_hits += category[2]

		sum_data = 0
		for category in categories:
			sum_data += category[3]

		data = meta_data + [sum_data] + [category[3] for category in categories] + data_hits
		row_list.append(dict((label,data[i]) for i, label in enumerate(header)))

# Save unranked CSV table
DB_export = pd.DataFrame(row_list, columns = header)
DB_export.to_csv('CRZ_DB_clean_tables.csv', header = header, sep='|')

# Filter out all irrelevant tables
# and produce CSV which has only tables with at least one position and one
delete_rows = []
for index, row in DB_export.iterrows():
	if not(((float(row['Pozícia']) > 0) or (float(row['Popis práce']) > 0)) and (float(row['Kvantifikátor']) > 0)):
		delete_rows.append(index)

print('Number of tables : ', DB_export.shape[0],'| Filtered out : ', len(delete_rows))

DB_export = DB_export.drop(delete_rows)
DB_export.to_csv('CRZ_DB_clean_tables.csv', sep='|')

# Copy all relevant tables into directory _tables
for index, row in DB_export.iterrows():
	source      = os.path.join(working_dir,str(row['ID']) + '_' + str(row['Priloha_ID']) + '_tables\\table_' + str(row['Tabulka_cislo']) + '.csv')
	destination = os.path.join(final_dir,str(row['ID']) + '_' + str(row['Priloha_ID']) + '_' + str(row['Tabulka_cislo']) + '.csv')
	os.system('copy '+source+' '+destination)

# úprava - tento kód už nebol využitý