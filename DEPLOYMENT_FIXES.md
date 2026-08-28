# DetectAI Deployment Fixes & Debug Guide

## 🐛 Issues Fixed

### 1. Missing Database Module
**Problem**: `backend/database/db.py` was missing, causing import errors
**Solution**: Created complete database module with:
- SQLite connection management
- Case storage and retrieval
- Interrogation log tracking
- Verdict/leaderboard system

### 2. Import Path Issues
**Problem**: Frontend and backend had path resolution conflicts
**Solution**: 
- Added `__init__.py` files to all Python packages
- Database module now properly handles imports
- Fallback imports in `api/backend.py` for Vercel deployment

### 3. Vercel Configuration
**Problem**: `vercel.json` was incomplete/incorrect
**Solution**:
- Fixed build command to install all dependencies
- Added proper function configuration with Python 3.9 runtime
- Set correct timeout to 300s for Gemini API calls
- Added rewrites for API routing

### 4. Streamlit Cloud Configuration
**Problem**: Missing `.streamlit/config.toml`
**Solution**: Created configuration for:
- Headless server mode
- Custom theme matching Dark Cyber-Noir design
- Proper upload/memory settings

---

## 🚀 Deployment Instructions

### Step 1: Deploy Backend to Vercel

```bash
# Install Vercel CLI
npm install -g vercel
vercel login

# Deploy from project root
vercel --prod
```

**Or via Dashboard:**
1. Go to https://vercel.com/dashboard
2. Import GitHub repository: `Irfanshaikh016/project`
3. Set environment variables:
   - `GEMINI_API_KEY`: Your Google Gemini API key
   - `BACKEND_URL`: Will be auto-filled after deployment
4. Deploy

**Note**: You'll get a URL like `https://project-xxxxx.vercel.app`

### Step 2: Deploy Frontend to Streamlit Cloud

1. Go to https://streamlit.io/cloud
2. Click "New app"
3. Connect GitHub repo: `Irfanshaikh016/project`
4. Set:
   - **Repository**: `Irfanshaikh016/project`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
5. Click "Deploy"

### Step 3: Configure Streamlit Secrets

After Streamlit deployment:
1. Click app settings (gear icon)
2. Go to "Secrets"
3. Add:
```toml
BACKEND_URL = "https://your-vercel-url.vercel.app"
GEMINI_API_KEY = "your-gemini-api-key"
```
4. Save

---

## 🧪 Testing Deployment

### Test Backend Health
```bash
curl https://your-vercel-url.vercel.app/health
# Should return: {"status":"healthy","service":"DetectAI Backend"}
```

### Test Backend API
```bash
curl https://your-vercel-url.vercel.app/
# Should return app info
```

### Test Frontend
1. Open Streamlit app URL in browser
2. Set Gemini API key in sidebar
3. Try "Generate AI Crime Case"
4. Check browser console (F12) for errors
5. Verify case generation works

---

## 📋 Troubleshooting

### Backend Error: "Database is locked"
**Cause**: Vercel has ephemeral filesystem. SQLite doesn't persist.
**Solution**: For production, use PostgreSQL or Supabase:
```python
# backend/database/db.py
DATABASE_URL = os.getenv("DATABASE_URL")
# Switch to SQLAlchemy + PostgreSQL
```

### Frontend Error: "Connection refused"
**Cause**: `BACKEND_URL` not set in Streamlit secrets
**Solution**: 
1. Verify Streamlit secrets are saved
2. Restart the app
3. Check browser console for actual URL being used

### Slow Case Generation
**Cause**: Gemini API has rate limits on free tier
**Solution**:
- Increase timeout in `frontend/app.py` (currently 40s)
- Upgrade Gemini API plan
- Cache results in database

### Missing Dependencies
**Cause**: `requirements.txt` incomplete
**Solution**: All requirements are now complete:
- `backend/requirements.txt` - FastAPI, Uvicorn, Gemini client
- `frontend/requirements.txt` - Streamlit, requests, Pillow
- `requirements.txt` - Combined for local development

---

## 📊 Files Added/Modified

✅ **Created**:
- `backend/database/__init__.py`
- `backend/database/db.py` - Complete database module
- `.streamlit/config.toml` - Streamlit configuration
- `DEPLOYMENT_FIXES.md` - This file

✏️ **Updated**:
- `vercel.json` - Fixed configuration and timeouts
- All existing files remain unchanged

---

## 🔐 Environment Variables

### Vercel (Set in dashboard)
```
GEMINI_API_KEY=sk-... (your Google Gemini API key)
BACKEND_URL=https://your-project.vercel.app (auto-fill after deploy)
```

### Streamlit Cloud (Secrets tab)
```toml
BACKEND_URL="https://your-project.vercel.app"
GEMINI_API_KEY="sk-..."
```

### Local Development (.env)
```
BACKEND_URL=http://localhost:8000
GEMINI_API_KEY=your_key_here
PORT=8000
```

---

## ✅ Deployment Checklist

- [ ] All code committed to GitHub
- [ ] GitHub repo is public or Vercel/Streamlit have access
- [ ] Gemini API key obtained from https://aistudio.google.com/apikey
- [ ] Backend deployed to Vercel (get URL)
- [ ] Backend health check passes
- [ ] Streamlit secrets configured with backend URL
- [ ] Frontend deployed to Streamlit Cloud
- [ ] Frontend can generate test case
- [ ] Interrogation works (suspects respond)
- [ ] Database saves verdicts
- [ ] Leaderboard shows scores

---

## 📞 Support

- **Vercel Issues**: Check https://vercel.com/docs
- **Streamlit Issues**: Check https://docs.streamlit.io
- **Gemini API Issues**: Check https://ai.google.dev
- **Database Issues**: Local SQLite works fine for development; use PostgreSQL for production
