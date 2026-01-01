# Quick Deployment Guide - Render (Free)

## 🚀 Fast Track (5 Minutes)

### 1. Push to GitHub
```bash
git add .
git commit -m "Ready for deployment"
git push
```

### 2. Sign up at https://render.com (use GitHub login)

### 3. Create PostgreSQL Database
- Click **"New +"** → **"PostgreSQL"**
- Name: `campusmart-db`
- Plan: **Free**
- Click **"Create Database"**
- Copy the **Internal Database URL**

### 4. Create Web Service
- Click **"New +"** → **"Web Service"**
- Connect your GitHub repo
- Settings:
  - **Build Command**: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
  - **Start Command**: `gunicorn campusmart.wsgi:application`
  - **Plan**: **Free**

### 5. Add Environment Variables
In Web Service → Environment, add:

```
DJANGO_SETTINGS_MODULE=campusmart.settings_production
SECRET_KEY=<generate using: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())">
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=<paste Internal Database URL from step 3>
```

### 6. Deploy & Run Migrations
- Click **"Create Web Service"**
- After deployment, go to **Shell** tab and run:
  ```bash
  python manage.py migrate
  python manage.py createsuperuser
  ```

### 7. Done! 🎉
Your app is live at: `https://your-app-name.onrender.com`

---

**Note**: Free tier spins down after 15 min inactivity. First request may be slow.

For detailed instructions, see `DEPLOYMENT.md`


