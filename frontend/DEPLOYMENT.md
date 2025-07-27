# GitHub Pages Deployment Guide

This guide will help you deploy your frontend app to GitHub Pages.

## Prerequisites

1. Your code should be pushed to a GitHub repository
2. Node.js and npm should be installed locally
3. Your backend API should be deployed separately (if needed)

## Deployment Options

You have two options for deployment:

### Option 1: Automatic Deployment with GitHub Actions (Recommended)

This is already set up! The workflow in `.github/workflows/deploy.yml` will automatically:
- Build your app when you push to the `deploy` branch
- Deploy it to GitHub Pages

#### Steps:
1. **Enable GitHub Pages in your repository:**
   - Go to your GitHub repository
   - Navigate to Settings → Pages
   - Under "Source", select "GitHub Actions"

2. **Update your backend URL:**
   - Deploy your Python backend to a service like:
     - Railway: https://railway.app/
     - Render: https://render.com/
     - Heroku: https://heroku.com/
     - AWS/Google Cloud/Azure

3. **Set your backend URL:**
   - In your repo, go to Settings → Secrets and variables → Actions
   - Click "New repository secret"
   - Name: `VITE_API_BASE_URL`
   - Secret: Your deployed backend URL (e.g., `https://your-app.railway.app`)
   - This is REQUIRED for deployment to work properly!

4. **Push to deploy branch:**
   ```bash
   git add .
   git commit -m "Deploy to GitHub Pages"
   git push origin deploy
   ```

5. **Access your deployed app:**
   - Your app will be available at: `https://yourusername.github.io/GenXData/`

### Option 2: Manual Deployment

If you prefer to deploy manually:

1. **Install dependencies:**
   ```bash
   cd frontend
   npm install
   ```

2. **Install gh-pages:**
   ```bash
   npm install --save-dev gh-pages
   ```

3. **Build and deploy:**
   ```bash
   npm run deploy
   ```

## Configuration Files Created

- **`vite.config.ts`**: Updated with GitHub Pages base path
- **`package.json`**: Added deployment scripts and gh-pages dependency
- **`.github/workflows/deploy.yml`**: GitHub Actions workflow for automatic deployment
- **`public/404.html`**: Handles client-side routing for SPAs on GitHub Pages
- **`src/main.tsx`**: Updated with basename for proper routing
- **`src/lib/api.ts`**: Environment-based API configuration

## Environment Variables

Create a `.env` file in the frontend directory for local development:

```bash
# .env
VITE_API_BASE_URL=http://localhost:8000
```

For production, set the environment variable in GitHub Actions or update the default in `api.ts`.

## Backend Deployment

Your frontend will need a deployed backend. Popular options:

1. **Railway** (Recommended for Python apps):
   ```bash
   pip install railway
   railway login
   railway init
   railway up
   ```

2. **Render** (Free tier available):
   - Connect your GitHub repo
   - Select Python environment
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python api.py` or `uvicorn api:app --host 0.0.0.0 --port $PORT`

3. **Heroku**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## CORS Configuration

Make sure your backend allows requests from your GitHub Pages domain:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://yourusername.github.io"  # Add your GitHub Pages URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Troubleshooting

### Common Issues:

1. **404 errors on page refresh:**
   - The `404.html` file should handle this automatically

2. **API calls failing:**
   - Check if your backend URL is correct
   - Verify CORS settings
   - Check browser console for errors

3. **Assets not loading:**
   - Verify the `base` path in `vite.config.ts` matches your repository name

4. **Build failures:**
   - Check that all dependencies are in `package.json`
   - Ensure TypeScript has no errors: `npm run lint`

### Testing Locally:

Test the production build locally before deploying:

```bash
npm run build:gh-pages
npm run preview
```

## Custom Domain (Optional)

If you have a custom domain:

1. Add a `CNAME` file to `frontend/public/` with your domain
2. Update the GitHub Actions workflow to include your domain
3. Configure DNS to point to GitHub Pages

Your app is now ready for GitHub Pages deployment! 🚀
