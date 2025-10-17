"""
Verify S3 bucket structure
"""
import boto3

AWS_ACCESS_KEY_ID = 'AKIAW7AD7VICGSICRT66'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'litework-erp'
REGION = 'ap-northeast-2'

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION)

print("Checking S3 bucket structure...\n")

# Check static folder
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='static/', Delimiter='/')
if 'Contents' in response:
    for obj in response['Contents'][:20]:  # Show first 20
        print(f"{obj['Key']} - {obj['Size']} bytes")

# Test if logo is accessible
try:
    s3.head_object(Bucket=BUCKET_NAME, Key='static/LW.png')
    print(f"\n✓ LW.png is accessible at: https://{BUCKET_NAME}.s3.amazonaws.com/static/LW.png")
except:
    print("\n✗ LW.png not found at static/LW.png")

