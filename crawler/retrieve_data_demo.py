# -*- coding: utf-8 -*-
"""
Created on Sun May  2 08:16:58 2021

@author: Windwalker
"""
from database_cloudant import CloudantDB
from cloudant.design_document import DesignDocument
from cloudant.view import View

def get_data_summary(db="covid",viewType="month",startkey="2020-10",mode = "mean"):
    if(db=="covid"):
        db = CloudantDB('tweets_covid')
    elif(db=="vaccine"):
        db= CloudantDB("tweets_vaccine")
    elif(db=="no_keywords"):
        db=CloudantDB('tweets_no_keywords')
    else:
        print("db parameter must in [covid,vaccine,no_keywords]")
        return {}
    ddoc = DesignDocument(db.curDB,'_design/ddoc001')
    ddoc.fetch()
    if(viewType=="month"):
        view = View(ddoc, 'view_month')
    elif(viewType=="zone"):
        view = View(ddoc,"view_zone")
    else:
        view = View(ddoc, 'view_time')
    result = {}
    for row in view(limit=100,reduce=True,group=True,startkey=startkey)['rows']:
        if(mode=="mean"):
            result[row['key']] = round(row['value']['sum']/row['value']['count'],6)
        elif(mode=="count"):
            result[row['key']] = row['value']['count']
    return result

def get_data(n=100,db="covid",viewType="day",startkey="2021-05-01"):
    if(db=="covid"):
        db = CloudantDB('tweets_covid')
    elif(db=="vaccine"):
        db= CloudantDB("tweets_vaccine")
    elif(db=="no_keywords"):
        db=CloudantDB('tweets_no_keywords')
    else:
        print("db parameter must in [covid,vaccine,no_keywords]")
        return []
    ddoc = DesignDocument(db.curDB,'_design/ddoc001')
    ddoc.fetch()
    if(viewType=="zone"):
        view = View(ddoc,"view_zone")
    elif(viewType=="day"):
        view = View(ddoc, 'view_time')
    else:
        return "Does not support viewType"+viewType
    result = []
    for row in view(limit=n,reduce=False,group=False,startkey=startkey,include_docs=True)['rows']:
        result.append(row)
    return result

print("Covid mean sentiment score (by zone)")
print(get_data_summary(db="covid",viewType="zone",startkey=0,mode="mean"))
print()

print("Covid mean sentiment score (by month)")
print(get_data_summary(db="covid",viewType="month",startkey="2020-10",mode="mean"))
print()

print("Vaccine mean sentiment score (by day)")
print(get_data_summary(db="vaccine",viewType="day",startkey="2020-10-08",mode="mean"))
print()

print("Vaccine record count by month")
print(get_data_summary(db="vaccine",viewType="type",startkey="2020-10",mode="count"))
print()

print("Get 100 tweets related to Covid19 since 2021-05-01")
print(get_data(n=100,db="covid",viewType = "day", startkey="2021-05-01"))
print()

print("Get 100 tweets related to vacinne in Sydney")
print(get_data(n=100,db="vaccine",viewType = "zone", startkey="Sydney"))
print()