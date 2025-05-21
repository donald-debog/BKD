import os
import requests
import boto3
from dotenv import load_dotenv
from botocore.client import Config

# Load environment variables
load_dotenv()

# R2 configuration
R2_ACCESS_KEY_ID = os.getenv("R2_ACCESS_KEY_ID")
R2_SECRET_ACCESS_KEY = os.getenv("R2_SECRET_ACCESS_KEY")
R2_BUCKET = os.getenv("R2_BUCKET")
R2_ENDPOINT = os.getenv("R2_ENDPOINT")

# Supabase configuration (for DB record)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Set up boto3 client for R2
s3 = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY_ID,
    aws_secret_access_key=R2_SECRET_ACCESS_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def upload_photo_to_r2(file_path, session_id):
    """
    Uploads a photo to Cloudflare R2 and returns the public URL
    """
    filename = os.path.basename(file_path)
    r2_key = f"{session_id}/{filename}"
    
    with open(file_path, "rb") as f:
        s3.upload_fileobj(f, R2_BUCKET, r2_key, ExtraArgs={"ACL": "public-read", "ContentType": "image/jpeg"})
    
    # Construct public URL (R2 public bucket URL pattern)
    public_url = f"{R2_ENDPOINT}/{R2_BUCKET}/{r2_key}"
    return public_url, filename

def create_supabase_record(session_id, url, filename):
    """
    Creates a record in the Supabase 'photos' table
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("Supabase credentials not set, skipping DB record.")
        return None
    data = {
        "session_id": session_id,
        "url": url,
        "filename": filename
    }
    db_url = f"{SUPABASE_URL}/rest/v1/photos"
    db_headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "apikey": SUPABASE_KEY,
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    db_response = requests.post(db_url, headers=db_headers, json=data)
    if db_response.status_code >= 300:
        print(f"Error creating database record: {db_response.text}")
        return None
    return db_response.json()

def upload_session_photos(session_path, session_id):
    results = []
    photos = [
        os.path.join(session_path, f)
        for f in os.listdir(session_path)
        if f.lower().endswith(".jpg")
    ]
    for photo_path in photos:
        print(f"Uploading {os.path.basename(photo_path)} to R2...")
        url, filename = upload_photo_to_r2(photo_path, session_id)
        print(f"Uploaded to: {url}")
        # Optionally create a Supabase DB record
        create_supabase_record(session_id, url, filename)
        results.append(url)
    print(f"Uploaded {len(results)} photos to R2 for session {session_id}")
    return results

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print("Usage: python supabase_uploader.py <session_id>")
        sys.exit(1)
    session_id = sys.argv[1]
    session_path = os.path.join("photos", "current", session_id)
    if not os.path.isdir(session_path):
        print(f"Session directory not found: {session_path}")
        sys.exit(1)
    upload_session_photos(session_path, session_id) 