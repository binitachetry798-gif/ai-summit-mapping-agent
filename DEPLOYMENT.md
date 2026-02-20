# 🚀 Deployment Guide — MSE Agent Mapping Tool

Since this project is fully containerized and uses modern frameworks, deployment is straightforward.

## Option 1: Cloud Deployment (Recommended)

### 1. Backend + Database (via Render.com)
We've included a `render.yaml` Blueprint to auto-deploy the FastAPI backend and PostgreSQL database.

1. Push your code to a GitHub repository.
2. Sign up for [Render](https://render.com).
3. Click **New +** → **Blueprint**.
4. Connect your repo.
5. In the **Environment Variables** section, paste the contents of your `backend/.env` file.
   - `SARVAM_API_KEY`: ...
   - `GROQ_API_KEY`: ...
   - `GEMINI_API_KEY`: ...
6. Click **Apply**. Render will:
   - Build the backend
   - Provision a free PostgreSQL database
   - Start the service (it will give you a URL like `https://mse-mapper-backend.onrender.com`)

### 2. Frontend (via Vercel)
We've included `vercel.json` for easy SPA routing.

1. Sign up for [Vercel](https://vercel.com).
2. Click **Add New Project**.
3. Import your GitHub repo.
4. **Build Settings**:
   - Framework Preset: **Vite**
   - Root Directory: `frontend` (Important!)
5. **Environment Variables**:
   - `VITE_API_URL`: Paste your Render backend URL (e.g., `https://mse-mapper-backend.onrender.com`)
6. Click **Deploy**.

---

## Option 2: Local Docker Deployment (If Docker Installed)

If you have Docker Desktop installed, you can run the entire stack locally with one command:

```bash
docker-compose up --build
```
This starts:
- Frontend on `http://localhost:5173`
- Backend on `http://localhost:8000`
- PostgreSQL Database

---

## Option 3: Quick Demo Tunneling (ngrok)

To instantly share your running localhost with someone over the internet:

1. Install ngrok: `npm install -g ngrok`
2. Expose Frontend: `ngrok http 5173`
3. Expose Backend: `ngrok http 8002`

*Note: You'll need to update `frontend/.env` to point to the ngrok backend URL.*
