# -*- coding: utf-8 -*-
"""
Created on Sun May 23 20:12:04 2021

@author: Windwalker
"""
from database_cloudant import CloudantDB
from cloudant.design_document import DesignDocument
from cloudant.view import View
import sys

USERNAME='admin'
PASSWORD = 'password'
URL = 'http://172.26.131.97:5984'

def addViews(db):
    ddoc = DesignDocument(db.curDB,'_design/ddoc001')
    try:
        ddoc.add_view("view_zone",'function(doc){emit(doc.zone,parseFloat(doc.sentiment_score))}',"_stats")
        ddoc.add_view("view_time","function(doc){emit(doc.created_at.split(' ')[0], parseFloat(doc.sentiment_score))}","_stats")
        ddoc.add_view("view_month","function(doc){emit(doc.created_at.split(' ')[0].split('-').slice(0,2).join('-'), parseFloat(doc.sentiment_score))}","_stats")
        ddoc.add_view("view_zone_month","function(doc){emit(doc.created_at.split(' ')[0].split('-').slice(0,2).join('-').concat(' ',doc.zone), parseFloat(doc.sentiment_score))}","_stats")
        ddoc.save()
    except:
        ddoc.fetch()
    return ddoc

def main():
    args = sys.argv[1:]
    if(len(args)==3):
        username = args[0]
        password = args[1]
        url = args[2]
    else:
        username = USERNAME
        password = PASSWORD
        url=URL
    db_vac = CloudantDB('tweets_vaccine',username,password,url) 
    db_cov = CloudantDB("tweets_covid",username,password,url)
    db_all = CloudantDB("tweets_no_keywords",username,password,url)
    
    ddoc_vac = addViews(db_vac)
    ddoc_cov = addViews(db_cov)
    ddoc_all = addViews(db_all)
    """
    # Testing
    view = View(ddoc_cov, 'view_month')
    for row in view(limit=100,reduce=True,group=True,startkey="2020-10")['rows']:
        print(row)
    """

if __name__ == '__main__':
    main()


