import os
from dotenv import load_dotenv
from sqlalchemy import URL
load_dotenv()

token = os.getenv("TOKEN")
db_database_name = os.getenv("DB_DATABASE_NAME")
db_user_name = os.getenv('DB_USER_NAME')
db_user_password = os.getenv('DB_USER_PASSWORD')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')

def get_url():
    return URL.create(
    'postgresql+psycopg2',
    db_user_name,
    db_user_password,
    db_host,
    db_port,
    db_database_name
)