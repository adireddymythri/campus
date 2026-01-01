# Deployment Guide for Campus Mart

This guide will help you deploy your Django application to **Render** for free.

## Why Render?

- ✅ **100% Free Tier** - No credit card required
- ✅ **Easy Setup** - Simple configuration
- ✅ **PostgreSQL Database** - Free tier included
- ✅ **Automatic SSL** - HTTPS enabled by default
- ✅ **Git Integration** - Auto-deploy on push

## Prerequisites

1. A GitHub account
2. Your code pushed to a GitHub repository
3. A Render account (sign up at https://render.com)

## Step-by-Step Deployment

### Step 1: Push Your Code to GitHub

If you haven't already, push your code to GitHub:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

### Step 2: Create a Render Account

1. Go to https://render.com
2. Sign up with your GitHub account (recommended for easy integration)

### Step 3: Create a PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Configure:
   - **Name**: `campusmart-db`
   - **Database**: `campusmart`
   - **User**: `campusmart_user`
   - **Region**: Choose closest to you
   - **Plan**: **Free**
3. Click **"Create Database"**
4. Wait for the database to be created
5. Copy the **Internal Database URL** (you'll need this later)

### Step 4: Create a Web Service

1. In Render dashboard, click **"New +"** → **"Web Service"**
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: `campusmart` (or any name you prefer)
   - **Region**: Same as your database
   - **Branch**: `main` (or your default branch)
   - **Root Directory**: `campusmart` (if your code is in a subdirectory)
   - **Environment**: `Python 3`
   - **Build Command**: 
     ```
     pip install -r requirements.txt && python manage.py collectstatic --noinput
     ```
   - **Start Command**: 
     ```
     gunicorn campusmart.wsgi:application
     ```
   - **Plan**: **Free**

### Step 5: Configure Environment Variables

In your Web Service settings, go to **"Environment"** and add these variables:

#### Required Variables:

```
DJANGO_SETTINGS_MODULE=campusmart.settings_production
SECRET_KEY=your-secret-key-here (generate a strong random string)
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=<paste the Internal Database URL from Step 3>
```

#### Optional Variables (if you need them):

```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
REDIS_URL=redis://localhost:6379 (if you need Redis)
```

**To generate a SECRET_KEY:**
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 6: Deploy

1. Click **"Create Web Service"**
2. Render will start building and deploying your app
3. This may take 5-10 minutes on the first deploy
4. You can watch the build logs in real-time

### Step 7: Run Migrations

After the first deployment:

1. Go to your Web Service dashboard
2. Click on **"Shell"** tab
3. Run:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

## Post-Deployment

### Access Your App

Your app will be available at: `https://your-app-name.onrender.com`

### Important Notes

1. **Free Tier Limitations:**
   - Services spin down after 15 minutes of inactivity
   - First request after spin-down may take 30-60 seconds
   - 750 hours/month free (enough for always-on if you have one service)

2. **Static Files:**
   - Static files are served via WhiteNoise (already configured)
   - Media files (user uploads) are stored locally and will be lost on redeploy
   - For persistent media storage, consider using AWS S3 or Cloudinary (free tiers available)

3. **Database:**
   - PostgreSQL database is persistent
   - Free tier includes 1 GB storage
   - Backup your database regularly

4. **Redis (if needed):**
   - For Channels/WebSockets, you'll need Redis
   - Render doesn't offer free Redis, but you can use:
     - **Upstash** (free tier available)
     - **Redis Cloud** (free tier available)
   - Update `REDIS_URL` environment variable accordingly

## Troubleshooting

### Build Fails

- Check build logs for errors
- Ensure all dependencies are in `requirements.txt`
- Verify Python version in `runtime.txt` matches Render's supported versions

### App Crashes

- Check application logs in Render dashboard
- Verify all environment variables are set correctly
- Ensure `ALLOWED_HOSTS` includes your Render domain

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Use the **Internal Database URL** (not External) for better performance
- Check database is running and accessible

### Static Files Not Loading

- Ensure `collectstatic` runs during build
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise is properly configured

## Alternative: Railway (Another Free Option)

If you prefer Railway:

1. Sign up at https://railway.app
2. Create a new project
3. Add PostgreSQL database
4. Deploy from GitHub
5. Set environment variables
6. Railway provides $5 free credit monthly

## Support

- Render Docs: https://render.com/docs
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/

---

**Happy Deploying! 🚀**


