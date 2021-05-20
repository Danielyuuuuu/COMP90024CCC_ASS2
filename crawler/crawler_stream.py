import tweepy
import json
import sys
#from database import tweetsDB
from database_cloudant import CloudantDB
from sentiment_analysis import sentiment_analyzer
#import geopandas
from crawler_keywords import words_arr
from zoneFeatures import zone_info, getBoundingbox
from TwitterProcessor import filtKeywords, filtLocations, parseTweet
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
USERNAME='admin'
PASSWORD = 'password'
URL = 'http://172.26.131.97:5984'
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
    # connect database
    db = CloudantDB("tweets_keywords",username,password,url)
    db_all = CloudantDB("tweets_no_keywords",username,password,url)
    db_raw = CloudantDB("tweets_raw",username,password,url)
    sa = sentiment_analyzer.SentimentAnalyzer()
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
                tweets = self.api.user_timeline(user_id=userid, count=100, exclude_replies=True,lang='en')
            except tweepy.TweepError:
                print("API error")
                time.sleep(16*60)
                return
            print("searching user:",userid,"filtering ",len(tweets)," tweets")
            for tweet in tweets:
                zone = filtLocations(tweet,self.locations)
                if(zone is None):
                    continue
                db_raw.add_record(tweet._json)
                db_all.add_record(parseTweet(tweet,sa,zone,["no keywords"]))
                words = filtKeywords(tweet,self.keywords)
                if(words is None):
                    continue
                record = parseTweet(tweet,sa,zone,words)
                data.append(record)
                print("---new tweet found----- keywords:",words,"zone",zone)
                db.add_record(record)
                print("saved to database")
                
    
    class MyStreamListener(tweepy.StreamListener):
        def __init__(self,keywords,locations,userListener):
            super().__init__()
            self.keywords = keywords
            self.userListener = userListener
            self.locations = locations
        def on_status(self, status):
            if(status.place is not None):
                zone = filtLocations(status,self.locations)
                if(zone is not None):
                    db_raw.add_record(status._json)
                    db_all.add_record(parseTweet(status,sa,zone,["no keywords"]))
                words = filtKeywords(status,self.keywords)
                if(words is not None and zone is not None):
                    record = parseTweet(status,sa,zone,words)
                    data.append(record)
                    print("---new tweet found----- keywords:",words,"zone",zone)
                    db.add_record(record)
                    print("saved to database")
                try:
                    self.userListener.searchUser(status.user.id)
                except Exception as e:
                    print(e)
                    return
    
        def on_error(self, status_code):
            print(status_code)
            if status_code == 420:
                # returning False in on_error disconnects the stream
                time.sleep(60)
                return False

    
    # connect twitter
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
    
    try:
        api.verify_credentials()
        print("Authentication OK")
    except:
        print("Error during authentication")
    


    box= getBoundingbox(zone_info["features"])
    box_1d = [j for sub in box.values() for j in sub]
    
    myUserListener = UserTimelineListener(api,words_arr,box.keys())
    myStreamListener = MyStreamListener(words_arr,box.keys(),myUserListener)
    while True:
        try:
            myStream = tweepy.Stream(auth, listener=myStreamListener)
            myStream.filter(locations=box_1d, languages=["en"])
        except Exception as e:
            time.sleep(5)
            print(e)

if __name__ == '__main__':
    main()
    """
    with open('data_streaming.json', 'w') as outfile:
        json.dump(data, outfile)
    
    
    import jsonlines
    with jsonlines.open('data_streaming.jsonl', mode='a') as writer:
        for d in data:
            writer.write(d)
    """
