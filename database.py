import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()
  
dataBase = mysql.connector.connect(
  host = os.environ['AWS_RDS_ENDPOINT'],
  user = os.environ['AWS_RDS_USERNAME'],
  passwd = os.environ['AWS_RDS_PASSWORD']
)
 
# preparing a cursor object
cursorObject = dataBase.cursor()
