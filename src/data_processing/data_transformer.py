import pandas as pd
from textblob import TextBlob
import logging
from typing import Dict

class DataTransformer:
    """Transforms and enriches tweet data with sentiment analysis."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def clean_tweets(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicates and clean tweet data."""
        try:
            df = df.drop_duplicates(subset=['text'])
            return df.reset_index(drop=True)
        except Exception as e:
            self.logger.error(f"Error cleaning tweets: {str(e)}")
            raise

    def add_sentiment_analysis(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add sentiment scores to tweets."""
        try:
            df['sentiment'] = df['text'].apply(
                lambda x: TextBlob(x).sentiment.polarity
            )
            return df
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            raise

    def transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df = self.clean_tweets(df)
        df = self.add_sentiment_analysis(df)
        return df