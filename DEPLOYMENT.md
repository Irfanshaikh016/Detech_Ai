# DetectAI Vercel & Streamlit Cloud Deployment Guide

## 📋 Architecture Overview

```
┌─────────────────────────────────────────────┐
│         DetectAI Application                │
├─────────────────────────────────────────────┤
│  Frontend: Streamlit              │ Frontend │
│  (Streamlit Cloud)                │  URL     │
│                                   │ https:// │
│  ┌─────────────────────────────┐  │ detect-  │
│  │ Crime Case Generator        │  │ ai.     │
│  │ Scene Explorer              │  │ streamli│
│  │ Suspect Interrogation       │  │ t.app   │
│  │ Evidence Locker             │  │          │
│  │ Verdict Submission          │  │          │
│  └──────────────┬──────────────┘  │          │
│                 │                 │          │
│  HTTP Requests  │                 │          │
│  (CORS Enabled) │                 │          │
│                 ▼                 │          │
├──────────────────────────────────┼──────────┤
│  Backend: FastAPI (Vercel)       │ Backend  │
│                                  │   URL    │
│  ┌──────────────────────────────┐│ https:// │
│  │ Case Generation (Gemini AI)  ││ your-   │
│  │ Suspect Interrogation        ││ project.│
│  │ Evidence Analysis            ││ vercel. │
│  │ Judge Evaluation             ││ app     │
│  │ Database (SQLite)            ││          │
│  └──────────────────────────────┘│          │
│                                  │          │
└──────────────────────────────────┴──────────┘
```

---

## ✅ Prerequisites

1. **GitHub Repository**
   - Repo pushed with all code
   - `.gitignore` configured

2. **Vercel Account**
   - Sign up at https://vercel.com
   - Connected to your GitHub

3. **Streamlit Cloud Account**
   - Sign up at https://streamlit.io/cloud
   - Connected to your GitHub

4. **Google Gemini API Key**
   - Get from https://ai.google.dev
   - Free tier available

---

## 🚀 Step-by-Step Deployment

### Step 1: Deploy Backend to Vercel

#### 1.1 Install Vercel CLI (Optional)
```bash
npm install -g vercel
vercel login
```

#### 1.2 Deploy via Vercel Dashboard (Recommended)

1. Go to https://vercel.com/dashboard
2. Click **"Add New..."** → **"Project"**
3. Select your GitHub repository
4. Click **"Import"**
5. Configure project settings:
   - **Framework Preset**: Other
   - **Root Directory**: `.` (leave default)
   - **Build Command**: Leave empty or `npm run build`
   - **Output Directory**: Leave empty
   - **Install Command**: Leave empty

#### 1.3 Add Environment Variables

In Vercel Dashboard → **Settings** → **Environment Variables**:

| Variable | Value | Scope |
|----------|-------|-------|
| `GEMINI_API_KEY` | Your API key | Production, Preview, Development |
| `BACKEND_URL` | (Leave empty for now) | Production |

Click **"Deploy"**

#### 1.4 Get Your Backend URL

After deployment completes:
- Backend URL: `https://your-project-name.vercel.app`
- API endpoint: `https://your-project-name.vercel.app/api`
- Docs: `https://your-project-name.vercel.app/api/docs`
- Health check: `https://your-project-name.vercel.app/api/health`

**Copy this URL for Step 2.**

---

### Step 2: Deploy Frontend to Streamlit Cloud

#### 2.1 Create Streamlit Secrets File

Create `.streamlit/secrets.toml` locally:

```toml
# .streamlit/secrets.toml
BACKEND_URL = "https://your-project-name.vercel.app"
GEMINI_API_KEY = "your_gemini_api_key"
```

**DO NOT COMMIT THIS FILE** - Add to `.gitignore`:
```
.streamlit/secrets.toml
```

#### 2.2 Update Frontend Configuration

Edit `frontend/app.py` (line ~33):

```python
# Change this:
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# To this:
BACKEND_URL = os.getenv("BACKEND_URL", "https://your-project-name.vercel.app")
```

#### 2.3 Deploy to Streamlit Cloud

1. Push changes to GitHub:
   ```bash
   git add .
   git commit -m "Update backend URL for Vercel deployment"
   git push
   ```

2. Go to https://streamlit.io/cloud

3. Click **"New app"**

4. Fill in:
   - **Repository**: Your GitHub repo
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`

5. Click **"Deploy"**

#### 2.4 Add Streamlit Secrets

After deployment:

1. Go to your app's **"Settings"** (gear icon)
2. Click **"Secrets"**
3. Add your secrets in TOML format:
   ```toml
   BACKEND_URL = "https://your-project-name.vercel.app"
   GEMINI_API_KEY = "your_gemini_api_key"
   ```
4. Save

#### 2.5 Get Your Frontend URL

After deployment:
- Frontend URL: `https://your-streamlit-app-name.streamlit.app`

---

## 🔗 Final URLs

After both deployments:

| Component | URL |
|-----------|-----|
| **Frontend** | https://your-streamlit-app-name.streamlit.app |
| **Backend** | https://your-project-name.vercel.app |
| **API Docs** | https://your-project-name.vercel.app/docs |
| **Health Check** | https://your-project-name.vercel.app/health |

