from dotenv import load_dotenv
import os

from utils.mysql import *
from utils.logs import *

dotenv_path = os.join(os.dirname(__file__), '.env')
load_dotenv(dotenv_path)

host = os.environ.get("HOST")
user = os.environ.get("USER")
password = os.environ.get("PASSWORD")
database = os.environ.get("DATABASE")

connection = MYSQL(connect=True, host=host, user=user,
                   password=password, database=database)
