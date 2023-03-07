from dotenv import load_dotenv
import os
import pymysql

load_dotenv()


if __name__ == '__main__':
    db = pymysql.connect(host=os.environ['AWS_RDS_ENDPOINT'],
                            user=os.environ['AWS_RDS_USERNAME'],
                            passwd=os.environ['AWS_RDS_PASSWORD'],
                            db='dispenser',
                            autocommit=True)
    cur = db.cursor()

    