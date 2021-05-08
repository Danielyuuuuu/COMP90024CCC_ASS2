import sentiment_analyzer as sa

s = sa.SentimentAnalyzer()
text = 'i am super happy'
v = s.predict_sentiment(text)
print(text)
print(v)

text = 'Today is Tuesday'
v = s.predict_sentiment(text)
print(text)
print(v)

text = 'Today is Sunday'
v = s.predict_sentiment(text)
print(text)
print(v)

text = 'The dog has died'
v = s.predict_sentiment(text)
print(text)
print(v)