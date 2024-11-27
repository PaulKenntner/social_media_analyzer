import tweepy
from src.config.config_loader import get_twitter_config

def create_twitter_client():
    config = get_twitter_config()
    
    client = tweepy.Client(
        consumer_key=config['api_key'],
        consumer_secret=config['api_secret'],
        access_token=config['access_token'],
        access_token_secret=config['access_token_secret']
    )
    
    return client

def test_connection():
    client = create_twitter_client()
    try:
        # Test the connection by fetching your own user info
        me = client.get_me()
        print(f"Successfully connected to Twitter API as: @{me.data.username}")
        return True
    except Exception as e:
        print(f"Error connecting to Twitter API: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 