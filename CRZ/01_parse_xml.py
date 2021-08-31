# Matej Badin | UHP | 2019                                              |
# --------------------------------------------------------------------  |
# Packages needed :  numpy, xml.etree.ElementTree, os                   |
# --------------------------------------------------------------------  |
# Parsing downloaded data from CRZ GOV obtained by download_dump script |

import os
import xml.etree.cElementTree as ET
import numpy as np
import pandas as pd

working_dir   = os.getcwd()+'\\CRZ_DB\\'
corrupted_dir = os.getcwd()+'\\Corrupted_XML_files\\'
files		= [f for f in os.listdir(working_dir) if os.path.isfile(os.path.join(working_dir, f))]

table = []

for f in files:
	try:
		file = ET.parse(working_dir+f)
		contracts = file.getroot()

		print('Parsing file ... '+f)

		if (len(list(contracts)) > 0):

			for contract in contracts:
				contract_name = contract[4].text
				contract_ID   = contract[1].text

				contract_inner_ID = contract[0].text

				contract_purchaser         = contract[2].text
				contract_purchaser_address = contract[21].text
				contract_purchaser_ICO     = contract[20].text

				contract_supplier         = contract[3].text
				contract_supplier_address = contract[19].text
				contract_supplier_ICO     = contract[13].text

				contract_date_publication = contract[12].text
				contract_date_signed      = contract[24].text
				contract_date_validity    = contract[6].text
				contract_date_efficiency  = contract[5].text
				contract_date_last_change = contract[16].text

				contract_price_final  = contract[8].text
				contract_price_signed = contract[7].text

				contract_resort = contract[11].text

				contract_type  = contract[23].text
				contract_state = contract[14].text

				contract_attachments = []
				attachments = contract[32]

				for attachment in attachments:
					contract_attachment_ID    = attachment[0].text
					contract_attachment_name  = attachment[1].text

					contract_attachment_document_scan = attachment[2].text
					contract_attachment_size_scan     = int(attachment[3].text)

					contract_attachment_document_text = attachment[4].text
					contract_attachment_size_text     = int(attachment[5].text)

					contract_text = False
					suffix = ''
# úprava - pre fungovanie s novými linkami - problém je treba opravit (doplnením udajov)
					if (contract_attachment_document_text != None ):
						contract_attachment_PDF  = "https://www.crz.gov.sk/data/att/" + contract_attachment_document_text
					elif (contract_attachment_document_scan != None ):
						contract_attachment_PDF  = "https://www.crz.gov.sk/data/att/" + contract_attachment_document_scan
					else:
						contract_attachment_PDF = "Problem"


					contract_attachment_size = str(max(contract_attachment_size_scan, contract_attachment_size_text))
					contract_attachment_date = attachment[6].text

				contract_attachments.append([contract_attachment_ID, contract_attachment_name, contract_attachment_PDF, contract_attachment_size, contract_attachment_date, contract_text])

				table.append([contract_name, contract_ID, contract_inner_ID, contract_purchaser_ICO, contract_purchaser, contract_purchaser_address,
							contract_supplier_ICO, contract_supplier, contract_supplier_address, contract_date_publication, contract_date_signed, contract_date_validity, contract_date_efficiency,
							contract_date_last_change, contract_price_final, contract_price_signed, contract_resort, contract_type, contract_state, contract_attachments])
	except:
		os.system('move '+working_dir+f+' '+corrupted_dir+f)
header = ['Nazov','ID','Inner-ID','Objednavatel_ICO','Objednavatel','Objednavatel_adresa','Dodavatel_ICO','Dodavatel','Dodavatel_adresa',
 			'Datum_zverejnenia','Datum_podpisu','Datum_platnosti','Datum_ucinnosti','Posledna_zmena','Cena_konecna','Cena_podpisana','Rezort','Typ','Stav','Prilohy']

table = np.asarray(table, dtype='object')
# Pandas export better to UTF-8 CSV than raw NumPy
pd.DataFrame(table).to_csv('CRZ_DB.csv', header = header, sep='|')