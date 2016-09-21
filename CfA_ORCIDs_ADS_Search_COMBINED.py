import ads
import csv
import time
import cStringIO
import codecs

#UnicodeWriter makes writing to csv go a bit more smoothly
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

#creates a new csv file to write to
f = open('orcid_bibcodes_complete.csv', 'wb')


#opens the csv using UnicodeWriter
writer = UnicodeWriter(f, dialect='excel', quoting=csv.QUOTE_ALL)

#ADS token redacted - enter in yours between the quote marks
ads.config.token = ''

#opens another csv, which contains a list of ORCID iDs and works from cfa_orcids, and creates a dictionary for each row
with open('cfa_orcids_works2.csv') as worksfile:
    reader = csv.reader(worksfile)
    works = [row for row in reader]

#for each row, checks to see if the external identifer is an ADS bibcode, DOI, or ARXIV id. If so, it searches the CfA Bibliography in ADS for that external ID and returns the bibcode and writes it all to the csv
for work in works:
    if work[3] == "BIBCODE" or "DOI" or "ARXIV":
        exid = work[2]
        ads_works = ads.SearchQuery(identifier=exid, bibgroup="CFA", fl=['bibcode'])
        for ads_work in ads_works:
            bibcode = ads_work.bibcode
            utfbibcode = bibcode.encode('utf-8')
            if bibcode:
                work.append(utfbibcode)
    time.sleep(0.2)
    writer.writerow(work)

#closes the csv
f.close()