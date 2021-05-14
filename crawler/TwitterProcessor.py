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

def parseTweet(status,analyzer,zone_name,keywords):
    if(status.place is not None):
        p = {'type':status.place.place_type,
             'name':status.place.name,
             'fullname':status.place.full_name,
             'bounding_box':str(status.place.bounding_box.coordinates)
             }
    else:
        p = {'type':'',
             'name':'',
             'fullname':'',
             'bounding_box':''
             }
    sentiment = analyzer.predict_sentiment(status.text)
    tweet_json = {'id':status.id,
                 'created_at':str(status.created_at),
                 'text':status.text,
                 "place":p,
                 'sentiment_score':str(sentiment[0]),
                 "sentiment":sentiment[1],
                 'zone':zone_name,
                 "keywords":' '.join(keywords)}
    return tweet_json