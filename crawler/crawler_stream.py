import tweepy
import json
from database import tweetsDB
from sentiment_analysis import sentiment_analyzer
#import geopandas
from crawler_keywords import words_arr
from zoneFeatures import zone_info, getBoundingbox
from TwitterProcessor import filtKeywords, filtLocations
import time

consumer_key = "Ozup2OAf8pHZhha38AELtzswf"
consumer_secret = "T0QCvEWdUm2PakSKDsho9usdvaPWZsUB0hhB2XE1JwgwCGp7wV"
access_token = "1252083222189498368-BZUECSVoWd6IDSWGnETwH4krVS3AHh"
access_token_secret = "y9UNO50rhFndcMPy4S4cY5qLEcZdz6NygWyl8t0ZY7H8s"
"""
zones = geopandas.read_file('./geo_data/target_zones.geojson')
zone_code = zones.loc[0,:].zone
zone_location=zones.loc[0,:].geometry.bounds

GEOBOX_MELBOURNE = [144.877548, -37.851203, 145.031356, -37.729655]  # https://boundingbox.klokantech.com/
GEOBOX_AUS = [106.8, -41.9, 154.9, -11.5]
"""

# connect twitter
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")

# connect database
#db = tweetsDB()
#sa = sentiment_analyzer.SentimentAnalyzer()
data=[]

class UserTimelineListener():
    def __init__(self,api,keywords,locations):
        self.searched = set()
        self.api = api
        self.keywords = keywords
        self.locations = locations
    def searchUser(self,userid):
        if(userid in self.searched):
            print("user has already been searched")
            return
        self.searched.add(userid)
        try:
            tweets = api.user_timeline(user_id=userid, count=100, exclude_replies=True,lang='en')
        except tweepy.TweepError:
            print("API error")
            time.sleep(16*60)
            return
        print("searching user:",userid,"filtering ",len(tweets)," tweets")
        for tweet in tweets:
            a = filtKeywords(tweet,self.keywords)
            if(a is None):
                continue
            a = filtLocations(tweet,self.locations)
            if(a is None):
                continue
            data.append(tweet)
            print("-----------new tweet found----------")
            

class MyStreamListener(tweepy.StreamListener):
    def __init__(self,keywords,userListener):
        super().__init__()
        self.keywords = keywords
        self.userListener = userListener

    def on_status(self, status):
        if(status.place is not None):
            
            a = filtKeywords(status,self.keywords)
            if(a is not None):
                data.append(status)
                print("-----------new tweet found----------")
            try:
                self.userListener.searchUser(status.user.id)
            except Exception as e:
                print(e)
                return
            

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False

box= getBoundingbox(zone_info["features"])
box_1d = [j for sub in box.values() for j in sub]

myUserListener = UserTimelineListener(api,words_arr,box.keys())
myStreamListener = MyStreamListener(words_arr,myUserListener)
myStream = tweepy.Stream(auth, listener=myStreamListener)
myStream.filter(locations=box_1d, languages=["en"])

