import tweepy
from src.config.config_loader import get_twitter_config
from datetime import datetime
from src.database.db_handler import DatabaseHandler

class GermanPoliticsCollector:
    def __init__(self):
        config = get_twitter_config()
        self.client = tweepy.Client(
            bearer_token=config['bearer_token'],
            consumer_key=config['api_key'],
            consumer_secret=config['api_secret'],
            access_token=config['access_token'],
            access_token_secret=config['access_token_secret'],
            wait_on_rate_limit=True
        )

    # Common German political party hashtags and keywords
    POLITICAL_KEYWORDS = [
        'Bundestag', 'Bundesregierung',
        'CDU', 'SPD', 'Grüne', 'FDP', 'AfD', 'Linke',
        'Scholz', 'Merz', 'Baerbock', 'Lindner',
        'Deutsche Politik', 'Bundestagswahl'
    ]

    # Major German political accounts
    POLITICAL_ACCOUNTS = [
        'Bundestag',
        'RegSprecher',
        'CDU',
        'spdde',
        'Die_Gruenen',
        'fdp',
    ]

    def search_political_tweets(self, max_results=50):
        """Search for recent tweets about German politics"""
        query = ' OR '.join(self.POLITICAL_KEYWORDS)
        query += ' lang:de'  # Only German language tweets
        
        try:
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                tweet_fields=['created_at', 'public_metrics', 'lang']
            )
            
            if not tweets.data:
                return []

            return [{
                'id': tweet.id,
                'text': tweet.text,
                'created_at': tweet.created_at,
                'metrics': tweet.public_metrics,
                'collected_at': datetime.now()
            } for tweet in tweets.data]

        except Exception as e:
            print(f"Error collecting tweets: {str(e)}")
            return []

    def get_political_accounts_tweets(self, max_results=50):
        """Get recent tweets from major political accounts"""
        all_tweets = []
        
        for account in self.POLITICAL_ACCOUNTS:
            try:
                # First get the user ID
                user = self.client.get_user(username=account)
                if not user.data:
                    continue

                # Then get their tweets
                tweets = self.client.get_users_tweets(
                    id=user.data.id,
                    max_results=max_results,
                    tweet_fields=['created_at', 'public_metrics', 'lang']
                )
                
                if tweets.data:
                    account_tweets = [{
                        'id': tweet.id,
                        'text': tweet.text,
                        'created_at': tweet.created_at,
                        'metrics': tweet.public_metrics,
                        'account': account,
                        'collected_at': datetime.now()
                    } for tweet in tweets.data]
                    all_tweets.extend(account_tweets)

            except Exception as e:
                print(f"Error collecting tweets for {account}: {str(e)}")
                continue

        return all_tweets

    def collect_and_store(self):
        """Collect tweets and store them in the database"""
        with DatabaseHandler() as db:
            # Collect and store general political tweets
            political_tweets = self.search_political_tweets()
            if political_tweets:
                db.store_tweets(political_tweets, is_political_account=False)
                print(f"Stored {len(political_tweets)} general political tweets")

            # Collect and store tweets from political accounts
            account_tweets = self.get_political_accounts_tweets()
            if account_tweets:
                db.store_tweets(account_tweets, is_political_account=True)
                print(f"Stored {len(account_tweets)} tweets from political accounts")

if __name__ == "__main__":
    # Test the collector
    collector = GermanPoliticsCollector()
    
    print("Collecting and storing general political tweets...")
    political_tweets = collector.collect_and_store()