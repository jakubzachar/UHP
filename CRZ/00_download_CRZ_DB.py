# Matej Badin | UHP | 2019                                             |
# -------------------------------------------------------------------- |
# Packages needed :  urllib, zipfile, dateutil, datetime               |
# -------------------------------------------------------------------- |
# Crawler for downloading and categorizing dump from CRZ GOV database  |
# Downloads and categorizes every contract from now to given date      |
# -------------------------------------------------------------------- |

import urllib.request
import zipfile
import os

from datetime import date
from dateutil.rrule import rrule, DAILY
#úprava - aktualizácia dátumu
start_date = date(2011, 1, 1)
end_date   = date(2021, 6, 30)

dates      = []

for dt in rrule(DAILY, dtstart=start_date, until=end_date):
	dates.append(dt.strftime("%Y-%m-%d"))

print(len(dates))

for date in dates:
	print('Downloading date : '+date)

	# Download
	urllib.request.urlretrieve('http://www.crz.gov.sk//export/'+date+'.zip', date+'.zip')

	# Unzip
	zip_ref = zipfile.ZipFile(date+'.zip', 'r')
	zip_ref.extractall('')
	zip_ref.close()

	# Delete
	os.system('del '+date+'.zip')

