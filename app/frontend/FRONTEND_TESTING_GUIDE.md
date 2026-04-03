# 🏏 CricMind Frontend - Local Testing Guide

## 📋 Prerequisites

You need either:
- **Node.js** (v18+) with npm/yarn, OR
- **Bun** (faster, recommended)

Check if you have Node.js:
```bash
node --version
npm --version
```

If not, download from: https://nodejs.org/

## 🚀 Step-by-Step Setup

### 1. Start Your Backend First

Open a terminal and run:
```bash
cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API"
uvicorn app.main:app --reload
```

✅ Backend should be running at: `http://localhost:8000`

Test it: Open browser → `http://localhost:8000/docs`

---

### 2. Install Frontend Dependencies

Open a NEW terminal (keep backend running) and run:

```bash
cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API\app\frontend"

# If you have npm (Node.js):
npm install

# OR if you have Bun (faster):
bun install
```

This will install all React, Tailwind, and other dependencies (~2-3 minutes).

---

### 3. Start Frontend Development Server

```bash
# With npm:
npm run dev

# OR with Bun:
bun run dev
```

✅ Frontend should start at: `http://localhost:5173`

You'll see output like:
```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

---

### 4. Open in Browser

Open: **http://localhost:5173**

You should see the CricMind landing page! 🎉

---

## 🧪 Testing the App

### Test Flow:

1. **Landing Page** (`/`)
   - Should show "Create Your Dream PSL Team"
   - Click "Join Now"

2. **Register** (`/register`)
   - Create account: username, email, password
   - Should auto-login and redirect to dashboard

3. **Dashboard** (`/dashboard`)
   - Should show "Welcome back, [username]!"
   - See today's match (if any in DB)
   - Click "Create Team" for a match

4. **Team Selection** (`/match/{id}/team-selection`)
   - See two team squads
   - Select 11 players
   - Budget tracker: 0/100 credits
   - Set Captain & Vice Captain
   - Submit team

5. **AI Assistant** (`/ai-assistant`)
   - Ask questions about players
   - Should show remaining questions: X/10

6. **Leaderboard** (`/leaderboard/season`)
   - See rankings

---

## ⚠️ Common Issues & Fixes

### Issue 1: "Failed to fetch" errors
**Problem:** Frontend can't connect to backend

**Fix:**
```bash
# Make sure backend is running:
cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API"
uvicorn app.main:app --reload

# Backend MUST be at http://localhost:8000
```

---

### Issue 2: CORS errors in browser console
**Problem:** Backend blocking frontend requests

**Fix:** Your backend already has CORS enabled in `main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ✅ This allows all origins
    ...
)
```

If still having issues, restart the backend.

---

### Issue 3: "No matches found" on dashboard
**Problem:** No match data in Supabase

**Fix:** 
- Seed match data to Supabase first
- Or manually create test data via Supabase dashboard

---

### Issue 4: Players not loading in team selection
**Problem:** No player data in database

**Fix:**
- Make sure players table is seeded in Supabase
- Check: `http://localhost:8000/players` returns data

---

### Issue 5: AI not working
**Problem:** GROQ_API_KEY not set or invalid

**Fix:**
- Check `FAST API/.env` has valid GROQ_API_KEY
- Test: `http://localhost:8000/docs` → Try `/ai/ask` endpoint

---

### Issue 6: Login not working
**Problem:** No users in database or JWT token issue

**Fix:**
1. Create account via `/register` page first
2. Check Supabase `users` table has your user
3. Check browser DevTools → Application → Local Storage → `authToken` exists after login

---

## 🔍 Debugging Tips

### Check Backend is Running:
```bash
# Open browser:
http://localhost:8000/
# Should show: {"message": "CricMind API is running"}

http://localhost:8000/health
# Should show: {"status": "healthy"}

http://localhost:8000/docs
# Should show Swagger UI
```

### Check Frontend API Calls:
1. Open browser DevTools (F12)
2. Go to "Network" tab
3. Refresh page
4. See all API calls (should be green 200 status)
5. If red 4xx/5xx → check error message

### Check Browser Console:
- Press F12 → Console tab
- Look for errors (red text)
- Common: "Failed to fetch", "401 Unauthorized", "CORS error"

---

## 📂 Project Structure

