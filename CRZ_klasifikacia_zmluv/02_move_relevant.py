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

source_dir    = os.getcwd()+'\\contracts_text\\'
direction_dir = os.getcwd()+'\\contracts_mandayrates\\'

if not os.path.exists('contracts_mandayrates'):
	os.makedirs('contracts_mandayrates')

DB_clean_tagged = pd.read_csv('DB_clean_text_tagged.csv', delimiter = '|')

for index, row in DB_clean_tagged.iterrows():
	contract = str(row['ID']) + '_' + str(row['Priloha_ID'])
	os.system('move ' +source_dir+contract +'.pdf ' + direction_dir+contract +'.pdf')
	os.system('move ' +source_dir+contract +'.txt ' + direction_dir+contract +'.txt')

# úprava - zmluvy boli premiestnené manuálne