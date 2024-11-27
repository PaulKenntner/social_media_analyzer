import psycopg2
from psycopg2.extras import Json
from src.config.config_loader import get_database_config

class DatabaseHandler:
    def __init__(self):
        self.config = get_database_config()
        self.conn = None
        self.connect()

    def connect(self):
        """Establish database connection"""
        try:
            self.conn = psycopg2.connect(
                host=self.config['host'],
                port=self.config['port'],
                dbname=self.config['name'],
                user=self.config['user'],
                password=self.config['password']
            )
            print("Successfully connected to database")
        except Exception as e:
            print(f"Error connecting to database: {str(e)}")
            raise

    def init_tables(self):
        """Create necessary tables if they don't exist"""
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS tweets (
                    id BIGINT PRIMARY KEY,
                    text TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    collected_at TIMESTAMP NOT NULL,
                    account_name VARCHAR(255),
                    metrics JSONB,
                    lang VARCHAR(10),
                    is_political_account BOOLEAN
                );
                
                CREATE INDEX IF NOT EXISTS tweets_created_at_idx ON tweets(created_at);
                CREATE INDEX IF NOT EXISTS tweets_account_name_idx ON tweets(account_name);
            """)
            self.conn.commit()

    def store_tweets(self, tweets, is_political_account=False):
        """Store tweets in the database"""
        with self.conn.cursor() as cur:
            for tweet in tweets:
                cur.execute("""
                    INSERT INTO tweets (
                        id, text, created_at, collected_at, 
                        account_name, metrics, lang, is_political_account
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (id) DO UPDATE SET
                        metrics = EXCLUDED.metrics,
                        collected_at = EXCLUDED.collected_at
                """, (
                    tweet['id'],
                    tweet['text'],
                    tweet['created_at'],
                    tweet['collected_at'],
                    tweet.get('account', None),
                    Json(tweet['metrics']),
                    tweet.get('lang', 'de'),
                    is_political_account
                ))
            self.conn.commit()

    def get_recent_tweets(self, limit=100):
        """Retrieve recent tweets from database"""
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT id, text, created_at, account_name, metrics
                FROM tweets
                ORDER BY created_at DESC
                LIMIT %s
            """, (limit,))
            return cur.fetchall()

    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close() 