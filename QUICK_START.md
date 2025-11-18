# Quick Start Guide

## 🚀 Fastest Way to Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup (optional - for Gemini API)
python setup_api_key.py

# 3. Extract data (if not done)
python main.py

# 4. Setup backend
python setup_backend.py

# 5. Start server
python start_server.py
```

Then open: **http://localhost:8000**

---

## 📋 What Was Fixed

✅ **Root endpoint now serves frontend HTML** (was showing JSON before)
- Changed `/` JSON endpoint to `/api` 
- Frontend is now accessible at `http://localhost:8000`

---

## 🔍 Quick Test

### Test Backend
```bash
# Health check
curl http://localhost:8000/health

# Query test
curl "http://localhost:8000/query?q=What%20is%20the%20expense%20ratio?"
```

### Test Frontend
1. Open browser: http://localhost:8000
2. You should see the FAQ Assistant UI
3. Click an example question or type your own
4. Click "Ask" button

---

## 📁 Important Files

- **Backend API**: `api.py`
- **Frontend**: `frontend/index.html`
- **Full Guide**: `README.md`
- **Configuration**: `.env` (create this)

---

## ⚠️ Common Issues

**Frontend shows JSON instead of HTML?**
- Restart the server: `python start_server.py`
- Clear browser cache (Ctrl+Shift+R)

**API connection failed?**
- Check backend is running: `curl http://localhost:8000/health`
- Verify port 8000 is not in use

**No data?**
- Run: `python main.py` to scrape fund data
- Then: `python setup_backend.py` to build index

---

For detailed instructions, see: **README.md**
