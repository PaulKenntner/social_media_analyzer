from typing import List, Dict
import tweepy
from datetime import datetime
import logging
from src.config.config_loader import get_twitter_config
from src.database.db_handler import DatabaseHandler

class GermanPoliticsCollector:
    """Collects tweets from German political discourse using Twitter's API."""
    
    POLITICAL_KEYWORDS = [
        'Bundestag', 'Bundesregierung',
        'CDU', 'SPD', 'Grüne', 'FDP', 'AfD', 'Linke',
        'Scholz', 'Merz', 'Baerbock', 'Lindner',
        'Deutsche Politik', 'Bundestagswahl'
    ]

    POLITICAL_ACCOUNTS = [
        'Bundestag',
        'RegSprecher',
        'CDU',
        'spdde',
        'Die_Gruenen',
        'fdp',
    ]

    def __init__(self) -> None:
        """Initialize collector with Twitter API credentials."""
        try:
            config = get_twitter_config()
            self.client = tweepy.Client(
                bearer_token=config['bearer_token'],
                consumer_key=config['api_key'],
                consumer_secret=config['api_secret'],
                access_token=config['access_token'],
                access_token_secret=config['access_token_secret'],
                wait_on_rate_limit=True
            )
            self.logger = logging.getLogger(__name__)
        except KeyError as e:
            raise ValueError(f"Missing required configuration: {e}")

    def search_political_tweets(self, max_results: int = 100) -> List[Dict]:
        """Search for recent German political tweets."""
        query = ' OR '.join(self.POLITICAL_KEYWORDS) + ' lang:de'
        
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'lang']
            )
            
            if not tweets.data:
                self.logger.warning("No tweets found for query")
                return []

            return [{
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'metrics': tweet.public_metrics,
                'collected_at': datetime.now()
            } for tweet in tweets.data]

        except tweepy.TweepyException as e:
            self.logger.error(f"Twitter API error: {str(e)}")
            return []

    def get_political_accounts_tweets(self, max_results: int = 50) -> List[Dict]:
        """Collect recent tweets from major German political accounts."""
        all_tweets = []
        
        for account in self.POLITICAL_ACCOUNTS:
            try:
                user = self.client.get_user(username=account)
                if not user.data:
                    self.logger.warning(f"Could not find user: {account}")
                    continue

                tweets = self.client.get_users_tweets(
                    id=user.data.id,
                    max_results=max_results,
                    tweet_fields=['created_at', 'public_metrics', 'lang']
                )
                
                if tweets.data:
                    all_tweets.extend([{
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'metrics': tweet.public_metrics,
                        'account': account,
                        'collected_at': datetime.now()
                    } for tweet in tweets.data])

            except tweepy.TweepyException as e:
                self.logger.error(f"Error collecting tweets for {account}: {e}")
                continue

        return all_tweets

    def collect_and_store(self) -> None:
        """Collect tweets and store them in the database."""
        try:
            with DatabaseHandler() as db:
                # Collect and store general political tweets
                political_tweets = self.search_political_tweets()
                if political_tweets:
                    db.store_tweets(political_tweets, is_political_account=False)
                    self.logger.info(f"Stored {len(political_tweets)} general political tweets")

                # Collect and store tweets from political accounts
                account_tweets = self.get_political_accounts_tweets()
                if account_tweets:
                    db.store_tweets(account_tweets, is_political_account=True)
                    self.logger.info(f"Stored {len(account_tweets)} tweets from political accounts")
        
        except Exception as e:
            self.logger.error(f"Error in collect_and_store: {str(e)}")
            raise

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Test the collector
    collector = GermanPoliticsCollector()
    collector.collect_and_store()