### This script define a function that will make a connection to the mysql database

# import necessary libraries
import mysql.connector
from dotenv import load_dotenv
import os

# Load our environment variables from .env file
load_dotenv()

# define our function
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host = 'localhost',
            user = 'root',
            password = os.getenv('DB_PASSWORD'),
            database = 'nba_stats'
        )
        print('Database successfully connected!')
    
    except Exception as e:
        print(f'Database connection error: {e}')
        return None
    
    return conn