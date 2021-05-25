# -*- coding: utf-8 -*-
"""
Created on Wed May 19 00:40:53 2021

@author: Windwalker
"""
USERNAME='admin'
PASSWORD = 'password'
URL = 'http://172.26.131.97:5984'
from cloudant.client import CouchDB
from cloudant.design_document import DesignDocument
from cloudant.view import View

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
"""
reduce_func = "function(key, values, rereduce) {var result = 0;for(var i = 0; i < values.length; i++){value = parseFloat(values[i]);result+=value;}return result.toString();}"
db2 = CloudantDB("tweets_no_keywords")

ddoc = DesignDocument(db2.curDB, '_design/ddoc001')
ddoc.fetch()
ddoc.add_view("view_zone",'function(doc){emit(doc.zone,parseFloat(doc.sentiment_score))}',"_stats")
ddoc.save()

view = View(ddoc, 'view_zone')
# Assuming that 'view001' exists as part of the
# design document ddoc in the remote database...
# Use view as a callable
for row in view(limit=100,group=True)['rows']:
    print(row)
for view_name, view in ddoc.iterviews():
    print("------",view_name,view)

db2 = CloudantDB("tweets_no_keywords")
ddoc = DesignDocument(db2.curDB,'_design/ddoc001')
ddoc.fetch()
ddoc.add_view("view_time","function(doc){emit(doc.created_at.split(' ')[0], parseFloat(doc.sentiment_score))}","_stats")
ddoc.save()
view = View(ddoc, 'view_time')
for row in view(limit=100,reduce=True,group=True)['rows']:
    print(row)
"""