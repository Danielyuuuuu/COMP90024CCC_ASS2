# -*- coding: utf-8 -*-
"""
Created on Sun May  2 08:16:58 2021

@author: Windwalker
"""
from database_cloudant import CloudantDB
from cloudant.design_document import DesignDocument
from cloudant.view import View
db1 = CloudantDB("tweets_keywords")    # tweets in the specified location with keywords 
db2 = CloudantDB("tweets_no_keywords") # tweets in the sepcified locations without keyowrds
#db3 = CloudantDB("tweets_raw")         # raw tweet data in the specified locations
#print(len(db1.get_data()))
#print(db2.get_data(n=10000))
#print(len(db3.get_data(n=10)))



# get sentiment stats by zone
ddoc = DesignDocument(db2.curDB, '_design/ddoc001')
ddoc.fetch()
view = View(ddoc, 'view_zone')
summary = []
for row in view(group=True)['rows']:
    summary.append(row)
print(summary[0])
print()

# get all data from a specific day
date = "2021-01-01"
n = 100  # number of tweets need to retrieve
ddoc = DesignDocument(db2.curDB, '_design/ddoc001')
ddoc.fetch()
view = View(ddoc,"view_time")
data = []
for row in view(group=False,limit=n,reduce=False,key=date,include_docs=True)["rows"]:
    data.append(row)
print(data[0])
print()

# get sentiment stats by day
ddoc = DesignDocument(db2.curDB, '_design/ddoc001')
ddoc.fetch()
view = View(ddoc,"view_time")
sentiment_day = []
for row in view(group=True,reduce=True)["rows"]:
    sentiment_day.append(row)
print(sentiment_day[0])
print()

db1.close()
db2.close()
#db3.close()