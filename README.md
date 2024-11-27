# Social Media Data Aggregator

A Python-based social media data aggregator that collects, analyzes, and visualizes Twitter trends with a focus on German politics.

## Features
- Collect tweets from German political accounts and hashtags
- Store data in PostgreSQL database
- Sentiment analysis of tweets
- Visualizations of tweet engagement and sentiment
- Track trending political topics

## Prerequisites
- Python 3.12+
- PostgreSQL
- Twitter Developer Account with API access

## Setup

1. **Clone the repository**
```bash
git clone https://github.com/PaulKenntner/social_media_analyzer.git
cd social_media_analyzer
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up PostgreSQL**
```bash
# Install PostgreSQL (on macOS with Homebrew)
brew install postgresql@14
brew services start postgresql@14

# Create database and user
psql postgres
CREATE USER your_username WITH PASSWORD 'your_password';
CREATE DATABASE german_politics_db;
GRANT ALL PRIVILEGES ON DATABASE german_politics_db TO your_username;
\q
```

5. **Configure API and Database**
Create `config/config.json` with your credentials:
```json
{
    "twitter_api": {
        "bearer_token": "your_bearer_token",
        "api_key": "your_api_key",
        "api_secret": "your_api_secret",
        "access_token": "your_access_token",
        "access_token_secret": "your_access_token_secret"
    },
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "german_politics_db",
        "user": "your_username",
        "password": "your_password"
    }
}
```

## Usage

1. **Initialize Database**
```bash
python -m src.database.setup_db
```

2. **Collect Tweets**
```bash
python -m src.data_collection.test_collection
```

3. **Generate Analysis**
```bash
python -m src.analysis.tweet_analyzer
```

This will create several visualizations:
- `tweet_frequency.png`: Timeline of tweet activity
- `engagement_metrics.png`: Distribution of likes, retweets, etc.
- `sentiment_distribution.png`: Analysis of tweet sentiments

## Project Structure
```
social_media_analyzer/
├── config/
│   └── config.json           
├── src/
│   ├── __init__.py
│   ├── analysis/            
│   │   ├── __init__.py
│   │   └── tweet_analyzer.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── config_loader.py
│   ├── data_collection/
│   │   ├── __init__.py
│   │   ├── german_politics_collector.py
│   │   ├── twitter_client.py
│   ├── data_processing/
│   │   ├── __init__.py
│   │   └── data_transformer.py
│   └── database/
│       ├── __init__.py
│       ├── db_handler.py
│       └── setup_db.py
├── requirements.txt
└── README.md
```

## Limitations
- Free Twitter API tier limited to 100 tweets per month
- Only collects tweets from the last 7 days
- Rate limits apply to API requests

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

MIT License

Copyright (c) 2024 Paul Kenntner

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 