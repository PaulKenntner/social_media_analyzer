import json
import os

def load_config():
    # Get the absolute path to the config file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, '..', '..', 'config', 'config.json')
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    except json.JSONDecodeError:
        raise ValueError("Config file is not valid JSON")

def get_twitter_config():
    config = load_config()
    if 'twitter_api' not in config:
        raise KeyError("Twitter API configuration not found in config file")
    return config['twitter_api']

def get_database_config():
    config = load_config()
    if 'database' not in config:
        raise KeyError("Database configuration not found in config file")
    return config['database']

if __name__ == "__main__":
    # Test the config loading
    try:
        twitter_config = get_twitter_config()
        print("Successfully loaded Twitter configuration")
    except Exception as e:
        print(f"Error loading configuration: {str(e)}") 