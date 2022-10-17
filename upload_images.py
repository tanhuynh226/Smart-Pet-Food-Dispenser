import boto3
import os
from dotenv import load_dotenv
 
load_dotenv()
def upload_files(path):
    session = boto3.Session(
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name='us-west-2'
    )
    s3 = session.resource('s3')
    bucket = s3.Bucket(os.getenv("AWS_BUCKET_ID"))
 
    for subdir, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(subdir, file)
            with open(full_path, 'rb') as data:
                bucket.put_object(Key='images/'+full_path[len(path)+0:], Body=data)
 
if __name__ == "__main__":
    upload_files('/images')