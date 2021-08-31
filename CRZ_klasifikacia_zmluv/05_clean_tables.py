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
import operator
import shutil

def parse_text(text):
	slovak_alphabet = 'aáäbcčdďeéfghiíjklĺľmnňoóôpqrŕsštťuúvwxyýzž'

	text = text.casefold()
	words = []

	new_word = ''
	word = True
	for char in text:
		if char in slovak_alphabet:
			new_word = new_word + char
			word = True
		else:
			if word:
				words.append(new_word)
				new_word = ''
			word = False

	return words

# Files
working_dir = os.getcwd()
tables_dir       = working_dir+'\\IT_contracts_mandayrates_tables'
clean_tables_dir = working_dir+'\\IT_contracts_mandayrates_clean_tables'

if os.path.isdir(clean_tables_dir):
	shutil.rmtree(clean_tables_dir)
else:
	os.mkdir(clean_tables_dir)

tables_csv = [f for f in os.listdir(tables_dir) if os.path.isfile(os.path.join(tables_dir, f))]

# Import standard Slovak vocabulary corpus and dictionary
import hunspell

normal_SK  = os.path.join(working_dir, 'Dicts\\sk_SK')
english_US = os.path.join(working_dir, 'Dicts\\en_US')
special_SK = os.path.join(working_dir, 'Dicts\\sk_SK_special')

# Dictionary with standard Slovak language and words from contracts in this sector by build_special_dictionary.py
hunspell_normal  = hunspell.Hunspell(normal_SK, normal_SK)
hunspell_english = hunspell.Hunspell(english_US, english_US)
hunspell_special = hunspell.Hunspell(normal_SK, special_SK)

# Own spellcheck function also making sure word is case-folded and whitespace is stripped
def spell(word):
	word = word.casefold().strip()
	return (hunspell_normal.spell(word) or hunspell_english.spell(word) or hunspell_special.spell(word))

# Import keywords and add them to the special dictionary for spellchecking
fo = open('keywords.txt', 'r', encoding = 'utf-8')
lines = fo.readlines()
fo.close()

all_keywords  = []

categories = []
add_words = []

# Import keywords from keywords.txt and put them inside special dictionary
for line in lines:
	line = line.split(',')

	category_name = line[0]
	keywords = []

	for i, item in enumerate(line):
		if (i>0):
			keywords.append(item.strip().casefold())
			all_keywords.append(item.strip().casefold())

	categories.append([category_name,keywords])

# Add keywords to special if they are wrong
for keyword in all_keywords:
	words = keyword.split()
	for word in words:
		if not spell(word):
			add_words.append(word)

# Copy special dictionary and append lines with keywords, reload hunspell_special
special_dic_with_keywords = os.path.join(working_dir, 'Dicts\\sk_SK_special_with_keywords')
# Copy file
# Change number in first line
# Append lines to file

# Reload special Hunspell dictionary
hunspell_special = hunspell.Hunspell(normal_SK, special_dic_with_keywords)

# Empty dictionary to be filled with suggested keywords
suggested_keywords = dict()

#####################################################################################################
# Analysis !
#####################################################################################################