---

## 🧪 Testing the Deployment

### Test Backend

```bash
# Check if backend is running
curl https://your-project-name.vercel.app/health

# Should return:
# {"status":"healthy","service":"DetectAI Backend"}

# View API documentation
# https://your-project-name.vercel.app/docs
```

### Test Frontend

1. Open frontend URL in browser
2. Check browser console (F12) for errors
3. Try generating a test case
4. Check if backend calls succeed

---

## 🔧 Troubleshooting

### Backend Not Working

**Issue**: `502 Bad Gateway` or `500 Internal Server Error`

**Solutions**:
1. Check Vercel logs: https://vercel.com/dashboard → Select project → Deployments → Logs
2. Verify environment variables are set
3. Check Python version (should be 3.9+)
4. Verify all dependencies in `requirements.txt`

```bash
# View Vercel logs
vercel logs --follow
```

### Frontend Can't Connect to Backend

**Issue**: `Connection refused` or `404 Not Found`

**Solutions**:
1. Verify `BACKEND_URL` in Streamlit secrets
2. Test backend health check
3. Check CORS is enabled in backend
4. Check browser console (F12) for error details
5. Verify backend URL doesn't have trailing slash

```python
# Good
BACKEND_URL = "https://your-project.vercel.app"

# Bad
BACKEND_URL = "https://your-project.vercel.app/"  # trailing slash
```

### Database Issues

**Issue**: `SQLite database is locked` or data not persisting

**Solution**: Vercel has ephemeral file system. For persistence:

1. **Option A**: Use PostgreSQL
   ```python
   # backend/database/db.py
   DATABASE_URL = os.getenv("DATABASE_URL")
   # Use SQLAlchemy with PostgreSQL
   ```

2. **Option B**: Use Vercel KV (Redis)
   ```python
   # Use redis cache instead
   ```

3. **Option C**: Store locally (data will reset on redeployment)
   - Current approach using SQLite
   - Fine for hackathon/development

### Performance Issues

**Issue**: Slow responses or timeouts

**Solutions**:
1. Increase Vercel function timeout in `vercel.json`
2. Optimize database queries
3. Cache API responses
4. Use Vercel Pro for better specs

```json
{
  "functions": {
    "api/backend.py": {
      "maxDuration": 300  // Increase to 300 seconds
    }
  }
}
```

---

## 📊 Monitoring & Analytics

### Vercel Dashboard
- View deployments, logs, and analytics
- Monitor function usage
- Set up error alerts

### Streamlit Cloud
- View app logs: App menu → Manage app → Logs
- Monitor app health
- View usage statistics

---

## 💾 Local Development

### Setup Local Environment

```bash
# Clone repository
git clone https://github.com/Irfanshaikh016/project.git
cd project

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
```

### Run Backend Locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run backend
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Backend available at: http://localhost:8000
# Docs: http://localhost:8000/docs
```

### Run Frontend Locally

```bash
# Install dependencies
pip install -r frontend/requirements.txt

# Update BACKEND_URL in frontend/app.py to http://localhost:8000

# Run frontend
streamlit run frontend/app.py

# Frontend available at: http://localhost:8501
```

### Local Environment Variables

```bash
# .env for local development
BACKEND_URL=http://localhost:8000
GEMINI_API_KEY=your_api_key_here
PORT=8000
```

---

## 📋 Pre-Deployment Checklist

- [ ] All code pushed to GitHub
- [ ] `.env` and `.streamlit/secrets.toml` in `.gitignore`
- [ ] `GEMINI_API_KEY` added to Vercel environment variables
- [ ] `BACKEND_URL` updated in frontend `app.py`
- [ ] Backend deployed to Vercel
- [ ] Backend URL copied
- [ ] Frontend secrets configured
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Backend health check working
- [ ] Frontend can generate a test case
- [ ] API documentation accessible
- [ ] All features tested (case generation, interrogation, verdict)

---

## 🚀 Post-Deployment

1. **Test all features** in production
2. **Monitor logs** for errors
3. **Set up alerts** for failures
4. **Keep API keys secure** (never commit them)
5. **Update README** with production URLs
6. **Document any custom configs**

---

## 📞 Support & Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud)
- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Google Gemini API](https://ai.google.dev)
- [Python Best Practices](https://pep8.org)

---

## 🎓 Architecture Decisions

### Why Vercel for Backend?
- ✅ Free tier available
- ✅ Automatic deployments from GitHub
- ✅ Built-in environment variables
- ✅ Fast cold starts with Python
- ✅ Easy scaling

### Why Streamlit Cloud for Frontend?
- ✅ Designed for Streamlit apps
- ✅ One-click deployment
- ✅ Automatic redeployment on push
- ✅ Built-in secrets management
- ✅ Free tier available

### Why SQLite?
- ✅ Simple for development
- ✅ No external database needed
- ✅ Quick to set up
- ⚠️ Data resets on redeployment (for production, use PostgreSQL)

---

## 📝 Notes

- Both services have free tiers
- Vercel: 100GB bandwidth/month free
- Streamlit Cloud: Unlimited deployments
- Consider upgrading for production use
- Monitor usage to stay within free limits
