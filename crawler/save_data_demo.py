# -*- coding: utf-8 -*-
"""
Created on Tue May 18 22:27:55 2021

@author: Windwalker
"""
#import jsonlines
from database_cloudant import CloudantDB
from cloudant.design_document import DesignDocument
db1 = CloudantDB("test")
db1.add_record({"word1":{"asdfasdf":"123","123":"qewrqwer"},"word2":"value2","area":[1,2,3]},key="2020-02-03")
db1.add_record({"word1":123,"area":[1,2,3]},key="2020-02-02")

print(db1.curDB["2020-02-03"])
print()
print(db1.get_data())
db1.deleteDB('test')