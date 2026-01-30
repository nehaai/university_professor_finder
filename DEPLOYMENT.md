# Deployment Guide

This guide covers deploying the University Professor Finder with:
- **Frontend**: Vercel (free tier)
- **Backend**: Railway (free tier)

## Prerequisites

1. [GitHub account](https://github.com)
2. [Vercel account](https://vercel.com) (sign up with GitHub)
3. [Railway account](https://railway.app) (sign up with GitHub)

## Step 1: Push Code to GitHub

```bash
# Initialize git if not already done
cd /path/to/uni_prof
git init

# Add all files
git add .
git commit -m "Initial commit - University Professor Finder"

# Create a new repo on GitHub, then:
git remote add origin https://github.com/YOUR_USERNAME/uni-prof-finder.git
git branch -M main
git push -u origin main
```

## Step 2: Deploy Backend to Railway

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"** → **"Deploy from GitHub Repo"**
3. Select your repository
4. Railway will auto-detect the `backend` folder. If not:
   - Click on the service → **Settings** → **Root Directory** → Set to `backend`
5. Wait for the build to complete
6. Click **"Generate Domain"** to get your public URL (e.g., `https://uni-prof-backend.railway.app`)
7. Add environment variables in **Settings** → **Variables**:
   ```
   PORT=8000
   ALLOWED_ORIGINS=https://your-vercel-app.vercel.app
   ```

### Verify Backend Deployment

Visit `https://your-backend.railway.app/docs` to see the API documentation.

## Step 3: Deploy Frontend to Vercel

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **"Add New..."** → **"Project"**
3. Import your GitHub repository
4. Configure the project:
   - **Framework Preset**: Next.js
   - **Root Directory**: `frontend`
5. Add environment variable:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend.railway.app
   ```
6. Click **"Deploy"**

### Verify Frontend Deployment

Visit your Vercel URL (e.g., `https://uni-prof-finder.vercel.app`)

## Step 4: Update CORS (Important!)

After deploying the frontend, update the backend's ALLOWED_ORIGINS:

1. Go to Railway Dashboard → Your project → Variables
2. Update `ALLOWED_ORIGINS`:
   ```
   ALLOWED_ORIGINS=https://uni-prof-finder.vercel.app,https://your-custom-domain.com
   ```
3. Railway will automatically redeploy

## Environment Variables Reference

### Backend (Railway)

| Variable | Description | Example |
|----------|-------------|---------|
| `PORT` | Server port (Railway sets automatically) | `8000` |
| `ALLOWED_ORIGINS` | Comma-separated frontend URLs | `https://app.vercel.app` |
| `SEMANTIC_SCHOLAR_API_KEY` | (Optional) For higher rate limits | `your_key` |
| `OPENALEX_EMAIL` | (Optional) For polite pool access | `you@email.com` |

### Frontend (Vercel)

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `https://backend.railway.app` |

## Custom Domain (Optional)

### Vercel
1. Go to Project → Settings → Domains
2. Add your domain and follow DNS instructions

### Railway
1. Go to Service → Settings → Networking
2. Click "Custom Domain" and follow instructions

## Monitoring & Logs

### Railway
- View logs: Project → Deployments → Click on deployment → Logs
- Monitor: Project → Metrics

### Vercel
- View logs: Project → Deployments → Click on deployment → Functions tab
- Analytics: Project → Analytics

## Troubleshooting

### CORS Errors
- Ensure `ALLOWED_ORIGINS` on Railway includes your Vercel URL
- Check there are no trailing slashes

### 500 Errors on Search
- Backend might be cold starting (Railway free tier sleeps after inactivity)
- Wait 10-15 seconds and retry
- Check Railway logs for specific errors

### Slow Response Times
- First request after inactivity triggers cold start
- Consider Railway Pro for always-on deployment

## Costs

### Free Tier Limits

**Vercel Free:**
- 100GB bandwidth/month
- Serverless function invocations: 100K/month
- Perfect for this app

**Railway Free:**
- $5 free credit/month
- ~500 hours of uptime
- Sleeps after 10 min inactivity

### Upgrading
- Vercel Pro: $20/month (faster builds, more bandwidth)
- Railway Pro: $5/month (no sleep, more resources)

## Local Development

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Visit http://localhost:3000
