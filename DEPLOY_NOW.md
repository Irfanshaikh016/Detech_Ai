# 🚀 DetectAI Deployment Guide - Ready to Deploy!

Your project has been fully debugged and optimized for cloud deployment.

---

## ✅ What's Ready

✓ Backend (FastAPI) - Optimized for Vercel  
✓ Frontend (Streamlit) - Ready for Streamlit Cloud  
✓ Database (SQLite) - Fully implemented  
✓ All dependencies - Added to requirements  
✓ Environment configs - Configured for both platforms

---

## 📋 Quick Deployment Checklist

### You Need:
- ✅ GitHub account (code already pushed)
- ✅ Gemini API key (get from https://aistudio.google.com/apikey)
- ✅ Vercel account (sign up at https://vercel.com)
- ✅ Streamlit Cloud account (sign up at https://streamlit.io/cloud)

---

## 🔴 BACKEND DEPLOYMENT (Vercel)

### Option A: Via Vercel Dashboard (Easiest)

1. Go to **https://vercel.com/dashboard**
2. Click **"Add New"** → **"Project"**
3. Select GitHub repo: **`Irfanshaikh016/project`**
4. Click **"Import"**
5. In "Configure Project":
   - Framework Preset: **Other**
   - Root Directory: **`.`** (default)
   - Build Command: **`pip install -r backend/requirements.txt && pip install -r frontend/requirements.txt`**
   - Output Directory: **`.`** (default)
6. Click **"Deploy"**
7. Wait for deployment (2-3 minutes)
8. Copy your Backend URL: `https://your-project-xxxxx.vercel.app`

### Option B: Via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project root
cd /path/to/Irfanshaikh016/project
vercel --prod

# Follow prompts, accept defaults
```

### Set Environment Variables (Important!)

After deployment:
1. Go to your project on Vercel dashboard
2. Click **Settings** → **Environment Variables**
3. Add:
   - Key: `GEMINI_API_KEY`
   - Value: `your-gemini-api-key-here`
   - Scope: **Production, Preview, Development**
4. Click **"Save"**
5. **Redeploy** the project (go to Deployments → Click latest → Click "Redeploy")

### Test Backend

```bash
# Test health check
curl https://your-vercel-url.vercel.app/health

# Should return:
# {"status":"healthy","service":"DetectAI Backend"}

# View API docs
# https://your-vercel-url.vercel.app/docs
```

**✅ Backend deployed!** Get your URL and proceed to frontend.

---

## 🟢 FRONTEND DEPLOYMENT (Streamlit Cloud)

### Step 1: Deploy App

1. Go to **https://streamlit.io/cloud**
2. Sign in with GitHub
3. Click **"New app"**
4. Fill in:
   - **Repository**: `Irfanshaikh016/project`
   - **Branch**: `main`
   - **Main file path**: `frontend/app.py`
5. Click **"Deploy"**
6. Wait for deployment (2-3 minutes)
7. You'll get URL: `https://detectai-xxxxx.streamlit.app`

### Step 2: Add Secrets

After deployment completes:

1. Click **⋮** (menu) → **Settings**
2. Go to **Secrets** tab
3. Add (in TOML format):
   ```toml
   BACKEND_URL = "https://your-vercel-url.vercel.app"
   GEMINI_API_KEY = "your-gemini-api-key-here"
   ```
4. Click **"Save"**
5. App will auto-refresh with secrets

### Step 3: Test Frontend

1. Open your Streamlit URL in browser
2. In sidebar, enter your Gemini API key (or use secrets)
3. Click **"🚀 Generate AI Crime Case"**
4. Wait for case to generate
5. Try:
   - Scanning locations
   - Interrogating suspects
   - Submitting verdict

**✅ Frontend deployed!**

---

## 🔗 Final URLs

After both deployments:

```
Frontend:  https://your-streamlit-app.streamlit.app
Backend:   https://your-vercel-project.vercel.app
API Docs:  https://your-vercel-project.vercel.app/docs
Health:    https://your-vercel-project.vercel.app/health
```

---

## 🧪 Full Integration Test

1. Open **Streamlit frontend URL** in browser
2. Enter Gemini API key in sidebar
3. Select difficulty: **Easy**
4. Click **"🚀 Generate AI Crime Case"**
5. Verify:
   - ✅ Case generates (connects to backend)
   - ✅ Locations load
   - ✅ Can scan locations
   - ✅ Can interrogate suspects
   - ✅ Backend saves data
   - ✅ Can submit verdict

**If all pass: 🎉 Full deployment successful!**

---

## 🔧 Troubleshooting

### Backend won't deploy
**Solution**: Check Vercel logs
```bash
vercel logs --follow
```
Make sure `GEMINI_API_KEY` is set in environment variables.

### Frontend can't connect to backend
**Solution**: 
1. Verify `BACKEND_URL` in Streamlit secrets
2. Check browser console (F12) for errors
3. Make sure backend URL doesn't have trailing slash
4. Restart Streamlit app

### Case generation fails
**Solution**:
1. Verify Gemini API key is valid
2. Check API key isn't rate-limited (free tier limit: 60 requests/min)
3. Increase timeout or try again

### Database errors
**Solution**: SQLite works fine on free tier. If data persists issues:
- Data resets when Vercel redeploys
- For production: upgrade to Vercel Pro or use external DB

---

## 📊 Architecture Summary

```
┌─────────────────────────────────────────┐
│  Streamlit Cloud Frontend               │
│  https://your-app.streamlit.app         │
│  (Hosts frontend/app.py)                │
└──────────────┬──────────────────────────┘
               │ HTTP Requests
               ▼
┌─────────────────────────────────────────┐
│  Vercel Backend (Serverless)            │
│  https://your-project.vercel.app        │
│  (Runs api/index.py with Mangum)        │
│  ├─ Gemini API calls                    │
│  ├─ SQLite database (ephemeral)         │
│  └─ Case/verdict storage                │
└─────────────────────────────────────────┘
```

---

## 📚 Key Files

- **Backend API**: `api/index.py` (Vercel handler)
- **Frontend App**: `frontend/app.py` (Streamlit)
- **Database**: `backend/database/db.py` (SQLite)
- **Routes**: `backend/routes/cases.py` (API endpoints)
- **Services**: `backend/services/gemini_service.py` (AI logic)

---

## ✨ After Deployment

1. **Share your app URL** with friends/faculty
2. **Monitor logs** for any errors
3. **Test all features** thoroughly
4. **Keep Gemini API key secure** (never commit)
5. **Scale up** if needed (Vercel Pro for better specs)

---

## 🎯 Success Indicators

✅ Backend health check returns 200  
✅ Frontend loads without errors  
✅ Can generate crime case  
✅ Can interrogate suspects  
✅ Verdicts are saved  
✅ Leaderboard shows scores  

---

## 📞 Support

- **Vercel Issues**: https://vercel.com/docs
- **Streamlit Issues**: https://docs.streamlit.io
- **Gemini API Issues**: https://ai.google.dev
- **GitHub Issues**: Create issues in your repo

---

**You're all set! 🚀 Time to deploy DetectAI to the cloud!**
