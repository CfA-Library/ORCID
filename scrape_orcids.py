#simple web scraper to retrieve ORCIDs from Wolbach's ORCID webpage

import requests
from bs4 import BeautifulSoup
import csv
import cStringIO
import codecs

#UnicodeWriter stolen from Katie - makes csv writing run more smoothly
class UnicodeWriter:
    def __init__(self, f, dialect=csv.excel, encoding="utf-8-sig", **kwds):
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()
    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
			
#creates a new csv to write to
fileout = codecs.open('wolbach_orcids_uni.csv','wb')
wr = UnicodeWriter(fileout,lineterminator='\n', delimiter='|', dialect='excel',quoting=csv.QUOTE_ALL)

#retrieves web content from Wolbach's ORCID page
url = "http://library.cfa.harvard.edu/orcidid"
page = requests.get(url)
html = page.content

#soupifies it and finds the table in the page
soup = BeautifulSoup(html)
orcid_table = soup.find('table')

#creates an array, and then drills down within the table to find each cell, which it appends to the array
orcrows = []
for row in orcid_table.findAll('tr'):
    orccells = []
    for cell in row.findAll('td'):
        text = cell.text
        orccells.append(text)
    orcrows.append(orccells)

#writes the array to the csv file
wr.writerows(orcrows)
fileout.close()