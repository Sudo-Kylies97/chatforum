# Verity Forum

Verity is a text-first web forum built for the Full Stack Software Engineer assessment. Anyone can read discussions; authenticated users can post, comment, and like; moderators make the final call on misinformation labels. The AI extensions are moderation assistance (A) and thread vibe analysis (B).

## Run locally

Requirements: Docker Desktop with Compose. No local Python, Node, PostgreSQL, or Redis installation is required.

```bash
cp .env.example .env
docker compose up --build
```

Open the Angular application at <http://localhost:4200>, API documentation at <http://localhost:8000/api/docs/>, and Django admin at <http://localhost:8000/admin/>. The initial image build can take several minutes.

Demo accounts are recreated safely on every start:

| Role | Username | Password |
| --- | --- | --- |
| Regular | `alex` | `VerityDemo123!` |
| Regular | `sam` | `VerityDemo123!` |
| Moderator/admin | `moderator` | `VerityMod123!` |

The forum remains fully usable without an AI key: leave `AI_API_KEY` empty and AI operations fail open with visible unavailable states. For live AI features, set a key and OpenAI-compatible models in `.env`.

## Architecture and decisions

- **Django REST Framework** supplies mature password/session authentication, permissions, migrations, admin user management, pagination, and OpenAPI generation without external auth.
- **Angular** provides a typed, responsive single-page interface. Focused OnPush components handle presentation, while a signal-based `ForumStore` owns session, feed, filter, loading/error, moderation, and token state. Django session cookies and CSRF protect browser writes.
- **PostgreSQL** is the durable source of truth. Feed queries annotate counts and prefetch comments/authors to avoid N+1 access.
- **Synchronous AI analysis** keeps moderation and vibe results available immediately for this small assessment deployment, with bounded provider timeouts and fail-open behavior.
- **Personal API tokens** are random, revocable bearer credentials for automation. Only SHA-256 digests are stored, and the secret is displayed once.

AI pre-flags are visible only to moderators. They never automatically publish a misinformation label: a human moderator must confirm it. Moderation and vibe analysis can each be enabled independently with `AI_MODERATION_ENABLED` and `AI_VIBE_ENABLED`. Vibe is recalculated after comments are added and is displayed as a badge on the post.

## API usage

All endpoints are under `/api/v1/`. Anonymous clients may list/retrieve posts and categories. Browser clients use `/auth/csrf/` then `/auth/login/`. Automated clients create a token in the Developer Access panel and send it as:

```http
Authorization: Bearer vf_your_token
```

Core endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET/POST` | `/posts/` | List or create posts |
| `POST` | `/posts/{id}/comments/` | Add a comment |
| `POST/DELETE` | `/posts/{id}/like/` | Like or unlike |
| `POST` | `/posts/{id}/moderation/` | Moderator public-label decision |
| `POST` | `/posts/{id}/retry_ai/` | Moderator AI retry |
| `GET/POST/DELETE` | `/tokens/` | Manage personal tokens |

Import [postman/Verity-Forum.postman_collection.json](postman/Verity-Forum.postman_collection.json) and select its local variables. The collection demonstrates login, post creation, comments, likes, moderation, and bearer-token use. Before assessment submission, publish that collection from the candidate's Postman workspace and place the public URL here: **`PUBLIC_POSTMAN_URL_PENDING`**.

## Development and verification

For local development without Docker, use Python 3.12+ and Node 22+, run PostgreSQL, then adjust `DATABASE_URL`:

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
.venv/bin/python backend/manage.py migrate
.venv/bin/python backend/manage.py seed_demo
.venv/bin/python backend/manage.py runserver
npm install --prefix frontend
npm start --prefix frontend
```

Verification:

```bash
.venv/bin/python backend/manage.py test forum
.venv/bin/python backend/manage.py check
npm test --prefix frontend -- --browsers=ChromeHeadless --code-coverage
npm run build --prefix frontend
./scripts/api-smoke.sh
```

The automated suites mock every AI provider response and connection failure. They do not require `AI_API_KEY`, internet access, Redis, or paid API credits.

The smoke script expects the Docker stack at `localhost:8000`. It logs in with the seeded account and exercises authenticated post creation.


