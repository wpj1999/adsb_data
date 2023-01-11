from contextlib import closing
from urllib.request import urlopen
import json
import time
import datetime
import csv

url = "http://192.168.10.10/tar1090/data/aircraft.json"
now = datetime.datetime.now()
today = now.strftime("%Y-%m-%d")


while True:
    time.sleep(1)
    try:
        if today != now.strftime("%Y-%m-%d"):
            today = now.strftime("%Y-%m-%d")
        else:
            with closing(urlopen(url, None, 5.0)) as aircraft_file:
                aircraft_data = json.load(aircraft_file)
                for a in aircraft_data['aircraft']:
                    now_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    with open('./' + today + '.csv', 'a', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow([now_time, a])
                    f.close()
    except:
        pass