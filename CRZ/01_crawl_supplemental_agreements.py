# Matej Badin | UHP | 2019                                             |

# -------------------------------------------------------------------- |
# Packages needed :  numpy, xml.etree.ElementTree, os                  |
# -------------------------------------------------------------------- |
# Crawl tables with supplemental agreements on CRZ GOV                 |
# Include them inside DB get by 01_parse_xml.py                        |
# -------------------------------------------------------------------- |

import requests
import lxml.html as lh
import pandas as pd
import re

find_ID = re.compile(r'\d+')

# Find last starting ID --> 1 000 000 000 is just sufficiently large number
# úprava - zmena linku
url  = 'https://www.crz.gov.sk/dodatky-k-zmluvam/?page=1000000000'

page = requests.get(url)
doc  = lh.fromstring(page.content)

# úprava - potrebná zmena kódu: last_ID = int(doc.find_class('pagelist')[0][-1].text_content()) - nefunguje
path = doc.xpath("//nav")
last_ID = int(path[0][0][11].text_content())

print('Up to this date there are ',last_ID*20,'supplemental agreements ...')
print('Going to crawl CRZ GOV and build DB_supplements.')

supplements_ID = []
page_ID = 1
for page_ID in range(0,last_ID):
	print('\tProcessing page',page_ID,'out of',last_ID)
	url  = 'https://www.crz.gov.sk/dodatky-k-zmluvam/?page='+str(page_ID) # úprava - zmena linku

	page = requests.get(url)
	doc  = lh.fromstring(page.content)

	tr_elements = doc.xpath('//tr')
	supplements = [supplement for supplement in tr_elements if len(supplement) == 5]
	IDs = [find_ID.findall(supplement[1][0].attrib['href'])[0] for supplement in supplements[1:] if len(supplement[1][0].attrib['href']) != 0] # úprava - doplnená podmienka kvôli chybám na stránke
	supplements_ID = supplements_ID + IDs

	f = open('IDs.txt', 'a')
	for ID in IDs:
		f.write(ID + '\n')
	f.close()

