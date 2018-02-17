import celeryconfig
from celery import Celery
from celery import task

import requests, zipfile, StringIO
import csv
import redis
from datetime import date

stockapp = Celery('tasks')
stockapp.config_from_object(celeryconfig)
stockapp.autodiscover_tasks()

# Connecting to redis server
conn = redis.Redis(host='redis', port=6379, db=0)

# Getting latest and previous key if any
latest_key = conn.hget('latest', 'current')
previous = conn.hget('latest', 'previous')

# Deleting previous data
def delete_previous_data():
    # if previous is not none and if previous is not same as latest
    if previous is not None and previous != latest_key:
        previous_keys = conn.keys(previous + "*")
        conn.delete(*previous_keys)
    else:
        print "previous data is None, ignoring data deletion"

# function to parse CSV file and store the records in hash with score in sortedsets
def parse_csv(latest_key):
    csvfilename = latest_key + ".CSV"
    sortedset_key = latest_key + ":sortedset"

    with open(csvfilename, 'r') as csvfile:
        reader = csv.DictReader( csvfile )
        for line in reader:
            record = {
                'code': line['SC_CODE'],
                'name': line['SC_NAME'],
                'open': line['OPEN'],
                'high': line['HIGH'],
                'low': line['LOW'],
                'close': line['CLOSE']
            }
            set_key = latest_key + ":" + record['name']
            set_key = set_key.strip()
            # Entire record is stored in hash for quick access
            conn.hmset(set_key, record)
            # difference of close and high is calculated to use as a score
            diff = float(record['close']) - float(record['open'])
            # adding name with diff score calculated in sortedset
            conn.zadd(sortedset_key, set_key, diff)

    # saving some metadata in redis to fetch always latest data
    prev = conn.hget('latest', 'date')
    conn.hset('latest', 'date', latest_key)
    conn.hset('latest', 'previous', prev)

'''    
This function downloads bhavcopy zip file from BSE and extract it and call parsecsv function to store it in redis
This function acts as a task that run at 4PM daily (since BSE closes at around 3:30-3:40)
'''
@stockapp.task
def daily_task_to_schedule():
    today = date.today()
    latest_key = "EQ" + today.strftime('%d%m%y')
    zipfilename = latest_key + "_CSV"
    url = "https://www.bseindia.com/download/BhavCopy/Equity/" + zipfilename + ".ZIP"
    r = requests.get(url, stream=True)
    if r.ok:
        z = zipfile.ZipFile(StringIO.StringIO(r.content))
        fn = z.extractall()
        parse_csv(latest_key)
        delete_previous_data()
    else:
        print "New zip file is not yet available."

# init function to manually push CSV file in redis (for first time)
def init(key='EQ160218'):
    conn.flushdb()
    parse_csv(key)
    conn.hset('latest', 'date', key)
    # initialize celery to schedule it to daily

# called only when it is triggered as python tasks.py
if __name__ == '__main__':
    init()