import boto3

AWS_ACCESS_KEY_ID = 'AKIAW7AD7VICGSICRT66'
AWS_SECRET_ACCESS_KEY = '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'
BUCKET_NAME = 'litework-erp'
REGION = 'ap-northeast-2'

s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, 
                  aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name=REGION)

print("Checking S3 bucket contents:\n")

# Check static folder
print("Files in static/ folder:")
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='static/')
if 'Contents' in response:
    for obj in response['Contents']:
        print(f"  - {obj['Key']} ({obj['Size']} bytes)")
else:
    print("  (empty)")

# Check productionfiles folder
print("\nFiles in productionfiles/ folder:")
response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix='productionfiles/')
if 'Contents' in response:
    for obj in response['Contents']:
        print(f"  - {obj['Key']} ({obj['Size']} bytes)")
else:
    print("  (empty)")

# Test access to logo
print("\nTesting access to static/LW.png:")
try:
    s3.head_object(Bucket=BUCKET_NAME, Key='static/LW.png')
    print("  SUCCESS - File exists and is accessible")
    print(f"  URL: https://{BUCKET_NAME}.s3.amazonaws.com/static/LW.png")
except Exception as e:
    print(f"  FAILED - {e}")

