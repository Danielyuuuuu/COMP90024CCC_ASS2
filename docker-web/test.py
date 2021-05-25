
from cloudant.design_document import DesignDocument

USERNAME='admin'
PASSWORD = 'password'
URL = 'http://172.26.131.218:5984/'
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View
import pandas as pd

class CloudantDB():
    def __init__(self,db_name,username = USERNAME,password=PASSWORD,url = URL,partition=True):
        self.client = CouchDB(USERNAME, PASSWORD, url=URL, connect=True)
        self.session = self.client.session()
        self.curDB = None
        print('Username: {0}'.format(self.session['userCtx']['name']))
        print('Databases: {0}'.format(self.client.all_dbs()))
        self.accessDB(db_name,partition=True)
    
    def accessDB(self,db_name,partition=True):
        if(db_name in self.client.all_dbs()):
            self.curDB = self.client[db_name]
        else:
            self.curDB = self.client.create_database(db_name)
            print("creating db:",db_name)
        if self.curDB.exists():
            print('Accessing db:',db_name)
    
    def add_record(self, json_record, db_name=None, key=None):
        if(key is not None and key not in self.curDB):
            json_record['_id'] = key
            self.curDB.create_document(json_record)
        elif('id' in json_record.keys()):
            hash_string = str(hash(json_record['id']))
            if(hash_string not in self.curDB):
                json_record['_id'] = hash_string
                record = json_record
                self.curDB.create_document(record)
            else:
                print("already exist")
    
    def delete_record(self,recordID):
        if(recordID in self.curDB):
            my_document = self.curDB[recordID]
            my_document.delete()
        elif(str(hash(recordID)) in self.curDB):
            my_document = self.curDB[str(hash(recordID))]
            my_document.delete()
        else:
            print("deletion err, record not found")
    def delete_all_records(self):
        for doc in self.curDB:
            doc.delete()
    
    def deleteDB(self,db_name):
        self.client.delete_database(db_name)
        self.curDB = None
        print(db_name,"removed")
    
    def get_data(self,n=10000):
        data = []
        count = 0
        for document in self.curDB:
            data.append(document)
            count+=1
            if(count>n):
                break
        return data
    
    def close(self):
        self.client.disconnect()
        
    def allDB(self):
        all_dbs = self.client.all_dbs()
        print('Databases: {0}'.format(all_dbs))
        return all_dbs



db10 = CloudantDB("monthlytopwords")
data = db10.get_data()
lst = []

for month_data in data:
    month = month_data["_id"]
    for key in month_data:
        if key != "_id" and key!= "_rev":
            for word in month_data[key]:
                count = month_data[key][word]
                lst.append([month, key, word, count])
df = pd.DataFrame(lst)
df.columns = ["month", "zone", "word", "count"]
print(df["zone"].unique())

zones = ['Adelaide', 'Ballarat', 'Brisbane', 'Bunbury', 'Canberra', 'Geelong', 'Hobart', 'Melbourne', 'Newcastle', 'Perth', 'Sydney']

missing_zones = set(zones) - set(df["zone"].unique())

for zone in missing_zones:
    df.loc[zone] = ["2021-01", zone, "Null", 0]

print(df)