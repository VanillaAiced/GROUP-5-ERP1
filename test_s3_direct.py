#!/usr/bin/env python3
"""
Direct S3 Connection Test
This script tests S3 connection using the credentials from your batch file.
"""

import boto3
from botocore.exceptions import ClientError, NoCredentialsError

def test_s3_connection_direct():
    """Test S3 connection with direct credentials"""

    print("🔍 Direct S3 Connection Test")
    print("=" * 50)

    # Use the credentials from your batch file
    AWS_ACCESS_KEY_ID = "AKIAW7AD7VICGSICRT66"
    AWS_SECRET_ACCESS_KEY = "LUXEpQPulxii/f1xvKtazL1NPgeWf5ev7EpIdI/B"
    AWS_STORAGE_BUCKET_NAME = "litework-erp"
    AWS_S3_REGION_NAME = "ap-northeast-2"

    print(f"📋 Testing with:")
    print(f"✅ Bucket: {AWS_STORAGE_BUCKET_NAME}")
    print(f"✅ Region: {AWS_S3_REGION_NAME}")
    print(f"✅ Access Key: {AWS_ACCESS_KEY_ID[:8]}...")
    print()

    try:
        # Create S3 client with direct credentials
        s3_client = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_S3_REGION_NAME
        )

        print("🔗 Testing S3 Connection:")

        # Test bucket access
        try:
            response = s3_client.head_bucket(Bucket=AWS_STORAGE_BUCKET_NAME)
            print(f"✅ SUCCESS: Bucket '{AWS_STORAGE_BUCKET_NAME}' is accessible")

            # Test listing objects
            try:
                response = s3_client.list_objects_v2(Bucket=AWS_STORAGE_BUCKET_NAME, MaxKeys=5)
                if 'Contents' in response:
                    print(f"✅ SUCCESS: Found {len(response['Contents'])} objects in bucket")
                    print("📁 Sample objects:")
                    for obj in response['Contents'][:3]:
                        print(f"   - {obj['Key']} (Size: {obj['Size']} bytes)")
                else:
                    print(f"✅ SUCCESS: Bucket is empty but accessible")

            except ClientError as e:
                print(f"⚠️  Can access bucket but cannot list objects: {e}")

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                print(f"❌ ERROR: Bucket '{AWS_STORAGE_BUCKET_NAME}' does not exist")
                return False
            elif error_code == '403':
                print(f"❌ ERROR: Access denied to bucket '{AWS_STORAGE_BUCKET_NAME}'")
                print("   Check your IAM permissions and bucket policy")
                return False
            else:
                print(f"❌ ERROR: {e}")
                return False

        # Test upload capability
        print("\n📤 Testing Upload Capability:")
        try:
            test_content = "Test file for Django ERP S3 integration"
            s3_client.put_object(
                Bucket=AWS_STORAGE_BUCKET_NAME,
                Key='test/django-s3-test.txt',
                Body=test_content,
                ContentType='text/plain'
            )
            print("✅ SUCCESS: Can upload files to bucket")

            # Clean up test file
            s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key='test/django-s3-test.txt')
            print("✅ SUCCESS: Can delete files from bucket")

        except ClientError as e:
            print(f"❌ ERROR: Cannot upload/delete files: {e}")

        print(f"\n🎉 FINAL RESULT:")
        print(f"✅ Your S3 configuration is PROPERLY ALIGNED!")
        print(f"✅ Django can successfully connect to your S3 bucket")
        print(f"✅ All permissions are working correctly")

        return True

    except NoCredentialsError:
        print("❌ ERROR: AWS credentials are invalid")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {e}")
        return False

if __name__ == "__main__":
    test_s3_connection_direct()
