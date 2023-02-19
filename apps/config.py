# from decouple import config
import secrets
from sys import exit
import os
from dotenv import load_dotenv

class Config(object):

    load_dotenv()
    #setup App Secret Key
    SECRET_KEY = secrets.token_hex(20)

class ProductionConfig(Config):

    #set debug flag
    DEBUG = False
    try:
        SQLALCHEMY_DATABASE_URI = '{}+pymysql://{}:{}@{}:{}/{}'.format(
            os.environ.get('SQL_DB_ENGINE'),
            os.environ.get('SQL_DB_USERNAME'),
            os.environ.get('SQL_DB_PASSWORD'),
            os.environ.get('SQL_DB_HOSTNAME'),
            os.environ.get('SQL_DB_PORT'),
            os.environ.get('SQL_DB_NAME')
        )
    except KeyError as e:
        exit(f'Please provide DB credentials: {e}')

config_dict = {
    'Production' : ProductionConfig
}