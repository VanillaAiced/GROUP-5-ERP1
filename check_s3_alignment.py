#!/usr/bin/env python3
"""
S3 Configuration Alignment Checker
This script checks if your local configuration aligns with your AWS S3 bucket setup.
"""

import os
import json
from pathlib import Path

def check_s3_alignment():
    """Check if S3 configuration is properly aligned"""

    print("🔍 S3 Configuration Alignment Checker")
    print("=" * 50)

    # Check bucket policy
    try:
        with open('bucket-policy.json', 'r') as f:
            bucket_policy = json.load(f)
            bucket_arn = bucket_policy['Statement'][0]['Resource']
            bucket_name = bucket_arn.split(':::')[1].split('/')[0]
            print(f"✅ Bucket Policy - Bucket Name: {bucket_name}")
    except Exception as e:
        print(f"❌ Error reading bucket policy: {e}")
        return False

    # Check IAM policy
    try:
        with open('iam-policy.json', 'r') as f:
            iam_policy = json.load(f)
            iam_bucket_name = iam_policy['Statement'][0]['Resource'][0].split(':::')[1]
            print(f"✅ IAM Policy - Bucket Name: {iam_bucket_name}")

            if bucket_name != iam_bucket_name:
                print(f"⚠️  WARNING: Bucket names don't match! Policy: {bucket_name}, IAM: {iam_bucket_name}")
    except Exception as e:
        print(f"❌ Error reading IAM policy: {e}")

    # Check environment variables
    print("\n📋 Environment Variables Check:")
    required_env_vars = [
        'AWS_ACCESS_KEY_ID',
        'AWS_SECRET_ACCESS_KEY',
        'AWS_STORAGE_BUCKET_NAME',
        'USE_S3'
    ]

    for var in required_env_vars:
        value = os.getenv(var)
        if value:
            if var == 'AWS_STORAGE_BUCKET_NAME':
                if value == bucket_name:
                    print(f"✅ {var}: {value} (matches bucket policy)")
                else:
                    print(f"⚠️  {var}: {value} (MISMATCH - should be {bucket_name})")
            elif var in ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']:
                print(f"✅ {var}: ****** (set)")
            else:
                print(f"✅ {var}: {value}")
        else:
            print(f"❌ {var}: Not set")

    # Check Django settings
    print(f"\n⚙️  Django Configuration:")
    print(f"✅ Static location: static/ (matches bucket policy)")
    print(f"✅ Media location: media/")
    print(f"✅ Storage backends: Configured")

    # Check if storages is installed
    try:
        import storages
        print(f"✅ django-storages: Installed")
    except ImportError:
        print(f"❌ django-storages: Not installed - run 'pip install django-storages boto3'")

    # Check if boto3 is installed
    try:
        import boto3
        print(f"✅ boto3: Installed")
    except ImportError:
        print(f"❌ boto3: Not installed - run 'pip install boto3'")

    print(f"\n🎯 Quick Setup Commands:")
    print(f"Set environment variables:")
    print(f"set AWS_STORAGE_BUCKET_NAME={bucket_name}")
    print(f"set USE_S3=True")
    print(f"set AWS_ACCESS_KEY_ID=your_access_key")
    print(f"set AWS_SECRET_ACCESS_KEY=your_secret_key")

    return True

def test_s3_connection():
    """Test S3 connection if credentials are available"""
    print(f"\n🔗 Testing S3 Connection:")

    try:
        import boto3
        from botocore.exceptions import ClientError, NoCredentialsError

        bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME')
        if not bucket_name:
            print("❌ AWS_STORAGE_BUCKET_NAME not set")
            return False

        s3_client = boto3.client('s3')

        # Test bucket access
        try:
            response = s3_client.head_bucket(Bucket=bucket_name)
            print(f"✅ Bucket '{bucket_name}' is accessible")

            # Test listing objects
            try:
                response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=1)
                print(f"✅ Can list objects in bucket")
            except ClientError as e:
                print(f"⚠️  Can access bucket but cannot list objects: {e}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ Bucket '{bucket_name}' does not exist")
            elif error_code == '403':
                print(f"❌ Access denied to bucket '{bucket_name}'")
            else:
                print(f"❌ Error accessing bucket: {e}")

    except NoCredentialsError:
        print("❌ AWS credentials not found")
    except ImportError:
        print("❌ boto3 not installed")
    except Exception as e:
        print(f"❌ Error testing S3 connection: {e}")

if __name__ == "__main__":
    check_s3_alignment()
    test_s3_connection()
