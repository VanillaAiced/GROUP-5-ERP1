# AWS S3 Setup Guide for Django ERP System

## Overview
This guide will help you set up AWS S3 for hosting static and media files in your Django ERP application.

## Prerequisites
- AWS Account
- AWS CLI installed (optional but recommended)
- Basic understanding of AWS S3 and IAM

## Step 1: Create an S3 Bucket

1. Log in to [AWS Console](https://console.aws.amazon.com/)
2. Navigate to S3 service
3. Click "Create bucket"
4. Configure your bucket:
   - **Bucket name**: Choose a unique name (e.g., `your-erp-static-files`)
   - **Region**: Select your preferred region (e.g., `us-east-1`)
   - **Block Public Access settings**: Uncheck "Block all public access" (for static files)
   - **Bucket Versioning**: Enable (recommended)
   - Click "Create bucket"

## Step 2: Configure Bucket Policy

1. Go to your bucket → Permissions → Bucket Policy
2. Add the following policy (replace `your-bucket-name` with your actual bucket name):

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "PublicReadGetObject",
            "Effect": "Allow",
            "Principal": "*",
            "Action": "s3:GetObject",
            "Resource": "arn:aws:s3:::your-bucket-name/*"
        }
    ]
}
```

## Step 3: Configure CORS (Cross-Origin Resource Sharing)

1. Go to your bucket → Permissions → CORS
2. Add the following CORS configuration:

```json
[
    {
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD", "PUT", "POST", "DELETE"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": ["ETag"],
        "MaxAgeSeconds": 3000
    }
]
```

## Step 4: Create IAM User with S3 Access

1. Navigate to IAM service in AWS Console
2. Click "Users" → "Add user"
3. Configure user:
   - **User name**: `django-erp-s3-user`
   - **Access type**: Check "Programmatic access"
   - Click "Next: Permissions"

4. Set permissions:
   - Click "Attach existing policies directly"
   - Search and select `AmazonS3FullAccess` (or create a custom policy for better security)
   - Click "Next" until you reach "Create user"

5. **Important**: Save the Access Key ID and Secret Access Key (you won't be able to see the secret key again)

## Step 5: Configure Django Settings

1. Install required packages:
```bash
pip install boto3 django-storages
```

2. Create a `.env` file in your project root (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update `.env` file with your AWS credentials:
```
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key_id
AWS_SECRET_ACCESS_KEY=your_secret_access_key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1
```

## Step 6: Update Django to Use Environment Variables

Install python-decouple or python-dotenv:
```bash
pip install python-decouple
```

## Step 7: Upload Static Files to S3

Run the following command to collect and upload static files to S3:
```bash
python manage.py collectstatic
```

## Step 8: Test the Configuration

1. Upload a test image through Django admin
2. Verify the file appears in your S3 bucket under the `media/` folder
3. Check that static files are loaded from S3 in your browser's developer tools

## Folder Structure in S3

Your S3 bucket will have the following structure:
```
your-bucket-name/
├── static/          # CSS, JS, images from STATIC_ROOT
│   ├── admin/
│   ├── css/
│   ├── js/
│   └── images/
└── media/           # User uploaded files
    └── [user uploads]
```

## Security Best Practices

1. **Use IAM Policy with Minimal Permissions**:
   Instead of `AmazonS3FullAccess`, create a custom policy:
   ```json
   {
       "Version": "2012-10-17",
       "Statement": [
           {
               "Effect": "Allow",
               "Action": [
                   "s3:PutObject",
                   "s3:GetObject",
                   "s3:DeleteObject",
                   "s3:ListBucket"
               ],
               "Resource": [
                   "arn:aws:s3:::your-bucket-name",
                   "arn:aws:s3:::your-bucket-name/*"
               ]
           }
       ]
   }
   ```

2. **Keep credentials secure**:
   - Never commit `.env` file to version control
   - Add `.env` to `.gitignore`
   - Rotate access keys regularly

3. **Use CloudFront CDN** (Optional but recommended for production):
   - Faster content delivery
   - Better security with HTTPS
   - Lower S3 costs

## Troubleshooting

### Static files not loading
- Verify `USE_S3=True` in your `.env` file
- Check AWS credentials are correct
- Verify bucket permissions and CORS settings
- Run `python manage.py collectstatic` again

### Access Denied errors
- Check IAM user has proper permissions
- Verify bucket policy allows public read access
- Ensure bucket name in settings matches actual bucket name

### CORS errors
- Verify CORS configuration in S3 bucket
- Check that allowed origins include your domain

## Switching Between Local and S3

To switch back to local storage:
```
USE_S3=False
```

To use S3:
```
USE_S3=True
```

## Cost Optimization

1. Enable S3 Lifecycle policies to move old files to cheaper storage classes
2. Use CloudFront CDN to reduce S3 data transfer costs
3. Enable S3 Intelligent-Tiering for automatic cost optimization
4. Regularly audit and delete unused files

## Production Deployment Checklist

- [ ] S3 bucket created with appropriate region
- [ ] Bucket policy configured for public read access
- [ ] CORS configured properly
- [ ] IAM user created with minimal required permissions
- [ ] Environment variables set in production server
- [ ] Static files collected and uploaded to S3
- [ ] CloudFront CDN configured (recommended)
- [ ] HTTPS enabled
- [ ] Backup strategy in place

## Additional Resources

- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [django-storages Documentation](https://django-storages.readthedocs.io/)
- [boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

