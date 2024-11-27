import pandas as pd
from textblob import TextBlob

class DataTransformer:
    def __init__(self):
        pass
    
    def clean_tweets(self, df):
        # Remove duplicates
        df = df.drop_duplicates(subset=['text'])
        
        # Reset index
        df = df.reset_index(drop=True)
        
        return df
    
    def add_sentiment_analysis(self, df):
        def get_sentiment(text):
            return TextBlob(text).sentiment.polarity
        
        df['sentiment'] = df['text'].apply(get_sentiment)
        return df
    
    def transform_data(self, df):
        df = self.clean_tweets(df)
        df = self.add_sentiment_analysis(df)
        return df 