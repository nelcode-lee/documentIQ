# Environment Variables Setup Guide

## ⚠️ IMPORTANT: Security Best Practices

### DO:
- ✅ Use `.env.example` as a **template** with placeholder values
- ✅ Put **real credentials** in `.env` file (which is gitignored)
- ✅ Keep `.env` file **local only** - never commit it to git
- ✅ Share `.env.example` in your repository so others know what variables are needed

### DON'T:
- ❌ Put real API keys in `.env.example`
- ❌ Commit `.env` file to git
- ❌ Share your `.env` file with others
- ❌ Hardcode credentials in your code

## Setup Steps

### 1. Copy the Example File

**Backend:**
```bash
cd backend
copy .env.example .env
# OR on Linux/Mac:
cp .env.example .env
```

**Frontend:**
```bash
cd frontend
copy .env.example .env
# OR on Linux/Mac:
cp .env.example .env
```

### 2. Fill in Real Values

Edit the `.env` file (not `.env.example`) and replace placeholder values:

**Backend `.env`:**
```env
# Replace these with your actual values
OPENAI_API_KEY=sk-proj-abc123xyz...  # Your real OpenAI API key
AZURE_SEARCH_ENDPOINT=https://your-actual-service.search.windows.net
AZURE_SEARCH_API_KEY=your-actual-search-key
# ... etc
```

**Frontend `.env`:**
```env
VITE_API_BASE_URL=http://localhost:8000
```

### 3. Verify `.env` is in `.gitignore`

Check that your `.gitignore` includes:
```
.env
.env.local
```

### 4. Test It Works

```bash
# Backend
cd backend
python -c "from app.config import settings; print('Config loaded:', settings.openai_api_key[:10] + '...')"

# Frontend
cd frontend
npm run dev
```

## File Structure

```
project/
├── backend/
│   ├── .env.example      ✅ Safe to commit (placeholders only)
│   ├── .env              ❌ Never commit (real credentials)
│   └── .gitignore        ✅ Includes .env
├── frontend/
│   ├── .env.example      ✅ Safe to commit (placeholders only)
│   ├── .env              ❌ Never commit (real credentials)
│   └── .gitignore        ✅ Includes .env
└── .gitignore            ✅ Root level gitignore
```

## What's Protected

The `.gitignore` files ensure:
- `.env` files are **never committed** to git
- `.env.local` and other variants are ignored
- Your credentials stay **local only**

## Sharing with Team

1. Share `.env.example` files (these are safe)
2. Each team member creates their own `.env` from the example
3. Each fills in their own credentials
4. **Never** share actual `.env` files via email/slack/etc.

## Deployment

For production deployments:
- Use environment variables in your hosting platform (Azure App Service, etc.)
- Or use Azure Key Vault for secrets
- Never hardcode credentials in deployment scripts

## Quick Checklist

- [ ] Copied `.env.example` to `.env` in both backend and frontend
- [ ] Filled in real values in `.env` files
- [ ] Verified `.env` is in `.gitignore`
- [ ] Tested that the app loads configuration correctly
- [ ] Never committed `.env` files to git
