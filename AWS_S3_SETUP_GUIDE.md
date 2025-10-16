# AWS S3 Setup Guide for Django ERP System

This guide will help you set up AWS S3 for serving static and media files for your Django ERP application.

## Prerequisites
- AWS Account
- AWS CLI installed (optional but recommended)

## Step 1: Create an S3 Bucket

1. **Login to AWS Console**
   - Go to https://aws.amazon.com/console/
   - Sign in to your account

2. **Create S3 Bucket**
   - Navigate to S3 service
   - Click "Create bucket"
   - Choose a unique bucket name (e.g., `your-erp-static-files`)
   - Select a region (recommend `us-east-1` for better performance)
   - **Important**: Uncheck "Block all public access" for static files
   - Click "Create bucket"

## Step 2: Configure Bucket Policy

1. **Set Bucket Policy**
   - Go to your bucket → Permissions → Bucket Policy
   - Add this policy (replace `YOUR-BUCKET-NAME` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::YOUR-BUCKET-NAME/static/*"
        }
    ]
}
```

2. **Configure CORS (if needed)**
   - Go to Permissions → CORS configuration
   - Add this configuration:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }
]
```

## Step 3: Create IAM User for Django

1. **Create IAM User**
   - Go to IAM service → Users → Add user
   - Username: `django-s3-user`
   - Access type: "Programmatic access"

2. **Set Permissions**
   - Attach existing policies directly
   - Create a custom policy with these permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::YOUR-BUCKET-NAME",
                "arn:aws:s3:::YOUR-BUCKET-NAME/*"
            ]
        }
    ]
}
```

3. **Save Credentials**
   - **IMPORTANT**: Save the Access Key ID and Secret Access Key
   - You'll need these for Heroku environment variables

## Step 4: Test Configuration

You can test your S3 configuration locally:

1. Create a `.env` file (never commit this to git):
```bash
USE_S3=True
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

2. Install dependencies:
```bash
pip install boto3 django-storages
```

3. Run collectstatic to test:
```bash
python manage.py collectstatic
```

## Step 5: Heroku Environment Variables

Set these environment variables in Heroku:

```bash
heroku config:set USE_S3=True
heroku config:set AWS_ACCESS_KEY_ID=your-access-key-id
heroku config:set AWS_SECRET_ACCESS_KEY=your-secret-access-key
heroku config:set AWS_STORAGE_BUCKET_NAME=your-bucket-name
heroku config:set AWS_S3_REGION_NAME=us-east-1
```

## Security Best Practices

1. **Use IAM Roles** (Advanced): Instead of IAM users, use IAM roles when possible
2. **Rotate Keys Regularly**: Change your AWS access keys periodically
3. **Monitor Usage**: Set up CloudWatch alarms for unusual S3 activity
4. **Backup Strategy**: Enable versioning on your S3 bucket

## Troubleshooting

**Common Issues:**

1. **403 Forbidden Error**
   - Check bucket policy allows public read access
   - Verify IAM user has correct permissions

2. **Static Files Not Loading**
   - Ensure `USE_S3=True` is set in environment variables
   - Check that `collectstatic` ran successfully during deployment

3. **CORS Errors**
   - Configure CORS policy in S3 bucket settings
   - Make sure your domain is included in allowed origins

## Cost Optimization

- **Use CloudFront CDN**: Set up CloudFront distribution for better performance and lower costs
- **Lifecycle Policies**: Set up rules to automatically delete old files
- **Monitoring**: Use AWS Cost Explorer to monitor S3 costs

## Next Steps

After setting up S3, proceed with the Heroku deployment using the HEROKU_DEPLOYMENT_GUIDE.md file.
