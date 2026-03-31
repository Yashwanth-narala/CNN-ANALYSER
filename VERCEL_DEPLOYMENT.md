# Vercel Deployment Guide

## Important Architecture Note

This project has:
- `frontend/` (React app) -> deploy on Vercel
- `backend/` (Flask + TensorFlow/OpenCV) -> deploy on a backend host (Render/Railway/VM)

Vercel is best used here for the frontend. The current backend is heavy for Vercel serverless limits.

## 1) Deploy Backend First

Deploy `backend/` to a Python host and get your backend URL, for example:
- `https://lc-cnn-api.onrender.com`

Make sure CORS in backend allows your Vercel frontend domain.

## 2) Deploy Frontend on Vercel

### Option A: Dashboard (recommended)
1. Import repository in Vercel.
2. Set **Root Directory** to `frontend`.
3. Framework preset: `Create React App` (auto-detected).
4. Add environment variable:
   - `REACT_APP_API_BASE_URL` = your deployed backend URL
5. Deploy.

### Option B: Vercel CLI
```bash
cd frontend
vercel
```
Then set env variable in Vercel project settings:
- `REACT_APP_API_BASE_URL`

## 3) Frontend Environment Variable

The frontend now uses:
- `REACT_APP_API_BASE_URL` (fallback: `http://localhost:5000`)

API calls are built with `frontend/src/config.js`.

## 4) CORS Setup (Backend)

Update backend CORS origins to include:
- Your Vercel domain (`https://your-app.vercel.app`)
- Optional custom domain

## 5) Verify After Deploy

1. Open Vercel frontend URL.
2. Upload an image and run analysis.
3. Confirm metrics load and CSV/PDF downloads work.
4. Check browser console/network for CORS or mixed-content errors.

