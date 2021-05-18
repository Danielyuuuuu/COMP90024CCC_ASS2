# -*- coding: utf-8 -*-
"""
Created on Sun May  2 08:16:58 2021

@author: Windwalker
"""
from database import tweetsDB
db = tweetsDB("tweets_all")
db1 = tweetsDB("tweets_keywords")
print(db1.get_num_record())
# retrieve the first 5 record in the database
data = db1.get_data(from_index=0,to_index=5,get_all=False)
print(data[0])

