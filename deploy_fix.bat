@echo off
echo Starting deployment to Heroku...
cd /d C:\Users\Vince\GROUP-5-ERP1
git add -A
git commit -m "Fix authentication URL redirects for login and registration"
git push heroku main
echo Deployment complete!
pause

