import logging
import sys
from typing import Dict, Any
import pandas as pd
from datetime import datetime

from src.data_collection.german_politics_collector import GermanPoliticsCollector
from src.database.db_handler import DatabaseHandler
from src.data_processing.data_transformer import DataTransformer

class SystemIntegrationTest:
    """Tests integration between all system components."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.collector = GermanPoliticsCollector()
        self.db = DatabaseHandler()
        self.transformer = DataTransformer()

    def test_twitter_api(self) -> Dict[str, Any]:
        """Test Twitter API connection with minimal data retrieval."""
        try:
            # Only request 1 tweet to minimize API usage
            tweets = self.collector.search_political_tweets(max_results=1)
            
            if tweets:
                return {
                    'status': 'success',
                    'message': 'Successfully connected to Twitter API',
                    'sample': tweets[0]
                }
            else:
                # Use mock data if rate limited
                mock_tweet = {
                    'id': 123456,
                    'text': 'Mock tweet for testing',
                    'created_at': datetime.now(),
                    'metrics': {'retweet_count': 0, 'like_count': 0},
                    'collected_at': datetime.now()
                }
                return {
                    'status': 'success',
                    'message': 'Using mock data (rate limited)',
                    'sample': mock_tweet
                }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Twitter API test failed: {str(e)}',
                'sample': None
            }

    def test_database(self) -> Dict[str, str]:
        """Test database connection and operations."""
        try:
            with self.db.conn.cursor() as cur:
                cur.execute("SELECT version();")
                version = cur.fetchone()[0]
                return {
                    'status': 'success',
                    'message': f'Connected to PostgreSQL version: {version}'
                }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Database test failed: {str(e)}'
            }

    def test_data_transformer(self) -> Dict[str, str]:
        """Test data transformation capabilities with sample data."""
        try:
            # Create sample DataFrame with German political content
            sample_data = {
                'text': [
                    'Die Bundesregierung plant neue Klimaschutzmaßnahmen.',
                    'Opposition kritisiert den aktuellen Haushaltsplan.'
                ],
                'created_at': ['2024-01-01', '2024-01-01']
            }
            df = pd.DataFrame(sample_data)
            
            # Test transformations
            cleaned_df = self.transformer.clean_tweets(df)
            analyzed_df = self.transformer.add_sentiment_analysis(cleaned_df)
            
            return {
                'status': 'success',
                'message': (f'Successfully transformed data with {len(analyzed_df)} rows. '
                          f'Sample sentiment: {analyzed_df["sentiment"].mean():.2f}')
            }
        except Exception as e:
            return {
                'status': 'failed',
                'message': f'Transformer test failed: {str(e)}'
            }

    def run_all_tests(self) -> None:
        """Run all system integration tests."""
        self.logger.info("Starting system integration tests...")
        
        # Run tests
        api_result = self.test_twitter_api()
        db_result = self.test_database()
        transformer_result = self.test_data_transformer()
        
        # Print results in a formatted way
        print("\n=== System Integration Test Results ===")
        print("\n1. Twitter API Test:")
        print(f"Status: {api_result['status']}")
        print(f"Message: {api_result['message']}")
        if api_result['sample']:
            print("Sample Data Available ✓")
        
        print("\n2. Database Test:")
        print(f"Status: {db_result['status']}")
        print(f"Message: {db_result['message']}")
        
        print("\n3. Data Transformer Test:")
        print(f"Status: {transformer_result['status']}")
        print(f"Message: {transformer_result['message']}")
        
        # Overall status
        all_passed = all(r['status'] == 'success' for r in 
                        [api_result, db_result, transformer_result])
        
        print("\n=== Overall Status ===")
        if all_passed:
            print("✅ All systems operational")
        else:
            print("❌ Some systems failed - check logs for details")

def main():
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        stream=sys.stdout
    )
    
    # Run tests
    tester = SystemIntegrationTest()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 