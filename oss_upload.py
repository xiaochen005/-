import oss2
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY_ID = os.getenv("ACCESS_KEY_ID")
ACCESS_KEY_SECRET = os.getenv("ACCESS_KEY_SECRET")
ENDPOINT = os.getenv("ENDPOINT")
BUCKET_NAME = os.getenv("BUCKET_NAME")

auth = oss2.Auth(ACCESS_KEY_ID, ACCESS_KEY_SECRET)
bucket = oss2.Bucket(auth, ENDPOINT, BUCKET_NAME)

def upload_file_to_oss(local_file_path, save_folder="video"):
    time_tag = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.basename(local_file_path)
    oss_key = f"{save_folder}/{time_tag}_{filename}"
    bucket.put_object_from_file(oss_key, local_file_path)
    public_url = f"https://{BUCKET_NAME}.{ENDPOINT}/{oss_key}"
    return public_url

def delete_oss_file(file_url):
    url_prefix = f"https://{BUCKET_NAME}.{ENDPOINT}/"
    if file_url.startswith(url_prefix):
        oss_key = file_url.replace(url_prefix, "")
        bucket.delete_object(oss_key)
