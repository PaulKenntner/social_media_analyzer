from src.database.db_handler import DatabaseHandler

def setup_database():
    try:
        with DatabaseHandler() as db:
            db.init_tables()
            print("Database tables created successfully")
    except Exception as e:
        print(f"Error setting up database: {str(e)}")

if __name__ == "__main__":
    setup_database() 