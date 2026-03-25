# Deployment Guide

## Architecture

- Database: Supabase Postgres with pgvector
- Backend: Render web service
- Frontend: Vercel project from `frontend/`
- LLM API: Gemini 2.5 Flash via `GEMINI_API_KEY` on Render

## 1. Supabase

1. Create a new Supabase project.
2. Open SQL Editor.
3. Run the SQL in `infra/supabase_setup.sql`.
4. This creates the schema and inserts starter cafe data.
5. Copy the connection string and keep `sslmode=require`.

Example:

```env
DATABASE_URL=postgresql+psycopg2://postgres:password@db.example.supabase.co:5432/postgres?sslmode=require
```

Quick verification queries:

```sql
select count(*) from recipes;
select count(*) from ingredients;
select count(*) from recipe_ingredients;
select name, sugar_g from products order by sugar_g desc;
```

## 2. Render Backend

1. Create a new Web Service from this repository.
2. Render can read `render.yaml`, or you can set the same values manually.
3. Add these environment variables:

```env
GEMINI_API_KEY=your_gemini_api_key
DATABASE_URL=your_supabase_connection_string
EMBED_MODEL=text-embedding-004
CHAT_MODEL=gemini-2.5-flash
EMBED_DIM=768
ALLOWED_ORIGINS=https://your-frontend.vercel.app
```

4. Deploy and confirm `/health` returns healthy.

## 3. Vercel Frontend

1. Create a new Vercel project using the `frontend/` directory as Root Directory.
2. Add:

```env
VITE_API_URL=https://your-render-service.onrender.com
```

3. Deploy.

## 4. Final Wiring

1. Copy the Vercel URL.
2. Update `ALLOWED_ORIGINS` on Render to that exact URL.
3. Redeploy Render once.
4. Test chat, upload, and document delete flows from the live frontend.

## Notes

- Render filesystem is ephemeral, so uploaded raw files are temporary. The chunked data is stored in Supabase after processing.
- Keep the real `.env` and API keys private. Use `.env.example` as the template.
- If you want the fastest Supabase setup, use `infra/supabase_setup.sql`. The older `infra/init_pgvector.sql` is still useful for local Docker initialization.
