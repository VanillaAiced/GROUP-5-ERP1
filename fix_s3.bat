@echo off
echo ============================================================
echo S3 Configuration and File Upload Script
echo ============================================================
echo.

echo Step 1: Verifying local files...
if exist "productionfiles\LW.png" (
    echo [OK] LW.png found
) else (
    echo [MISSING] LW.png - copying from static folder...
    copy "static\LW.png" "productionfiles\LW.png"
)

if exist "productionfiles\lite_work_logo.png" (
    echo [OK] lite_work_logo.png found
) else (
    echo [MISSING] lite_work_logo.png - copying from static folder...
    copy "static\lite_work_logo.png" "productionfiles\lite_work_logo.png"
)

echo.
echo Step 2: Running Python script to upload to S3...
python upload_to_s3.py

echo.
echo Step 3: If the above succeeded, test your URLs:
echo.
echo Logo URL: https://litework-erp.s3.amazonaws.com/static/LW.png
echo App URL:  https://litework-erp-app-d3a15bf4658e.herokuapp.com/
echo.

echo ============================================================
echo If you see errors above, please configure manually:
echo ============================================================
echo 1. Go to: https://s3.console.aws.amazon.com/s3/buckets/litework-erp
echo 2. Click Permissions tab
echo 3. Edit Bucket Policy - paste from bucket-policy.json
echo 4. Edit CORS - paste from cors-policy.json
echo 5. Click Objects tab and manually upload:
echo    - productionfiles\LW.png to static/LW.png
echo    - productionfiles\lite_work_logo.png to static/lite_work_logo.png
echo.
pause

