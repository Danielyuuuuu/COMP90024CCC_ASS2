import tweepy
import json
from database import tweetsDB
consumer_key = "Ozup2OAf8pHZhha38AELtzswf"
consumer_secret = "T0QCvEWdUm2PakSKDsho9usdvaPWZsUB0hhB2XE1JwgwCGp7wV"
access_token = "1252083222189498368-BZUECSVoWd6IDSWGnETwH4krVS3AHh"
access_token_secret = "y9UNO50rhFndcMPy4S4cY5qLEcZdz6NygWyl8t0ZY7H8s"

GEOBOX_MELBOURNE = [144.877548, -37.851203, 145.031356, -
                    37.729655]  # https://boundingbox.klokantech.com/
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

# connect database
db = tweetsDB()

class MyStreamListener(tweepy.StreamListener):

    def on_status(self, status):
        if(status.place is not None):
            print("Text:----------------------\n   ", status.text)
            print("place:----------------------\n   ", status.place)
            print("-------Saving to the database-----------")
            db.add_record(status.text,status.place.full_name)
            print("-----------------------------------------------")

    def on_error(self, status_code):
        print(status_code)
        if status_code == 420:
            # returning False in on_error disconnects the stream
            return False

myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth, listener=myStreamListener)
myStream.filter(locations=GEOBOX_AUS, languages=["en"])