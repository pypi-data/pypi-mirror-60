import pandas as pd
import os
import requests
import json
import datetime
import time
from dateutil import tz
from pathlib import Path

class Response():
    def __init__(self, key, origlat, origlon, destlat, destlon, startime, date, tripid='', modes=None, allModes=False, bestOnly=False):
        self.tripid = tripid
        self.origlat = origlat
        self.origlon = origlon
        self.destlat = destlat
        self.destlon = destlon
        self.startime = startime
        self.orig = '(' + str(origlat) + ',' + str(origlon) + ')'
        self.dest = '(' + str(destlat) + ',' + str(destlon) + ')'
        self.startime = startime
        self.allModes = allModes
        self.bestOnly = bestOnly
        self.modes = modes if modes is not None else []
        self.startimeTimestamp = self.dateToTimestamp(date) + int(startime)*60 # for local use only
        self.fileExists = False
        self.usageExceeded = False
        self.parameters = self.create_parameters()
        self.headers = {'X-TripGo-Key': key}
    
    def create_parameters(self):
        parameters = \
            {
                'v': 11,
                'from': self.orig,
                'to': self.dest,
                'departAfter': int(self.startimeTimestamp),
                'bestOnly': self.bestOnly
            }
        
        if len(self.modes) != 0:
            parameters.update({'modes': self.modes})
        else:
            parameters.update({'allModes': True})

        return parameters

    def fetch(self):
        while True:
            try:
                results = requests.get('https://api.tripgo.com/v1/routing.json',
                                         params=self.parameters,
                                         headers=self.headers)
                data = results.json()
                print('Successful fetch from %s' % (results.url))
                self.checkUsageLimit(data)

                if self.usageExceeded:
                    print('Error: API usage exceeded. Waiting 60 seconds...')
                    time.sleep(60)
                    continue

                return data

            except Exception as e:
                print("Error: " + str(e.message))
                print("Retrying in 5...")
                time.sleep(5)
                continue

    def save(self, destination_folder, unique_id=''):
        directory = self.dir_path(destination_folder)
        path, id, file_exists = self.file_path(directory, unique_id)

        if file_exists:
            print('File {} already exists.'.format(str(id)))
        else:
            data = self.fetch()

            with open(path, 'w') as f:
                json.dump(data, f)

        return True

    def dir_path(self, destination_folder):
        cwd = os.getcwd()
        directory = os.path.join(cwd, destination_folder)
        dirExists = os.path.exists(directory)

        if not dirExists:
            os.mkdir(destination_folder)

        return directory

    def file_path(self, directory, unique_id=''):
        md = '-'.join(self.modes) if self.modes is not [] else ''

        if unique_id == '' and self.tripid == '':
            olt = self.origlat[-4:]
            oln = self.origlon[-4:]
            dlt = self.destlat[-4:]
            dln = self.destlon[-4:]
            unique_id = '{}-{}-{}-{}-{}{}.json'.format(olt, oln, dlt, dln, self.startime, md)

        elif unique_id == '' and self.tripid != '':
            if self.modes == []:
                unique_id = '{}-{}.json'.format(self.tripid, self.startime)
            else:
                unique_id = '{}-{}-{}.json'.format(self.tripid, self.startime, md)

        else:
            unique_id = ''.join([unique_id, '.json'])

        path = os.path.join(directory, unique_id)
        pathExists = os.path.exists(path)

        return path, unique_id, pathExists

    def dateToTimestamp(self, dateString):
        dateArray = dateString.split('/')
        dateArray = [int(i) for i in dateArray]
        currentYear = datetime.datetime.now().year
        timestamp = datetime.datetime(currentYear + 1, dateArray[1], dateArray[0], tzinfo=tz.tzlocal()).timestamp()

        return int(timestamp)

    def checkUsageLimit(self, data):
        try:
            if 'usage' in data['error']:
                self.usageExceeded = True
        except:
            self.usageExceeded = False

# def getMissingModes(parsed_csv, vista_csv):
#
#     modeChoices = \
#     {
#         'car': 'me_car',
#         'transit': 'pt_pub',
#         'taxi': 'ps_tax',
#         'walking': 'wa_',
#         'cycling': 'cy_'
#     }
#
#     csv = parsed_csv
#     vista = vista_csv
#
#     for i in range(len(csv)):
#         car = int(csv.car[i])
#         transit = int(csv.transit[i])
#         taxi = int(csv.taxi[i])
#         walking = int(csv.walking[i])
#         cycling = int(csv.cycling[i])
#
#         tripid = csv.tripid[i]
#         startime = csv.startime[i]
#
#         match = vista.loc[(vista['tripid'] == tripid) & (vista['startime'] == startime)]
#         orig = {'lat': match.origlat.item(), 'lon': match.origlon.item()}
#         dest = {'lat': match.destlat.item(), 'lon': match.destlon.item()}
#         date = match.travdate.item()
#
#         if car == 0:
#             response(tripid, orig['lat'], orig['lon'], dest['lat'], dest['lon'], startime, date, mode='me_car', bestOnly=True).save()
#             print('saved')
            
if __name__ == '__main__':
    path = Path('~/Documents/Work/VISTA/2014-16.csv')
    csv = pd.read_csv(path)
    i = 20
    test = Response('3c564f8530bc1b3835a42ce3e89b7c44', 
                    csv.tripid[i], 
                    '-37.826118' , 
                    '145.201767', 
                    '-37.817800', 
                    '145.018510', 
                    csv.startime[i], 
                    csv.travdate[i], 
                    modes=['me_car', 'pt_pub'], 
                    bestOnly=True).save('Test')


    
    
    
