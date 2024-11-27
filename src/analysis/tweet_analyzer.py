import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
from src.database.db_handler import DatabaseHandler
from src.data_processing.data_transformer import DataTransformer

class TweetAnalyzer:
    def __init__(self):
        self.db = DatabaseHandler()
        self.transformer = DataTransformer()
        
    def get_tweets_dataframe(self):
        """Fetch tweets from database and convert to pandas DataFrame"""
        with self.db.conn.cursor() as cur:
            cur.execute("""
                SELECT id, text, created_at, account_name, 
                       metrics, is_political_account
                FROM tweets
                ORDER BY created_at DESC
            """)
            columns = ['id', 'text', 'created_at', 'account_name', 
                      'metrics', 'is_political_account']
            data = cur.fetchall()
            
        df = pd.DataFrame(data, columns=columns)
        # Expand metrics JSON into separate columns
        metrics_df = pd.json_normalize(df['metrics'])
        df = pd.concat([df.drop('metrics', axis=1), metrics_df], axis=1)
        
        # Transform the data
        df = self.transformer.transform_data(df)
        return df

    def plot_tweets_over_time(self):
        """Plot tweet frequency over time"""
        df = self.get_tweets_dataframe()
        
        plt.figure(figsize=(12, 6))
        df['created_at'].value_counts().sort_index().plot(kind='line')
        plt.title('Tweet Frequency Over Time')
        plt.xlabel('Date')
        plt.ylabel('Number of Tweets')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('tweet_frequency.png')
        plt.close()

    def plot_engagement_metrics(self):
        """Plot engagement metrics distribution"""
        df = self.get_tweets_dataframe()
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        metrics = ['retweet_count', 'reply_count', 'like_count', 'quote_count']
        
        for ax, metric in zip(axes.flat, metrics):
            sns.histplot(data=df, x=metric, ax=ax)
            ax.set_title(f'Distribution of {metric.replace("_", " ").title()}')
        
        plt.tight_layout()
        plt.savefig('engagement_metrics.png')
        plt.close()

    def get_top_engaged_tweets(self, n=5):
        """Get top engaged tweets based on combined metrics"""
        df = self.get_tweets_dataframe()
        
        df['total_engagement'] = (df['retweet_count'] + 
                                df['reply_count'] + 
                                df['like_count'] + 
                                df['quote_count'])
        
        return df.nlargest(n, 'total_engagement')[
            ['text', 'created_at', 'total_engagement']
        ]

    def plot_sentiment_distribution(self):
        """Plot distribution of tweet sentiments"""
        df = self.get_tweets_dataframe()
        
        plt.figure(figsize=(10, 6))
        sns.histplot(data=df, x='sentiment', bins=30)
        plt.title('Distribution of Tweet Sentiments')
        plt.xlabel('Sentiment Score')
        plt.ylabel('Number of Tweets')
        plt.tight_layout()
        plt.savefig('sentiment_distribution.png')
        plt.close()

    def get_sentiment_summary(self):
        """Get summary of sentiment analysis"""
        df = self.get_tweets_dataframe()
        
        summary = {
            'Average Sentiment': df['sentiment'].mean(),
            'Positive Tweets': (df['sentiment'] > 0).sum(),
            'Negative Tweets': (df['sentiment'] < 0).sum(),
            'Neutral Tweets': (df['sentiment'] == 0).sum(),
        }
        return summary

def main():
    analyzer = TweetAnalyzer()
    
    print("Generating visualizations...")
    analyzer.plot_tweets_over_time()
    analyzer.plot_engagement_metrics()
    analyzer.plot_sentiment_distribution()
    
    print("\nSentiment Summary:")
    sentiment_summary = analyzer.get_sentiment_summary()
    for key, value in sentiment_summary.items():
        print(f"{key}: {value:.2f}")
    
    print("\nTop engaged tweets:")
    top_tweets = analyzer.get_top_engaged_tweets()
    print(top_tweets.to_string())

if __name__ == "__main__":
    main() 