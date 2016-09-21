import requests
import json
import csv
import time
import cStringIO
import codecs

#Takes a CSV of CfA staff who have ORCIDs...
orcidfile = open('cfa_orcids.csv')
orcidsread = csv.reader(orcidfile)

#Creates a list...
cfa_orcids = []

#And extracts the ORCIDs only from the CSV, adding them to the list
for row in orcidsread:
    if orcidsread.line_num == 1:
        continue
    cfa_orcids.append(row[3])

#UnicodeWriter stolen from Katie
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

#opens/creates a new CSV using UnicodeWriter, writes the header row
f = open('cfa_orcids_works.csv', 'wb')
writer = UnicodeWriter(f, dialect='excel', quoting=csv.QUOTE_ALL)
writer.writerow(["ORCID", "Work Number", "External ID", "External ID Type"])

#headers for ORCID API cURL request
headers= {
    'Content-Type': 'application/orcid+json',
    'Authorization': 'Bearer REDACTED',
}

#beginning and end of API request URL
urlbeg = 'https://pub.orcid.org/v1.2/'
urlend = '/orcid-works'

#here's the main part, and what it does line by line: cycles through individual ORCIDs in ORCID list created above; inserts ORCID into URL for API request; makes the API request, assigns them to variable "results;" converts / interprets as json; creates variable of results narrowed down to ORCID activities; if there is anything in that activities list, then continue; creates a variable "works," further drilling down from ORCID activities; assigns each list a number; if there is anything, then continue; isolates individual instances of external identifiers; isolates the individual ID; isolates the individual ID type; converts the list number to a string; prints everything to check for errors; then prints a row in the CSV; finally, wait a second and a half before doing the same thing for the next ORCID in the ORCID list.

for orcid in cfa_orcids:
    url = urlbeg+orcid+urlend
    results = requests.get(url, headers=headers)
    jsonresults = results.json()
    activities = jsonresults['orcid-profile']['orcid-activities']
    if activities:
        works = activities['orcid-works']['orcid-work']
        for worknum, result in enumerate(works):
            if result['work-external-identifiers']:
                for externalids in result['work-external-identifiers']['work-external-identifier']:
                    wexid = str(externalids['work-external-identifier-id']['value'].encode('utf-8'))
                    wexidtype = str(externalids['work-external-identifier-type'].encode('utf-8'))
                    strworknum = str(worknum)
                    print orcid, strworknum, wexid, wexidtype
                    writer.writerow([orcid]+[strworknum]+[wexid]+[wexidtype])
    time.sleep(1.5)

#don't forget to close the CSV!
f.close()