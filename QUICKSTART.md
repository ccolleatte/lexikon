# 🚀 Lexikon - Quick Start Guide

**Sprint 1 Implementation - Full Stack Application**

This guide will get you up and running with Lexikon in **5 minutes**.

---

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **npm** or **pnpm** (package manager)

---

## Setup (5 minutes)

### 1. Clone & Install

```bash
cd lexikon

# Install frontend dependencies
npm install

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Start Backend (Terminal 1)

```bash
cd backend
python main.py
```

✅ Backend running at **http://localhost:8000**
📚 API docs at **http://localhost:8000/docs**

### 3. Start Frontend (Terminal 2)

```bash
npm run dev
```

✅ Frontend running at **http://localhost:5173**

### 4. Open Application

Open your browser to **http://localhost:5173**

---

## What's Included

### ✅ Frontend (SvelteKit + TailwindCSS)

- **Homepage** with feature overview
- **Onboarding Flow**:
  - US-001: Adoption Level Selection (3 levels)
  - US-003: Profile Setup (with validation)
- **Terms**:
  - US-002: Quick Draft Creation (5-minute form)
  - Auto-save functionality
  - Real-time validation
  - Progress tracking

### ✅ Backend (FastAPI)

- **3 API Endpoints**:
  - `POST /api/onboarding/adoption-level`
  - `POST /api/users/profile`
  - `POST /api/terms`
  - `GET /api/terms`
- **In-memory database** (Sprint 1 MVP)
- **Pydantic validation**
- **CORS enabled** for local development

### ✅ Components (6 production-ready)

- Button (5 variants, 3 sizes)
- Input (with char counter, validation)
- Textarea (with auto-resize option)
- Select (custom styled dropdown)
- Progress (4 variants, animated)
- Alert (4 variants with icons)
- Stepper (onboarding progress)

---

## User Flow

1. **Visit Homepage** → Click "Commencer"
2. **Select Adoption Level** → Choose Quick Project, Research, or Production
3. **Complete Profile** → Fill required fields (first name, last name, email)
4. **Create First Term** → Quick Draft mode (name + definition)
5. **See Success** → Term created in < 5 minutes! 🎉

---

## API Examples

### Create Term

```bash
curl -X POST http://localhost:8000/api/terms \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Épistémologie",
    "definition": "Étude critique des sciences, destinée à déterminer leur origine logique, leur valeur et leur portée.",
    "domain": "Philosophie",
    "level": "quick-draft",
    "status": "draft"
  }'
```

### Create User Profile

```bash
curl -X POST http://localhost:8000/api/users/profile \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Marie",
    "lastName": "Dupont",
    "email": "marie@test.fr",
    "language": "fr",
    "sessionId": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

## Development

### Frontend

```bash
npm run dev          # Start dev server
npm run build        # Build for production
npm run preview      # Preview production build
npm run check        # Type checking
```

### Backend

```bash
python main.py       # Start with auto-reload
```

---

## Testing the Full Flow

### Manual Test Checklist

- [ ] Homepage loads and shows 3 feature cards
- [ ] Click "Commencer" → Redirects to onboarding
- [ ] Select "Projet Rapide" → CTA button enables
- [ ] Click "Continuer" → Profile page shows with stepper
- [ ] Fill profile (Marie, Dupont, marie@test.fr) → CTA enables
- [ ] Click "Continuer" → Redirects to terms page
- [ ] Click "+ Nouveau terme" → Quick Draft page loads
- [ ] Fill name "Test" → Error shows (min 3 chars)
- [ ] Fill name "Test Term" → Error clears
- [ ] Fill definition (50+ chars) → Progress bar updates
- [ ] Click "Créer le terme" → Success!

### Expected Time

- **Onboarding**: ~1 minute
- **Profile Setup**: ~30 seconds
- **First Term**: ~2 minutes
- **Total**: < 4 minutes ✅ (Target: < 5 minutes)

---

## Troubleshooting

### Frontend not connecting to backend?

- Ensure backend is running on port 8000
- Check console for CORS errors
- Vite proxy is configured in `vite.config.js`

### Backend errors?

- Check Python version: `python --version` (needs 3.10+)
- Reinstall dependencies: `pip install -r requirements.txt`
- Check logs in terminal

### Port already in use?

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

---

## Next Steps

### For Sprint 2

- [ ] PostgreSQL + Neo4j database integration
- [ ] Real authentication (JWT + OAuth)
- [ ] AI relation suggestions
- [ ] Collaborative validation
- [ ] Import/Export (CSV, RDF)
- [ ] LLM configuration (BYOK)

### Current Limitations (Sprint 1)

- ⚠️ **Data is in-memory** (lost on restart)
- ⚠️ **No authentication** (fake tokens)
- ⚠️ **No avatar upload** yet
- ⚠️ **No AI suggestions** yet

These are intentional simplifications for MVP.

---

## Documentation

- **User Stories**: `user-stories/`
- **Wireframes**: `wireframes/`
- **Design System**: `docs/design/`
- **API Specs**: `docs/backend/api-specifications-sprint1.md`
- **Developer Handoff**: `docs/design/developer-handoff-guide.md`

---

## Support

If you encounter issues:

1. Check this QUICKSTART guide
2. Review error logs in terminal
3. Consult API docs at http://localhost:8000/docs
4. Check developer handoff guide

---

**Enjoy using Lexikon! 🎓📚**

*Version 0.1.0 - Sprint 1 Implementation*
