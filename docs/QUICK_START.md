# 🚀 Quick Start - Run Frontend Locally

## ⚡ Fastest Way (Windows)

### Option 1: Start Everything Together
Double-click: **`START_FULL_STACK.bat`**

This automatically:
- ✅ Starts backend at `http://localhost:8000`
- ✅ Starts frontend at `http://localhost:5173`
- ✅ Opens browser to frontend
- ✅ Installs dependencies if needed

---

## 📋 Manual Method (Step by Step)

### Terminal 1 - Start Backend:
```bash
cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API"
uvicorn app.main:app --reload
```
✅ Backend runs at: **http://localhost:8000**

### Terminal 2 - Start Frontend:
```bash
cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API\app\frontend"

# First time: Clean install dependencies
npm install

# If you get errors, run this first:
# FIX_DEPENDENCIES.bat

# Start dev server:
npm run dev
```
✅ Frontend runs at: **http://localhost:5173**

---

## 🧪 Test the App

Open browser → **http://localhost:5173**

### Test Flow:
1. **Landing page** loads with green cricket theme
2. Click **"Join Now"** → Register page
3. Create account (username, email, password)
4. Auto-redirects to **Dashboard**
5. See "Welcome back, [username]!"
6. Click **"Create Team"** on a match
7. Select 11 players (budget: 100 credits)
8. Set Captain & Vice Captain
9. Submit team
10. Try **AI Assistant** → Ask about players

---

## 🔧 Important Files Created

| File | Purpose |
|------|---------|
| `frontend/package.json` | Dependencies list |
| `frontend/.env` | API URL config (points to localhost:8000) |
| `frontend/FRONTEND_TESTING_GUIDE.md` | Detailed testing guide |
| `frontend/START_FRONTEND.bat` | Quick start script (frontend only) |
| `FAST API/START_FULL_STACK.bat` | Start both backend + frontend |

---

## ⚠️ Prerequisites

You need **Node.js** installed:
- Download: https://nodejs.org/ (v18 or higher)
- Check: `node --version` and `npm --version`

---

## 🎯 What Was Changed

### 1. API URL Updated
**File:** `frontend/lib/api.ts`
```typescript
// OLD (Lovable default):
const API_BASE = "https://cricmind-api.railway.app";

// NEW (for local testing):
const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
```

### 2. Environment Variable Added
**File:** `frontend/.env`
```env
VITE_API_URL=http://localhost:8000
```

When you deploy to Railway, change this to:
```env
VITE_API_URL=https://your-app-name.railway.app
```

---

## 🐛 Troubleshooting

### "Failed to fetch" errors
**Problem:** Backend not running or wrong URL

**Fix:**
1. Make sure backend is running: `http://localhost:8000/docs`
2. Check frontend `.env` has: `VITE_API_URL=http://localhost:8000`
3. Restart frontend dev server

---

### CORS errors
**Problem:** Backend blocking requests

**Fix:** Your backend already allows CORS. Restart backend:
```bash
uvicorn app.main:app --reload
```

---

### No matches/players showing
**Problem:** Empty Supabase database

**Fix:** Seed data to Supabase first (you said you'll handle this)

---

### "Cannot find module" errors
**Problem:** Dependencies not installed

**Fix:**
```bash
cd frontend
npm install
```

---

## 📱 Test on Mobile

1. Find your computer's local IP:
   ```bash
   ipconfig
   # Look for "IPv4 Address" (e.g., 192.168.1.100)
   ```

2. Start frontend with host flag:
   ```bash
   npm run dev -- --host
   ```

3. On phone, open: `http://YOUR-IP:5173`

---

## ✅ Success Checklist

- [ ] Backend running: `http://localhost:8000/docs` works
- [ ] Frontend running: `http://localhost:5173` opens
- [ ] Can register new account
- [ ] Can login
- [ ] Dashboard loads with username
- [ ] Can see matches and players
- [ ] Team selection page loads squads
- [ ] Can select 11 players
- [ ] Budget tracker updates correctly
- [ ] Can submit team
- [ ] AI assistant works (10 questions/day)
- [ ] No console errors in browser (F12 → Console)

---

## 🚀 Next Steps After Testing

### 1. Deploy Backend to Railway
Follow: `RAILWAY_DEPLOYMENT.md`

### 2. Update Frontend API URL
Edit `frontend/.env`:
```env
VITE_API_URL=https://your-railway-app.railway.app
```

### 3. Deploy Frontend
Options:
- **Vercel** (recommended for React): https://vercel.com
- **Netlify**: https://netlify.com
- **Railway**: Can also host frontend

### 4. Build Frontend for Production
```bash
cd frontend
npm run build
# Upload "dist/" folder to hosting
```

---

## 📚 Documentation

- **Detailed Testing Guide:** `frontend/FRONTEND_TESTING_GUIDE.md`
- **Backend Deployment:** `RAILWAY_DEPLOYMENT.md`
- **Frontend Spec:** `LOVABLE_FRONTEND_PROMPT.md`
- **API Changes:** `PRODUCTION_SUMMARY.md`

---

## 🎉 You're Ready!

Your full-stack CricMind app is ready for local testing.

**Commands Recap:**
```bash
# Backend:
uvicorn app.main:app --reload

# Frontend:
cd frontend
npm run dev

# Or use: START_FULL_STACK.bat (Windows)
```

**Test at:** http://localhost:5173

**Happy Testing! 🏏**
