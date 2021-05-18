# -*- coding: utf-8 -*-
"""
Created on Sun May  2 08:16:58 2021

@author: Windwalker
"""
from database_cloudant import CloudantDB
db1 = CloudantDB("tweets_keywords")
db2 = CloudantDB("tweets_no_keywords")
db3 = CloudantDB("tweets_raw")
print(len(db1.get_data()))
print(len(db2.get_data()))
print(len(db3.get_data()))
db1.close()
db2.close()
db3.close()
