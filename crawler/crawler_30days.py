# -*- coding: utf-8 -*-
"""
Created on Sun May  9 23:49:45 2021

@author: Windwalker
"""
import tweepy
import json
from database import tweetsDB
import tweepy
from zoneFeatures import zones
from datetime import datetime
import dateutil.relativedelta
from sentiment_analysis import sentiment_analyzer

consumer_key = "Ozup2OAf8pHZhha38AELtzswf"
consumer_secret = "T0QCvEWdUm2PakSKDsho9usdvaPWZsUB0hhB2XE1JwgwCGp7wV"
access_token = "1252083222189498368-BZUECSVoWd6IDSWGnETwH4krVS3AHh"
access_token_secret = "y9UNO50rhFndcMPy4S4cY5qLEcZdz6NygWyl8t0ZY7H8s"


GEOBOX_MELBOURNE = [144.877548, -37.851203, 145.031356, -37.729655]  # https://boundingbox.klokantech.com/
GEOBOX_AUS = [106.8, -41.9, 154.9, -11.5]

# connect twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# example_point_radius =['144.960578', '-37.826401', '25km']
# example_boundingbox = [144.934966,-37.839254,144.990447,-37.803238]


sa = sentiment_analyzer.SentimentAnalyzer()

def processPage(page,zone_name,keywords,save_to_db,return_data,db_name='tweet_zone_sentiment'):
    db = tweetsDB(db_name)
    result = []
    count = 0
    for tweet in page:
        sentiment = sa.predict_sentiment(tweet.text)
        tweet_json = {'id':tweet.id,
                      'created_at':str(tweet.created_at),
                      'text':tweet.text,
                      "place":{'type':tweet.place.place_type,
                               'name':tweet.place.name,
                               'fullname':tweet.place.full_name,
                               'bounding_box':str(tweet.place.bounding_box.coordinates)
                               },
                      'sentiment_score':str(sentiment[0]),
                      "sentiment":sentiment[1],
                      'zone':zone_name,
                      'keywords':" ".join(list(map(str,keywords)))}
        if(return_data):
            result.append(tweet_json)
        if(save_to_db):
            db.add_record(tweet_json)
        count += 1
    return result, count


def search(keywords=[],point_radius=[],boundingbox=[],
           from_date='', n=200, results_per_page=100,zone_name='',
           save_to_db = True, return_data = True,db_name='tweet_zone_sentiment'):
    # n is the total number of tweets need to search
    # results_per_page should between 10-100
    # point_radius should be of format: [lon lat radius], radius should be less than 40km
    # bounding_box: [west_long south_lat east_long north_lat]
    query = "lang:en "
    from_date=''
    count=0
    if(zone_name in zones.keys()):
        point_radius = zones[zone_name]
    try:
        if (keywords):
            assert type(keywords)==list,"keywords should be a list of string"
            query += " ".join(list(map(str,keywords)))
        if (point_radius):
            assert len(point_radius)==3, "point_radius should be of type [lon,lat,radius]"
            query += " point_radius:["+ " ".join(list(map(str,point_radius)))+"]"
        if (boundingbox):
            assert len(boundingbox)==4, "bounding_box should be of type:[west_long south_lat east_long north_lat]"
            query += " bounding_box:["+ " ".join(list(map(str,boundingbox))) +"]"
        if (not from_date):
            d= datetime.now() + dateutil.relativedelta.relativedelta(days=-29)
            from_date = '%d%02d%02d%02d%02d'%(d.year,d.month,d.day,d.hour,d.minute)
        data = []
        page_count = 0
        for page in tweepy.Cursor(api.search_30_day, environment_name='comp90024',
                                  query=query,fromDate=from_date,
                                  maxResults=results_per_page).pages():
            
            result, c = processPage(page,zone_name,keywords,save_to_db,return_data,db_name)
            if(return_data):
                data += result

            page_count += 1
            count += c
            print('processing page:',page_count, "number of tweets:", count,"zone:",zone_name)
            if(count>=n):
                break
        return data
    except AssertionError as e:
        print(e)
        return 
    except tweepy.TweepError as e:
        print(e)
        return

for zone, pr in zones.items():
    data = search(db_name='tweet_zone_sentiment',zone_name=zone)

"""
vaccine=['jab','vaccine','vaccination','AstraZeneca','Pfizer-BioNTech','vacc']
lockdown=['lockdown']
for word in vaccine:
    for zone in zones.keys():
        data = search(keywords=[word] ,db_name="tweet_keyword_sentiment",zone_name=zone, n=100)
"""






