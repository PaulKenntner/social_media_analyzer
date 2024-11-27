import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging
from typing import Dict, List

from src.database.db_handler import DatabaseHandler
from src.data_processing.data_transformer import DataTransformer

class TweetAnalyzer:
    """Analyzes and visualizes German political tweet data."""

    def __init__(self):
        self.db = DatabaseHandler()
        self.transformer = DataTransformer()
        self.logger = logging.getLogger(__name__)

    def get_tweets_dataframe(self) -> pd.DataFrame:
        """
        Fetch tweets from database and process them into analysis-ready DataFrame.
        
        Returns:
            DataFrame with processed tweet data and sentiment scores
        """
        try:
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
            metrics_df = pd.json_normalize(df['metrics'])
            df = pd.concat([df.drop('metrics', axis=1), metrics_df], axis=1)
            
            # Apply transformations
            df = self.transformer.clean_tweets(df)
            df = self.transformer.add_sentiment_analysis(df)
            
            return df

        except Exception as e:
            self.logger.error(f"Error preparing DataFrame: {str(e)}")
            raise

    def plot_tweets_over_time(self) -> None:
        """Visualize tweet frequency over time with sentiment coloring."""
        try:
            df = self.get_tweets_dataframe()
            
            # Convert created_at to datetime if it isn't already
            df['date'] = pd.to_datetime(df['created_at'])
            
            # Create daily frequency
            daily_tweets = df.groupby(df['date'].dt.date).size()
            
            # Create the plot
            plt.figure(figsize=(12, 6))
            
            if not daily_tweets.empty:
                # Plot with proper date formatting
                ax = daily_tweets.plot(
                    kind='line',
                    color='blue',
                    marker='o',  # Add markers for each data point
                    linestyle='-',
                    linewidth=2,
                    markersize=8,
                    alpha=0.7
                )
                
                # Improve x-axis formatting with date formatter
                from matplotlib.dates import DateFormatter
                ax.xaxis.set_major_formatter(DateFormatter('%Y-%m-%d'))
                plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))  # Limit number of x ticks
                
                # Add grid for better readability
                plt.grid(True, linestyle='--', alpha=0.7)
                
                # Add labels and title with more context
                plt.title('Daily Tweet Volume in German Politics', pad=20)
                plt.xlabel('Date (YYYY-MM-DD)', labelpad=10)
                plt.ylabel('Number of Tweets per Day', labelpad=10)
                
                # Rotate x-axis labels for better readability
                plt.xticks(rotation=45, ha='right')
                
                # Add some padding to prevent label cutoff
                plt.margins(x=0.05)
                
                # Add annotation showing date range
                date_range = f"Date Range: {daily_tweets.index.min()} to {daily_tweets.index.max()}"
                plt.figtext(0.99, 0.01, date_range, ha='right', va='bottom', fontsize=8)
                
            else:
                plt.text(0.5, 0.5, 'No tweet data available', 
                        horizontalalignment='center',
                        verticalalignment='center',
                        transform=plt.gca().transAxes)
            
            plt.tight_layout()
            plt.savefig('tweet_frequency.png', dpi=300, bbox_inches='tight')
            plt.close()
            
            self.logger.info("Successfully generated time series plot")
            
        except Exception as e:
            self.logger.error(f"Error plotting time series: {str(e)}")
            raise

    def plot_engagement_metrics(self) -> None:
        """Visualize engagement metrics distribution."""
        try:
            df = self.get_tweets_dataframe()
            
            fig, axes = plt.subplots(2, 2, figsize=(15, 10))
            metrics = ['retweet_count', 'reply_count', 'like_count', 'quote_count']
            
            for ax, metric in zip(axes.flat, metrics):
                sns.histplot(data=df, x=metric, ax=ax)
                ax.set_title(f'Distribution of {metric.replace("_", " ").title()}')
            
            plt.tight_layout()
            plt.savefig('engagement_metrics.png')
            plt.close()
            
            self.logger.info("Successfully generated engagement metrics plots")
            
        except Exception as e:
            self.logger.error(f"Error plotting engagement metrics: {str(e)}")
            raise

    def get_sentiment_summary(self) -> Dict:
        """
        Generate summary statistics of tweet sentiments.
        
        Returns:
            Dictionary containing sentiment statistics
        """
        try:
            df = self.get_tweets_dataframe()
            
            return {
                'Average Sentiment': df['sentiment'].mean(),
                'Positive Tweets': (df['sentiment'] > 0).sum(),
                'Negative Tweets': (df['sentiment'] < 0).sum(),
                'Neutral Tweets': (df['sentiment'] == 0).sum(),
                'Most Positive Tweet': df.loc[df['sentiment'].idxmax()]['text'],
                'Most Negative Tweet': df.loc[df['sentiment'].idxmin()]['text']
            }
            
        except Exception as e:
            self.logger.error(f"Error generating sentiment summary: {str(e)}")
            raise

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    analyzer = TweetAnalyzer()
    
    try:
        analyzer.plot_tweets_over_time()
        analyzer.plot_engagement_metrics()
        
        sentiment_summary = analyzer.get_sentiment_summary()
        for key, value in sentiment_summary.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
                
    except Exception as e:
        logging.error(f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    main()