```
frontend/
├── pages/              # All 11 pages
│   ├── Index.tsx       # Landing page
│   ├── Login.tsx       # Login page
│   ├── Register.tsx    # Register page
│   ├── Dashboard.tsx   # User dashboard
│   ├── TeamSelection.tsx  # Team builder (core feature)
│   ├── MyTeam.tsx      # View created team
│   ├── Leaderboard.tsx # Rankings
│   ├── AIAssistant.tsx # AI chat
│   ├── Players.tsx     # All players grid
│   ├── PlayerProfile.tsx # Single player stats
│   └── Matches.tsx     # Match schedule
├── components/         # Reusable UI components
├── lib/
│   ├── api.ts         # API client
│   └── utils.ts       # Helper functions
├── context/
│   └── AuthContext.tsx # Auth state management
├── hooks/             # Custom React hooks
└── App.tsx            # Main app with routes
```

---

## 🎨 What to Test

### 1. Authentication Flow
- ✅ Register new account
- ✅ Login with username/password
- ✅ JWT token saved in localStorage
- ✅ Protected routes redirect to login if not logged in
- ✅ Logout clears token

### 2. Team Selection (Core Feature)
- ✅ Load match with two squads
- ✅ Click players to add to team
- ✅ Budget tracker updates (X/100 credits)
- ✅ Player count updates (X/11 selected)
- ✅ Show error if budget exceeded
- ✅ Show error if > 9 players from one team
- ✅ Set Captain (2x points) and Vice Captain (1.5x)
- ✅ Submit team opens name input modal
- ✅ Team saved successfully

### 3. UI/UX
- ✅ Responsive design (try mobile width)
- ✅ Loading states (skeleton loaders)
- ✅ Error messages (toast notifications)
- ✅ Cricket theme colors (green/gold)
- ✅ Smooth animations

### 4. API Integration
- ✅ All endpoints working
- ✅ Auth headers sent correctly
- ✅ Error handling (401 → redirect to login)
- ✅ Rate limiting on AI (10 questions/day)

---

## 📝 Making Changes

### Update API URL (for production):
Edit `frontend/.env`:
```env
VITE_API_URL=https://your-railway-app.railway.app
```

Then rebuild:
```bash
npm run dev  # Restart dev server
```

### Customize Colors:
Edit `frontend/tailwind.config.ts`

### Add New Pages:
1. Create file in `pages/YourPage.tsx`
2. Add route in `App.tsx`

---

## 🚀 Building for Production

When ready to deploy:

```bash
# Build optimized production bundle:
npm run build

# Files will be in: frontend/dist/
# Deploy this folder to Vercel/Netlify/Railway
```

---

## ✅ Checklist Before Testing

- [ ] Backend running at `http://localhost:8000`
- [ ] Backend `/docs` accessible
- [ ] Supabase has player/match data
- [ ] Frontend dependencies installed (`npm install`)
- [ ] Frontend running at `http://localhost:5173`
- [ ] `.env` file has `VITE_API_URL=http://localhost:8000`
- [ ] Browser console has no errors

---

## 🆘 Still Having Issues?

1. **Restart everything:**
   ```bash
   # Terminal 1 - Backend:
   cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API"
   uvicorn app.main:app --reload
   
   # Terminal 2 - Frontend:
   cd "C:\Users\US\OneDrive\Desktop\PSL Project\FAST API\app\frontend"
   npm run dev
   ```

2. **Clear browser cache:**
   - Ctrl + Shift + Delete → Clear cache
   - Or use Incognito mode

3. **Check both terminals for error messages**

4. **Test backend endpoints manually:**
   - `http://localhost:8000/players`
   - `http://localhost:8000/matches/all`

---

## 🎉 Success Indicators

You'll know it's working when:
- ✅ Landing page loads with PSL theme
- ✅ You can register/login
- ✅ Dashboard shows your username
- ✅ You can see matches and players
- ✅ Team selection page loads squad data
- ✅ You can select 11 players and create a team
- ✅ AI assistant responds to questions
- ✅ No console errors in browser DevTools

---

**Happy Testing! 🏏**

After testing locally, deploy both:
1. Backend → Railway (follow RAILWAY_DEPLOYMENT.md)
2. Frontend → Vercel/Netlify (Lovable can do this automatically)
