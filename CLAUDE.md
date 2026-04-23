# Reword — Project Context for AI Agents

Web app for learning English words via flashcards + spaced repetition (SM-2/Anki-style).
Commercial product, 10k+ words planned. Target audience: Russian speakers learning English.

---

## Stack

| Layer | Tech |
|---|---|
| Backend | Python, FastAPI, Uvicorn, Pydantic v2 |
| DB | PostgreSQL 17, SQLAlchemy (async), asyncpg, Alembic |
| Auth | JWT (python-jose), bcrypt direct — **passlib removed**, incompatible with bcrypt 5.x |
| Storage | MinIO (local dev) → S3/Cloudflare R2 (prod), aiobotocore |
| Frontend | Next.js 16.2.4 (App Router), TypeScript, Tailwind CSS |

Architecture patterns: Repository, Service, Unit of Work, Abstract base classes.

---

## Domain Model

- **Card**: word, translation, example (used for phonetic transcription), audio_path, image_path
- **Deck**: groups cards by difficulty (beginner / intermediate / advanced)
- **Review**: SM-2 record — ease_factor, interval, repetitions, next_review, introduced_date
- **User**: JWT auth, daily_new_limit (default 20)

Study UI: 3 rating buttons — «Не помню» (q=1), «Хочу повторить» (q=3), «Запомнил» (q=5)

---

## Local Dev Setup

**Infrastructure:**
- PostgreSQL 17: `localhost:5432`, user=`reword`, password=`reword`, db=`reword` (native, not Docker)
- MinIO: `localhost:9000` (API), `localhost:9001` (console), creds=`minioadmin/minioadmin`, bucket=`reword`
- Backend: `localhost:8002`
- Frontend: `localhost:3000`

**Alembic uses psycopg2 (sync)** for migrations — asyncpg has issues on Windows.

**MinIO requires a public read policy (GetObject)** — without it audio won't play.
Set via aiobotocore `put_bucket_policy` (already configured in docker-compose createbuckets service).

**Start everything:**
```bash
docker compose up minio -d          # MinIO only
uvicorn src.main:app --port 8002    # backend (native)
cd frontend && npm run dev           # frontend
python -X utf8 scripts/seed_words.py --limit 5000  # seed words + audio
```

> **edge-tts (audio TTS) fails inside Docker** (Microsoft 403) — run seed locally only.

---

## File Structure

```
src/
  main.py                    # FastAPI app, CORS, routers
  core/
    config.py                # Settings via pydantic-settings
    deps.py                  # get_current_user, get_uow
    security.py              # JWT create/verify, bcrypt hashing
    exceptions.py            # Custom HTTP exceptions
  db/
    models/{user,deck,card,review}.py
    session.py               # async engine + sessionmaker
  repositories/
    base.py                  # Abstract base repo
    {user,deck,card,review}.py
  services/
    {user,deck,card,review}.py
    storage.py               # MinIO/S3 via aiobotocore
  schemas/
    {user,deck,card,review,token}.py  # Pydantic v2
  uow/
    base.py                  # Abstract UoW
    sqlalchemy.py            # SQLAlchemy implementation
  api/v1/
    auth.py, decks.py, cards.py, reviews.py, users.py

frontend/
  app/
    (auth)/login/page.tsx
    (auth)/register/page.tsx
    (app)/decks/page.tsx           # deck list, Learn/Review buttons
    (app)/decks/[id]/study/page.tsx  # study mode (learn + review)
    (app)/decks/[id]/stats/page.tsx  # deck statistics
    (app)/settings/page.tsx          # daily limit slider
    (app)/layout.tsx
  lib/
    api.ts                   # axios wrapper, all API calls
    auth.ts                  # token management (localStorage)
```

---

## API Endpoints

```
POST /api/v1/auth/login
POST /api/v1/auth/register
POST /api/v1/auth/refresh

GET  /api/v1/users/me
PATCH /api/v1/users/me           # update daily_new_limit

GET  /api/v1/decks
GET  /api/v1/decks/{id}
GET  /api/v1/decks/{id}/cards
GET  /api/v1/decks/{id}/learn-cards   # new cards, respects daily_new_limit
GET  /api/v1/decks/{id}/review-cards  # due for review today (SM-2)
GET  /api/v1/decks/{id}/stats

POST /api/v1/reviews             # submit SM-2 result
```

---

## Current Status (as of 2026-04-23)

### Done
- All models, repositories, schemas, services wired up
- JWT auth (access + refresh tokens)
- SM-2 spaced repetition (ReviewService)
- All API routes
- 24/24 tests passing (SQLite in-memory)
- Seed pipeline: 356 words in DB, ~232+ with audio in MinIO
- Docker Compose (minio + createbuckets + migrate + app)
- Full Next.js frontend: login, register, deck list, study, stats, settings
- Audio plays from MinIO directly via `NEXT_PUBLIC_STORAGE_URL`
- Daily new word limit with slider UI + presets (5/10/20/30/50)
- Separate "Учить (N)" / "Повторить (M)" buttons, greyed when 0
- Learn mode (`?mode=learn`) and Review mode (`?mode=review`)

### Not done yet (next steps)
1. **Images for cards** — `image_path` field exists in the model, needs Unsplash API or similar
2. **Full seed run** — `python -X utf8 scripts/seed_words.py --limit 5000` (currently ~356 words)
3. **Production deploy** — docker-compose.prod.yml, Nginx reverse proxy, SSL
4. **Flutter mobile app** — later, when App Store budget is available

---

## Key Decisions (do not reverse without reason)

- Audio served directly from MinIO/S3 URLs, not proxied through FastAPI
- Docker used **only for deploy** — local dev runs everything natively
- Frontend is Next.js (web-first); Flutter comes later
- passlib removed — use bcrypt directly (passlib broken with bcrypt 5.x)
- Grey Learn/Review buttons when count = 0 is intentional UX
- Alembic runs with psycopg2 (sync driver), not asyncpg

## Known Fixed Bugs (don't reintroduce)

- Login was querying by email instead of username → fixed
- CardService.list_by_deck blocked access to system decks → fixed
- CORS missing → added CORSMiddleware
- Audio URL was `/media/` path instead of MinIO → fixed
- MinIO bucket was private → public GetObject policy applied
- `useSearchParams` in Next.js 16 requires Suspense boundary → StudyPage wrapped

---

## Working with this project

- Propose each step, wait for approval before writing code
- All UI text is in Russian
- Tests live in `tests/` and use SQLite in-memory (no real DB needed)
- Run tests: `pytest`
