# Tutoring: lesson booking with a tutor

A small Flask service. A student picks a tutor and a time slot, puts a short
hold on the slot, then books the lesson.

- Postgres keeps tutors and booked lessons.
- Redis keeps temporary holds. A hold disappears by itself after `HOLD_TTL_SECONDS`.

## Configuration

Everything comes from environment variables:
`PORT` (default 8080), `DATABASE_URL`, `REDIS_URL`, `HOLD_TTL_SECONDS` (default 300).

## Run

```sh
cp .env.example .env
docker compose up -d app
```

The app listens on http://localhost:8090. The database and Redis have no
published ports. Stop with `docker compose down` (data stays) or
`docker compose down -v` (data is deleted).

## Try it

```sh
curl http://localhost:8090/health
curl http://localhost:8090/tutors
curl -X POST http://localhost:8090/holds -H 'Content-Type: application/json' \
  -d '{"tutor_id":1,"slot":"2026-11-20T10:00"}'
curl -X POST http://localhost:8090/lessons -H 'Content-Type: application/json' \
  -d '{"tutor_id":1,"slot":"2026-11-20T10:00","student":"Olesia"}'
curl http://localhost:8090/lessons
```

A second hold or a second booking for the same tutor and slot returns 409.
