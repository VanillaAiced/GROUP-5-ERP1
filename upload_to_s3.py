"""
Quick S3 diagnostic and file upload
"""
import boto3
import os
from pathlib import Path

# AWS credentials - USE ENVIRONMENT VARIABLES
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME', 'litework-erp')
REGION = os.getenv('AWS_S3_REGION_NAME', 'ap-northeast-2')

try:
    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION
    )
    
    print("Uploading logo files to S3...")
    
    # Upload the logo files directly
    files_to_upload = [
        ('productionfiles/LW.png', 'static/LW.png'),
        ('productionfiles/lite_work_logo.png', 'static/lite_work_logo.png'),
        ('productionfiles/PHPFP.jpg', 'static/PHPFP.jpg'),
    ]
    
    for local_path, s3_key in files_to_upload:
        if Path(local_path).exists():
            s3.upload_file(
                local_path,
                BUCKET_NAME,
                s3_key,
                ExtraArgs={
                    'ACL': 'public-read',
                    'ContentType': 'image/png' if local_path.endswith('.png') else 'image/jpeg'
                }
            )
            print(f"✓ Uploaded: {s3_key}")
            print(f"  URL: https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}")
        else:
            print(f"✗ File not found: {local_path}")
    
    # Apply bucket policy
    print("\nApplying bucket policy...")
    with open('bucket-policy.json', 'r') as f:
        policy = f.read()
    s3.put_bucket_policy(Bucket=BUCKET_NAME, Policy=policy)
    print("✓ Bucket policy applied")
    
    # Apply CORS
    print("\nApplying CORS configuration...")
    import json
    with open('cors-policy.json', 'r') as f:
        cors = json.load(f)
    s3.put_bucket_cors(Bucket=BUCKET_NAME, CORSConfiguration={'CORSRules': cors})
    print("✓ CORS configuration applied")
    
    print("\n" + "="*60)
    print("SUCCESS! Your static files are now configured on S3")
    print("="*60)
    print("\nTest your site at:")
    print("https://litework-erp-app-d3a15bf4658e.herokuapp.com/")
    
except Exception as e:
    print(f"Error: {e}")
    print("\nManual steps required - Go to AWS Console:")
    print("https://s3.console.aws.amazon.com/s3/buckets/litework-erp")
