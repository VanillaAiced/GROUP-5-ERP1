    print("CLEANUP COMPLETE!")
    print("="*70)
    print("\nTest your URLs:")
    print(f"  Logo: https://{BUCKET_NAME}.s3.amazonaws.com/static/LW.png")
    print(f"  App:  https://litework-erp-app-d3a15bf4658e.herokuapp.com/")
    print("\nIf images still don't load, clear your browser cache (Ctrl+Shift+R)")
    print("="*70)

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        print("\nPlease configure manually in AWS Console")
        print("https://s3.console.aws.amazon.com/s3/buckets/litework-erp")
"""
Clean up S3 bucket and upload files to correct locations
"""
import boto3
import os
from pathlib import Path

# AWS credentials
AWS_ACCESS_KEY_ID = 'AKIAW7AD7VICGSICRT66'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'litework-erp'
REGION = 'ap-northeast-2'

def main():
    print("="*70)
    print("S3 CLEANUP AND FIX SCRIPT")
    print("="*70)

    s3 = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=REGION
    )

    # Step 1: Delete the productionfiles folder in S3
    print("\nStep 1: Cleaning up incorrect paths in S3...")
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='static/productionfiles/')
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"  Deleting: {obj['Key']}")
                s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            print(f"  ✓ Deleted {len(response['Contents'])} files from static/productionfiles/")
        else:
            print("  No files found in static/productionfiles/")
    except Exception as e:
        print(f"  Note: {e}")

    # Also check for top-level productionfiles folder
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='productionfiles/')
        if 'Contents' in response:
            for obj in response['Contents']:
                print(f"  Deleting: {obj['Key']}")
                s3.delete_object(Bucket=BUCKET_NAME, Key=obj['Key'])
            print(f"  ✓ Deleted {len(response['Contents'])} files from productionfiles/")
    except Exception as e:
        print(f"  Note: {e}")

    # Step 2: Upload files to correct location
    print("\nStep 2: Uploading files to correct S3 paths...")

    files_to_upload = [
        ('productionfiles/LW.png', 'static/LW.png', 'image/png'),
        ('productionfiles/lite_work_logo.png', 'static/lite_work_logo.png', 'image/png'),
        ('productionfiles/PHPFP.jpg', 'static/PHPFP.jpg', 'image/jpeg'),
    ]

    uploaded_count = 0
    for local_path, s3_key, content_type in files_to_upload:
        if Path(local_path).exists():
            try:
                s3.upload_file(
                    local_path,
                    BUCKET_NAME,
                    s3_key,
                    ExtraArgs={
                        'ACL': 'public-read',
                        'ContentType': content_type,
                        'CacheControl': 'max-age=86400'
                    }
                )
                print(f"  ✓ Uploaded: {s3_key}")
                print(f"    URL: https://{BUCKET_NAME}.s3.amazonaws.com/{s3_key}")
                uploaded_count += 1
            except Exception as e:
                print(f"  ✗ Failed to upload {local_path}: {e}")
        else:
            print(f"  ✗ File not found: {local_path}")

    # Step 3: Apply bucket policy
    print("\nStep 3: Applying bucket policy...")
    try:
        with open('bucket-policy.json', 'r') as f:
            policy = f.read()
        s3.put_bucket_policy(Bucket=BUCKET_NAME, Policy=policy)
        print("  ✓ Bucket policy applied")
    except Exception as e:
        print(f"  ✗ Failed to apply bucket policy: {e}")

    # Step 4: Apply CORS
    print("\nStep 4: Applying CORS configuration...")
    try:
        import json
        with open('cors-policy.json', 'r') as f:
            cors = json.load(f)
        s3.put_bucket_cors(Bucket=BUCKET_NAME, CORSConfiguration={'CORSRules': cors})
        print("  ✓ CORS configuration applied")
    except Exception as e:
        print(f"  ✗ Failed to apply CORS: {e}")

    # Step 5: List current files in static/
    print("\nStep 5: Verifying files in S3 static/ folder...")
    try:
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='static/')
        if 'Contents' in response:
            print(f"  Found {len(response['Contents'])} files in static/")
            print("\n  Key image files:")
            for obj in response['Contents']:
                if any(name in obj['Key'] for name in ['LW.png', 'lite_work_logo.png', 'PHPFP.jpg']):
                    size_kb = obj['Size'] / 1024
                    print(f"    ✓ {obj['Key']} ({size_kb:.2f} KB)")
    except Exception as e:
        print(f"  Error listing files: {e}")

    print("\n" + "="*70)

