from TwitterSearch import TwitterSearchOrder, TwitterSearch
import geopandas
from crawler_keywords import words
from sentiment_analysis import sentiment_analyzer
from database import tweetsDB
       

zones = geopandas.read_file('./geo_data/target_zones.geojson')
zone_code = zones.loc[0,:].zone
search_lat = zones.loc[0,:].center_latitude
search_long = zones.loc[0,:].center_longitude
search_raidus = zones.loc[0,:].radius

db = tweetsDB()
sa = sentiment_analyzer.SentimentAnalyzer()

try:
    tso = TwitterSearchOrder() # create a TwitterSearchOrder object
    tso.set_keywords(words.get('vaccine')) # let's define all words we would like to have a look for
    tso.set_language('en') # we want to see German tweets only
    tso.set_include_entities(False) # and don't give us all those entity information
    tso.set_geocode(search_lat, search_long, search_raidus)
    #tso.set_count(10)

    # it's about time to create a TwitterSearch object with our secret tokens
    ts = TwitterSearch(
        consumer_key = "Ozup2OAf8pHZhha38AELtzswf",
        consumer_secret = "T0QCvEWdUm2PakSKDsho9usdvaPWZsUB0hhB2XE1JwgwCGp7wV",
        access_token = "1252083222189498368-BZUECSVoWd6IDSWGnETwH4krVS3AHh",
        access_token_secret = "y9UNO50rhFndcMPy4S4cY5qLEcZdz6NygWyl8t0ZY7H8s"
     )

     # this is where the fun actually starts :)
    for tweet in ts.search_tweets_iterable(tso):
		# Data to be written  
		dict ={  
		  "id": tweet['id'],  
		  "created_at": tweet['created_at'],
		  "text": tweet['text'],  
		  "zone_code": zone_code,
		  "senti_score" = sa.predict_sentiment(tweet['text'])
		}  			   
        #print( '@%s tweeted: %s' % ( tweet['user']['screen_name'], tweet['text'] ) )
		db.add_record(dict)
		
except TwitterSearchException as e: # take care of all those ugly errors if there are some
    print(e)