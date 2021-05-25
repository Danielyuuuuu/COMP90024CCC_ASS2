import os
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View
from collections import Counter
from datetime import datetime, timedelta
from threading import Timer
import sys
env_path = Path('./ip.env')
load_dotenv(dotenv_path=env_path, verbose=True)

URL = os.getenv("URL")



USERNAME=os.getenv("USERNAME")

PASSWORD = os.getenv("PASSWORD")






class CloudantDB():
    def __init__(self, db_name, username=USERNAME, password=PASSWORD, url=URL, partition=True):
        self.client = CouchDB(USERNAME, PASSWORD, url=URL, connect=True)
        self.session = self.client.session()
        self.curDB = None
        print('Username: {0}'.format(self.session['userCtx']['name']))
        print('Databases: {0}'.format(self.client.all_dbs()))
        self.accessDB(db_name, partition=True)

    def accessDB(self, db_name, partition=True):
        if (db_name in self.client.all_dbs()):
            self.curDB = self.client[db_name]
        else:
            self.curDB = self.client.create_database(db_name)
            print("creating db:", db_name)
        if self.curDB.exists():
            print('Accessing db:', db_name)

    def add_record(self, json_record, db_name=None, key=None):
        if (key is not None and key not in self.curDB):
            json_record['_id'] = key
            self.curDB.create_document(json_record)
        elif ('id' in json_record.keys()):
            hash_string = str(hash(json_record['id']))
            if (hash_string not in self.curDB):
                json_record['_id'] = hash_string
                record = json_record
                self.curDB.create_document(record)
            else:
                print("already exist")
        elif ('_id' in json_record.keys()):
            if (json_record['_id'] not in self.curDB):
                self.curDB.create_document(json_record)

    def delete_record(self, recordID):
        if (recordID in self.curDB):
            my_document = self.curDB[recordID]
            my_document.delete()
        elif (str(hash(recordID)) in self.curDB):
            my_document = self.curDB[str(hash(recordID))]
            my_document.delete()
        else:
            print("deletion err, record not found")

    def delete_all_records(self):
        for doc in self.curDB:
            doc.delete()

    def deleteDB(self, db_name):
        self.client.delete_database(db_name)
        self.curDB = None
        print(db_name, "removed")

    def get_data(self, n=10000):
        data = []
        count = 0
        for document in self.curDB:
            data.append(document)
            count += 1
            if (count > n):
                break
        return data

    def close(self):
        self.client.disconnect()

    def allDB(self):
        all_dbs = self.client.all_dbs()
        print('Databases: {0}'.format(all_dbs))
        return all_dbs


from nltk.tokenize import TweetTokenizer
from nltk.corpus import stopwords


def top_words(textlist, top=10):
    stop_words = stopwords.words('english')
    wordfreqdict = Counter()
    popular = []
    tokenizer = TweetTokenizer()

    for t in textlist:
        token = tokenizer.tokenize(t)
        for w in token:
            if len(w) >= 5 and w not in stop_words:
                wordfreqdict[w] += 1

    return wordfreqdict.most_common(top)


def add_months(month):
    start = month + "-01 00:00:00"
    newyear = False
    if month[-2:] == "12":
        endmonth = "01"
        newyear = True
    elif month[-2:] == "11":
        endmonth = "12"
    elif month[-2:] == "10":
        endmonth = "11"
    elif month[-2:] == "09":
        endmonth = "10"
    else:
        endmonth = "0" + str(1 + int(month[-1]))
    end = month[:-2] + endmonth + "-01 00:00:00"
    if newyear:
        end = month[:-4] + str(1 + int(month[3])) + "-" + endmonth + "-01 00:00:00"
    return start, end


def city_daily_popular_10words(tweetlist, startmonth='2021-01'):
    (start, end) = add_months(startmonth)
    city = ["Sydney", "Newcastle", "Canberra", "Melbourne", "Ballarat", "Geelong", "Hobart", "Perth", "Brisbane",
            "Adelaide"]
    alltext = {}
    month = []
    startlist = []
    endlist = []
    for m in range(12):
        month.append(start[:7])
        startlist.append(start)
        endlist.append(end)
        (start, end) = add_months(end[:7])
    for m in month:
        toplist = {}
        for c in city:
            toplist[c] = []

        alltext[m] = toplist

    for k in tweetlist:

        # print(k["doc"]['created_at'])
        for s in range(len(startlist)):
            start = startlist[s]
            end = endlist[s]
            if k["doc"]['created_at'] <= end and k["doc"]['created_at'] > start:
                for c in city:
                    if k["doc"]["zone"] == c:
                        alltext[month[s]][c].append(k["doc"]["text"])
    popdict = {}
    for m in month:
        worddict = {}
        for c in city:
            worddict[c] = dict(top_words(alltext[m][c]))
        popdict[m] = worddict
    return popdict


def get_data(n=100, db="covid", viewType="day", startkey="2021-05"):
    if (db == "covid"):
        db = CloudantDB('tweets_covid')
    elif (db == "vaccine"):
        db = CloudantDB("tweets_vaccine")
    elif (db == "no_keywords"):
        db = CloudantDB('tweets_no_keywords')

    else:
        print("db parameter must in [covid,vaccine,no_keywords]")
        return []
    ddoc = DesignDocument(db.curDB, '_design/ddoc001')
    ddoc.fetch()
    if (viewType == "zone"):
        view = View(ddoc, "view_zone")
    elif (viewType == "day"):
        view = View(ddoc, 'view_time')
    elif (viewType == "month"):
        view = View(ddoc, 'view_month')
    else:
        return "Does not support viewType" + viewType
    result = []
    for row in view(limit=n, reduce=False, group=False, startkey=startkey, include_docs=True)['rows']:
        result.append(row)
    return result


def job2():
    # update files in monthlytopwords
    tweetlist = get_data(n=4000000, db="no_keywords", viewType="zone")
    x = datetime.today()

    monthstr=str(x.month)
    if len(monthstr)==1:
        monthstr="0"+monthstr

    startmonth = str(x.year)[:-1]+str(int(str(x.year)[-1])-1)+"-"+monthstr


    cdict = city_daily_popular_10words(tweetlist, startmonth=startmonth)

    db10 = CloudantDB("monthlytopwords")
    for i in cdict:
        db10.add_record(cdict[i], key=i)
    #print(db10.get_data())
    return


if __name__ == '__main__':

    x = datetime.today()
    y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0) + timedelta(days=1)
    delta_t = y - x

    secs = delta_t.total_seconds()

    t = Timer(secs, job2)
    #job2()
    t.start()

