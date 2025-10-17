import boto3
import json

# AWS Configuration
AWS_ACCESS_KEY_ID = 'AKIAW7AD7VICGSICRT66'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'litework-erp'
REGION = 'ap-northeast-2'

print("Fixing S3 Access Denied Issue...")
print("=" * 60)

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION)

# 1. Apply Bucket Policy
print("\n1. Applying Bucket Policy for public read access...")
bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicReadGetObject",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": [
            f"arn:aws:s3:::{BUCKET_NAME}/static/*",
            f"arn:aws:s3:::{BUCKET_NAME}/media/*"
        ]
    }]
}

try:
    s3.put_bucket_policy(Bucket=BUCKET_NAME, Policy=json.dumps(bucket_policy))
    print("   SUCCESS - Bucket policy applied!")
except Exception as e:
    print(f"   ERROR: {e}")

# 2. Apply CORS
print("\n2. Applying CORS configuration...")
cors_config = {
    'CORSRules': [{
        'AllowedHeaders': ['*'],
        'AllowedMethods': ['GET', 'HEAD'],
        'AllowedOrigins': ['*'],
        'ExposeHeaders': ['ETag'],
        'MaxAgeSeconds': 3000
    }]
}

try:
    s3.put_bucket_cors(Bucket=BUCKET_NAME, CORSConfiguration=cors_config)
    print("   SUCCESS - CORS applied!")
except Exception as e:
    print(f"   ERROR: {e}")

# 3. Upload logo files with public-read ACL
print("\n3. Uploading logo files with public-read permissions...")
from pathlib import Path

files = [
    ('productionfiles/LW.png', 'static/LW.png', 'image/png'),
    ('productionfiles/lite_work_logo.png', 'static/lite_work_logo.png', 'image/png'),
]

for local, s3_key, content_type in files:
    if Path(local).exists():
        try:
            s3.upload_file(local, BUCKET_NAME, s3_key,
                          ExtraArgs={'ACL': 'public-read', 'ContentType': content_type})
            print(f"   SUCCESS - {s3_key}")
        except Exception as e:
            print(f"   ERROR uploading {local}: {e}")
    else:
        print(f"   SKIP - {local} not found")

# 4. Verify access
print("\n4. Verifying file access...")
for _, s3_key, _ in files:
    try:
        s3.head_object(Bucket=BUCKET_NAME, Key=s3_key)
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}"
        print(f"   SUCCESS - {url}")
    except Exception as e:
        print(f"   ERROR - {s3_key}: {e}")

print("\n" + "=" * 60)
print("DONE! Test your app now:")
print("https://litework-erp-app-d3a15bf4658e.herokuapp.com/")
print("=" * 60)

