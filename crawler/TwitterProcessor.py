# -*- coding: utf-8 -*-
"""
Created on Fri May 14 09:26:32 2021

@author: Windwalker
"""
import re

def filtKeywords(status,keywords):
    text = status.text
    tokens = re.sub(r'[^a-zA-Z0-9-]', ' ', text).lower().split()
    words = []
    for word in tokens:
        if(word in keywords):
            words.append(word)
    
    if(words):
        return words
    return None

def filtLocations(status, locations):
    place = status.place
    zone = None
    if(place is None):
        return None
    else:
        place = status.place.full_name.lower()
        for l in locations:
            if(re.search(l.lower(),place.lower()) is not None):
                zone = l
    if(zone is not None):
        return zone
    return None