N_tables = len(tables_csv)
for i, table_csv in enumerate(tables_csv):
	print('Processing table:',table_csv,' ', i+1, 'out of',N_tables)

	# Step 1
	# Read CSV and destroy any new line characters between " characters
	fo = open(os.path.join(tables_dir,table_csv), 'r', encoding = 'utf-8')
	lines = fo.readlines()
	fo.close()

	reminder = 0

	text = ''
	for line in lines:
		for char in line:
			if char == '"':
				reminder += 1
			reminder = reminder % 2

			if ((char == '\n') and (reminder == 1)):
				pass
			else:
				text += char

	fo = open(os.path.join(tables_dir,'temp.csv'), 'w', encoding = 'utf-8')
	fo.writelines(text)
	fo.close()

	# Step 2
	# Import CSV table into pandas and delete empty columns
	table = pd.read_csv(os.path.join(tables_dir,'temp.csv'), delimiter = ',')
	empty = dict((column,True) for column in table.columns)

	for column in table.columns:
		for index, row in table.iterrows():
			if not((str(row[column]).rstrip() == '') or (str(row[column]) == 'nan')):
				empty[column] = False
				break

	delete = [column for column in table.columns if empty[column]]
	table = table.drop(columns = delete, axis = 1)

	# Step 3
	# Try to identify columns with just dummy characters and not any meaningful word
	# and ... also destroy them
	dummy = dict((column,False) for column in table.columns)
	for column in table.columns:

		correct = 0
		wrong   = 0

		for index, row in table.iterrows():
			words = str(row[column]).casefold().split()
			for word in words:
				if spell(word):
					correct += 1
				else:
					wrong += 1

		# Arbitrarily chosen number
		if (wrong/(wrong+correct)>0.75):
			dummy[column] = True

	delete = [column for column in table.columns if dummy[column]]
	table = table.drop(columns = delete, axis = 1)
	# Save clean table
	table.to_csv(os.path.join(tables_dir,'temp.csv'), sep = ',')

	# Step 4
	# Identify if the first row is the header
	header = False

	# Select keywords in categories 'Hlavička tabuľky'
	selected_keywords   = []
	selected_categories = ['Hlavička tabuľky']

	# but still code in general ;)
	for category in categories:
		if category[0] in selected_categories:
			for keyword in category[1]:
				selected_keywords.append(keyword)

	# Pandas already tried to infer header from CSV - such nice from it ...
	number_of_hits = 0
	for keyword in selected_keywords:
		for column in table.columns:
			number_of_hits += column.count(keyword)

	# Arbitrarily chosen boundary
	if (number_of_hits>2):
		header = True

	# Step 5
	# Identify if there is a specific column with 'Pozicia'
	selected_keywords   = []
	selected_categories = ['Pozícia','Popis práce']
	number_of_hits      = dict((column,0) for column in table.columns)

	for category in categories:
		if category[0] in selected_categories:
			for keyword in category[1]:
				selected_keywords.append(keyword)

	for column in table.columns:
		for row in table[column]:
			row = str(row).casefold()
			for keyword in selected_keywords:
				if keyword in row:
					number_of_hits[column] += 1

	# Sorted columns with 'Pozicia'-like keywords if number of hits is at least > 1
	positions_columns = [(column,number_of_hits[column]/table.shape[0]) for column in table.columns if number_of_hits[column] > 0]
	positions_columns = sorted(positions_columns, key=lambda tup: tup[1], reverse=True)

	# Step 6
	# .. also try to identify columns which has significant number of rows containing numbers or prices
	find_number = re.compile(r'\d+')
	price_header = ['']

	selected_keywords   = []
	selected_categories = ['Hlavička cena']

	for category in categories:
		if category[0] in selected_categories:
			for keyword in category[1]:
				selected_keywords.append(keyword)

	prices_columns = []
	if header:
		for column in table.columns:
			for keyword in selected_keywords:
				if keyword in column:
					if not column in prices_columns:
						prices_columns.append(column)

	ratio_of_number_rows = dict((column,0) for column in table.columns)
	for column in table.columns:
		for row in table[column]:
			row = str(row)
			if len(find_number.findall(row))>0:
				ratio_of_number_rows[column] += 1

		ratio_of_number_rows[column] = ratio_of_number_rows[column]/table.shape[0]

	if len(prices_columns)>0:
		prices_columns = [(column,ratio_of_number_rows[column]) for column in prices_columns if ratio_of_number_rows[column] > 0.75]
	else:
		prices_columns = [(column,ratio_of_number_rows[column]) for column in table.columns if ratio_of_number_rows[column] > 0.75]

	positions_columns_names = [column[0] for column in positions_columns]
	for column in prices_columns:
		if column[0] in positions_columns_names:
			prices_columns.remove(column)

	prices_columns = sorted(prices_columns, key=lambda tup: tup[1], reverse=True)

	# Suggest new keywords based on data in the rows identified as this
	#  new keywords are given points according to the relative number of rows which already contain
	#  some selected keyword.
	if ((len(positions_columns)>0) and (len(prices_columns)>0)):
		for column in positions_columns:
			for row in table[column[0]]:
				row = str(row).casefold()
				words = parse_text(row)
				for word in words:
					if not word in selected_keywords:
						if word in suggested_keywords:
							suggested_keywords[word] += column[1]
						else:
							suggested_keywords[word]  = column[1]

	# Save to clean directory only if there is at least a single price column
	if (len(prices_columns)>0):
		table.to_csv(os.path.join(clean_tables_dir,table_csv), sep = ',')

	# Step 7
	# Identify in which column there is DPH or not
	with_DPH    = False
	without_DPH = False

	for column in table.columns:
		if 's DPH'   in column: with_DPH    = True
		if 'bez DPH' in column: without_DPH = True

	# Print metadata
	print('Header:',header)
	print('Positions:',positions_columns)
	print('Prices:',prices_columns)
	print('s DPH:',with_DPH)
	print('bez DPH:',without_DPH)

# Print suggested keywords
suggested_keywords = sorted(suggested_keywords.items(), key=operator.itemgetter(1), reverse=True)

fo = open('suggested_keywords.txt','w')
for keyword in suggested_keywords:
	fo.write(keyword[0]+'\t\t\t'+str(keyword[1])+'\n')
fo.close()

# úprava - tento kód už nebol využitý