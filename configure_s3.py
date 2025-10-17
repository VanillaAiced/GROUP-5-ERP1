"""
Configure S3 bucket policy and CORS settings
"""
import boto3
import json
import os
from pathlib import Path

# Load environment from Heroku config
AWS_ACCESS_KEY_ID = 'AKIAW7AD7VICGSICRT66'
AWS_SECRET_ACCESS_KEY = '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'
AWS_STORAGE_BUCKET_NAME = 'litework-erp'
AWS_S3_REGION_NAME = 'ap-northeast-2'

def configure_s3():
    """Configure S3 bucket with policy and CORS"""
    try:
        # Create S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME
        )

        print("=" * 60)
        print("Configuring S3 Bucket: litework-erp")
        print("=" * 60)

        # 1. Apply Bucket Policy
        print("\n1. Applying Bucket Policy...")
        bucket_policy_file = Path(__file__).parent / 'bucket-policy.json'
        with open(bucket_policy_file, 'r') as f:
            bucket_policy = f.read()

        s3_client.put_bucket_policy(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Policy=bucket_policy
        )
        print("   ✓ Bucket policy applied successfully!")

        # 2. Apply CORS Configuration
        print("\n2. Applying CORS Configuration...")
        cors_policy_file = Path(__file__).parent / 'cors-policy.json'
        with open(cors_policy_file, 'r') as f:
            cors_config = json.load(f)

        s3_client.put_bucket_cors(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            CORSConfiguration={'CORSRules': cors_config}
        )
        print("   ✓ CORS configuration applied successfully!")

        # 3. List static files
        print("\n3. Checking uploaded files in S3...")
        response = s3_client.list_objects_v2(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Prefix='static/'
        )

        if 'Contents' in response:
            print(f"\n   Found {len(response['Contents'])} files in static/")
            print("\n   Key files:")
            for obj in response['Contents']:
                if any(name in obj['Key'] for name in ['LW.png', 'lite_work_logo.png', 'PHPFP.jpg', '.css']):
                    size_kb = obj['Size'] / 1024
                    print(f"   - {obj['Key']} ({size_kb:.2f} KB)")
        else:
            print("   ! No files found in static/")

        # 4. Test file accessibility
        print("\n4. Testing file accessibility...")
        test_files = ['static/LW.png', 'static/lite_work_logo.png', 'static/PHPFP.jpg']

        for file_key in test_files:
            try:
                s3_client.head_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_key)
                url = f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{file_key}"
                print(f"   ✓ {file_key} - accessible at:")
                print(f"     {url}")
            except Exception as e:
                print(f"   ✗ {file_key} - NOT FOUND")

        print("\n" + "=" * 60)
        print("S3 Configuration Complete!")
        print("=" * 60)
        print("\nYour static files should now be accessible from:")
        print(f"https://{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/static/")
        print("\nYour Heroku app:")
        print("https://litework-erp-app-d3a15bf4658e.herokuapp.com/")

    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease configure manually in AWS Console:")
        print("1. Go to: https://s3.console.aws.amazon.com/s3/buckets/litework-erp")
        print("2. Click 'Permissions' tab")
        print("3. Update Bucket Policy and CORS as shown in the instructions")

if __name__ == '__main__':
    configure_s3()

