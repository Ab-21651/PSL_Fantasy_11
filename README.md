# 🏏 PSL Fantasy Cricket Platform

<div align="center">

![PSL Fantasy](https://img.shields.io/badge/PSL-Fantasy_Cricket-green?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393?style=for-the-badge&logo=fastapi)
![React](https://img.shields.io/badge/React-18+-61dafb?style=for-the-badge&logo=react)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?style=for-the-badge&logo=postgresql)

**Create your dream team, compete with friends, and dominate the PSL 2026 fantasy league!**

[Features](#-features) • [Demo](#-demo) • [Quick Start](#-quick-start) • [Deployment](#-deployment) • [Documentation](#-documentation)

</div>

---

## 🌟 Features

### 🎮 **Fantasy Gaming**
- 🏆 Create fantasy teams with 100 credit budget system
- 👥 Select 11 players (batters, bowlers, all-rounders, wicket-keepers)
- ⚡ Captain (2x points) and Vice-Captain (1.5x points)
- 📊 Real-time match data from ESPNCricinfo
- 🥇 Live leaderboards (match-wise and season-long)

### 📈 **Player Analytics**
- 📊 Detailed career statistics (batting, bowling, fielding)
- 🔥 Recent form tracking (last 5 matches)
- 💰 Dynamic credit system based on performance
- 🎯 Player profiles with team logos

### 🤖 **AI-Powered Assistant**
- 🧠 AI team selection recommendations
- 💡 Strategy suggestions based on player stats
- 📉 Match predictions and insights

### 🔐 **User Experience**
- 🔒 Secure JWT authentication
- 👤 Personal dashboard with team management
- 📱 Responsive design (mobile, tablet, desktop)
- 🌙 Modern UI with smooth animations

### 📊 **Admin Workflow**
- 🕷️ Automated web scraping from ESPNCricinfo
- 🔄 Quick match result updates
- 📈 Fantasy points auto-calculation
- 🎯 Fuzzy name matching for data consistency

---

## 🎯 Demo

**Live Site:** [Coming Soon]

**Screenshots:**

| Dashboard | Team Selection | Leaderboard |
|-----------|---------------|-------------|
| ![Dashboard](dashboard.jpeg) | ![Team](Tean Selection.jpeg) | ![AI Assistant](AI ASSISTANT.jpeg) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL (or Supabase account)
- Git

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ab-2165/psl-fantasy-cricket.git
   cd psl-fantasy-cricket
   ```

2. **Set up Backend**
   ```bash
   # Install Python dependencies
   pip install -r requirements.txt

   # Create .env file
   echo "DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db" > .env
   echo "SECRET_KEY=your-secret-key-here" >> .env
   ```

3. **Set up Frontend**
   ```bash
   cd app/frontend
   npm install
   ```

4. **Run the Application**
   ```bash
   # From project root
   START_FULL_STACK.bat  # Windows
   # OR manually:
   # Terminal 1: uvicorn app.main:app --reload
   # Terminal 2: cd app/frontend && npm run dev
   ```

5. **Access the app**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:8000`
   - API Docs: `http://localhost:8000/docs`

---

## 📂 Project Structure

```
psl-fantasy-cricket/
├── app/
│   ├── main.py              # FastAPI application entry
│   ├── db.py                # Database configuration
│   ├── models.py            # SQLAlchemy models
│   ├── auth.py              # JWT authentication
│   ├── routers/             # API endpoints
│   │   ├── auth.py          # User authentication
│   │   ├── players.py       # Player data & stats
│   │   ├── matches.py       # Match schedules
│   │   ├── fantasy.py       # Fantasy team logic
│   │   └── ai.py            # AI assistant
│   └── frontend/            # React application
│       ├── src/
│       │   ├── pages/       # Page components
│       │   ├── components/  # Reusable components
│       │   └── lib/         # Utilities & API client
│       └── package.json
│
├── scripts/
│   ├── scrape_simple.py         # ESPNCricinfo scraper
│   ├── seed_db.py               # Initial data seeder
│   └── seed_match_results.py   # Match results updater
│
├── docs/
│   ├── RAILWAY_DEPLOYMENT.md    # Deployment guide
│   ├── QUICK_START.md           # Setup instructions
│   ├── FANTASY_POINTS_GUIDE.md  # Scoring system
│   └── SCRAPING_GUIDE.md        # Data update workflow
│
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
└── README.md               # You are here!
```

---

## 🎮 How to Play

1. **Register** - Create your account
2. **Browse Matches** - See upcoming PSL matches
3. **Pick Your Team** - Select 11 players within 100 credits
4. **Set Captain & Vice-Captain** - Earn bonus points!
5. **Submit** - Lock your team before match starts
6. **Compete** - Check leaderboard after match completion

### 💯 Fantasy Points System

| Action | Points |
|--------|--------|
| **Batting** |
| Run scored | +1 |
| Four | +1 |
| Six | +2 |
| Fifty | +10 |
| Century | +25 |
| Duck (out for 0) | -5 |
| **Bowling** |
| Wicket | +25 |
| Maiden over | +12 |
| Economy < 6 | +6 |
| Economy > 10 | -6 |
| **Fielding** |
| Catch | +10 |
| Stumping | +15 |
| Run out | +10 |
| **Multipliers** |
| Captain | 2x points |
| Vice-Captain | 1.5x points |

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern, fast web framework
- **SQLAlchemy** - Async ORM
- **PostgreSQL** - Database (via Supabase)
- **JWT** - Authentication
- **Pydantic** - Data validation
- **BeautifulSoup4** - Web scraping

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **TanStack Query** - Data fetching
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Vite** - Build tool

### Infrastructure
- **Supabase** - PostgreSQL hosting
- **Railway** - Application deployment
- **GitHub** - Version control

---

## 📊 Database Schema

Key tables:
- `users` - User accounts and authentication
- `players` - Player profiles and credits
- `matches` - Match schedules and results
- `career_stats` - Historical player statistics
- `recent_form` - Last 5 matches performance
- `matchday_teams` - User fantasy teams
- `matchday_team_players` - Team rosters

---

## 🔄 Admin Workflow

### After Each PSL Match:

1. **Scrape Match Data**
   ```bash
   python scripts/scrape_simple.py --latest
   ```

2. **Update Database**
   ```bash
   python scripts/seed_match_results.py
   ```

3. **Verify** - Check leaderboard updates

**Total time:** ~2 minutes per match

---

## 📚 Documentation

- [Quick Start Guide](docs/QUICK_START.md)
- [Deployment Guide](docs/RAILWAY_DEPLOYMENT.md)
- [Fantasy Points System](docs/FANTASY_POINTS_GUIDE.md)
- [Data Scraping Workflow](docs/SCRAPING_GUIDE.md)

---

## 🚀 Deployment

### Railway (Recommended)

1. **Push to GitHub**
   ```bash
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [railway.app](https://railway.app)
   - Connect GitHub repository
   - Add environment variable: `DATABASE_URL`

3. **Deploy!**
   - Railway auto-deploys on push
   - Get your live URL: `https://your-app.railway.app`

**Detailed guide:** [docs/RAILWAY_DEPLOYMENT.md](docs/RAILWAY_DEPLOYMENT.md)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **ESPNCricinfo** - Match data source
- **PSL** - Pakistan Super League
- **FastAPI** - Amazing framework
- **shadcn/ui** - Beautiful components

---

## 📧 Contact

**Developer:** Abdullah Attique  
**Email:** abdullah.attique.2005@example.com  
**GitHub:** [AB-21651](https://github.com/Ab-21651)

---

<div align="center">

**Made with ❤️ for PSL fans**

⭐ Star this repo if you like it!

[Report Bug](hhttps://github.com/Ab-21651) • [Request Feature](https://github.com/yourusername/psl-fantasy-cricket/issues)

</div>
