# 🚂 Railway Deployment Guide - CricMind API

## Prerequisites
- GitHub account
- Railway account (sign up at railway.app)
- Your FastAPI code pushed to GitHub

---

## Step 1: Push Code to GitHub

```bash
cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API"

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit - CricMind FastAPI backend"

# Create GitHub repo and push
# Go to github.com and create a new repository called "cricmind-api"
git remote add origin https://github.com/YOUR_USERNAME/cricmind-api.git
git branch -M main
git push -u origin main
```

**⚠️ IMPORTANT:** Create a `.gitignore` file to exclude sensitive files:

```
__pycache__/
*.pyc
.env
*.log
.venv/
venv/
```

---

## Step 2: Deploy to Railway

### 2.1 Connect GitHub to Railway

1. Go to [railway.app](https://railway.app) and sign up/login
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub
5. Select the `cricmind-api` repository

### 2.2 Configure Environment Variables

Railway will auto-detect it's a Python app. Now add these environment variables:

**Go to:** Project → Variables → Add Variables

```env
DATABASE_URL=postgresql+asyncpg://postgres.moobxfaujplxknwutmab:I$b21651tOOr@aws-1-ap-southeast-2.pooler.supabase.com:6543/postgres
SECRET_KEY=cricmind_secret_key_2026_CHANGE_IN_PROD
GROQ_API_KEY=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
PORT=8000
```

**🔒 Security Note:** Change `SECRET_KEY` to a random 32+ character string for production.

### 2.3 Configure Build Settings

Railway should auto-detect Python and use:
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

If not auto-detected, add manually in Settings → Deploy.

---

## Step 3: Verify Deployment

1. Railway will give you a public URL like: `https://cricmind-api.railway.app`
2. Test endpoints:
   - `https://cricmind-api.railway.app/` → Should show `{"message": "CricMind API is running"}`
   - `https://cricmind-api.railway.app/health` → Should show `{"status": "healthy"}`
   - `https://cricmind-api.railway.app/docs` → Opens Swagger UI

---

## Step 4: Enable Custom Domain (Optional)

1. In Railway project → Settings → Domains
2. Click **"Generate Domain"** for free `.railway.app` subdomain
3. Or connect your own domain (cricmind.com)

---

## Step 5: Set Up Auto-Deploy

Railway auto-deploys on every git push to `main` branch.

To deploy updates:
```bash
git add .
git commit -m "Update: description of changes"
git push origin main
# Railway auto-deploys in ~2 minutes
```

---

## Troubleshooting

### ❌ Deployment fails
- Check **Logs** in Railway dashboard
- Verify all env vars are set
- Ensure `requirements.txt` has all dependencies

### ❌ Database connection error
- Verify `DATABASE_URL` is correct (use Supabase connection pooler URL)
- Check Supabase allows connections from Railway's IP

### ❌ 502 Bad Gateway
- Ensure start command is: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Check that `PORT` env var is set

---

## Cost & Limits

**Railway Free Tier:**
- $5 free credit/month
- ~500 hours of uptime
- Perfect for MVP & testing

**Supabase Free Tier:**
- 500MB database
- Unlimited API requests
- Perfect for PSL fantasy app

---

## What Changes Were Made for Production?

### 1. ✅ Authentication Added
- All `/fantasy/*` endpoints now require JWT token
- All `/ai/*` endpoints require JWT token
- Users can only edit their own teams

### 2. ✅ Rate Limiting Added
- AI questions limited to 10/day per user
- Tracked in `ai_usage` table

### 3. ✅ Health Check Endpoint
- `/health` endpoint for Railway monitoring

### 4. ✅ Security Improvements
- User validation in fantasy endpoints
- Token-based user identification (no user_id in request body)

---

## Next Steps After Deployment

1. ✅ Test all endpoints with Postman/Thunder Client
2. ✅ Update frontend (Lovable.dev) to use Railway URL
3. ✅ Seed match data to Supabase
4. ✅ Test fantasy team creation flow
5. ✅ Monitor Railway logs for errors

---

## Support

- Railway Docs: https://docs.railway.app
- Railway Discord: https://discord.gg/railway
- FastAPI Deployment: https://fastapi.tiangolo.com/deployment/

---

**You're ready to deploy! 🚀**
