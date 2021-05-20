# -*- coding: utf-8 -*-
"""
Created on Wed May 19 00:40:53 2021

@author: Windwalker
"""
USERNAME='admin'
PASSWORD = 'password'
URL = 'http://172.26.131.97:5984'
from cloudant.client import CouchDB

class CloudantDB():
    def __init__(self,db_name,username = USERNAME,password=PASSWORD,url = URL):
        self.client = CouchDB(username, password, url=URL, connect=True)
        self.session = self.client.session()
        self.curDB = None
        print('Username: {0}'.format(self.session['userCtx']['name']))
        print('Databases: {0}'.format(self.client.all_dbs()))
        self.accessDB(db_name)
    
    def accessDB(self,db_name):
        if(db_name in self.client.all_dbs()):
            self.curDB = self.client[db_name]
        else:
            self.curDB = self.client.create_database(db_name)
            print("creating db:",db_name)
        if self.curDB.exists():
            print('Accessing db:',db_name)
    
    def add_record(self, json_record, db_name=None):
        hash_string = str(hash(json_record['id']))
        if(hash_string not in self.curDB):
            json_record['_id'] = hash_string
            record = json_record
            my_document = self.curDB.create_document(record)
            #if my_document.exists():
                #print('Adding record...SUCCESS!!')
        else:
            print("already exist")
    
    def update_record(self, recordID, data):
        if(recordID in self.curDB):
            doc = self.curDB(recordID)
            for k,v in data.items():
                doc[k]=v
            doc.save()
            return
        hash_string = str(hash(recordID))
        if(hash_string in self.curDB):
            doc = self.curDB(hash_string)
            for k,v in data.items():
                doc[k]=v
            doc.save()
            return
        else:
            print("record not found")
    
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
    
    def get_num_records(self):
        return len(self.curDB)
    
    def close(self):
        self.client.disconnect()
        
    def allDB(self):
        all_dbs = self.client.all_dbs()
        print('Databases: {0}'.format(all_dbs))
        return all_dbs
