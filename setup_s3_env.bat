@echo off
echo Setting up S3 environment variables for ERP project...
echo.

REM Set the bucket name (this matches your bucket-policy.json)
set AWS_STORAGE_BUCKET_NAME=litework-erp

REM Enable S3 usage
set USE_S3=True

REM You need to replace these with your actual AWS credentials
set AWS_ACCESS_KEY_ID=AKIAW7AD7VICGSICRT66
set AWS_SECRET_ACCESS_KEY=LUXEpQPulxii/f1xvKtazL1NPgeWf5ev7EpIdI/B

REM Optional: Set the region (default is us-east-1)
set AWS_S3_REGION_NAME=ap-northeast-2

echo Environment variables set successfully!
echo.
echo IMPORTANT: Replace 'your_actual_access_key_here' and 'your_actual_secret_key_here'
echo with your real AWS credentials before running this script.
echo.
echo To make these permanent, add them to your system environment variables
echo through Control Panel > System > Advanced System Settings > Environment Variables
echo.
pause
