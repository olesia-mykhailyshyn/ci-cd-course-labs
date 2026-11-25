import os
import time

import psycopg
import redis
from flask import Flask, jsonify, request

PORT = int(os.environ.get("PORT", "8080"))
DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
HOLD_TTL_SECONDS = int(os.environ.get("HOLD_TTL_SECONDS", "300"))
DB_RETRIES = 30

app = Flask(__name__)
holds = redis.Redis.from_url(REDIS_URL, decode_responses=True)


def db():
    return psycopg.connect(DATABASE_URL, connect_timeout=3)


def wait_for_db():
    for attempt in range(1, DB_RETRIES + 1):
        try:
            with db() as conn:
                conn.execute("SELECT 1")
            print(f"db ready after {attempt} attempt(s)", flush=True)
            return
        except psycopg.OperationalError as exc:
            print(f"db not ready ({attempt}/{DB_RETRIES}): {exc}", flush=True)
            time.sleep(1)
    print("giving up on the database, only /health will work", flush=True)


def hold_key(tutor_id, slot):
    return f"hold:{tutor_id}:{slot}"


@app.get("/health")
def health():
    return "ok\n"


@app.get("/tutors")
def list_tutors():
    with db() as conn:
        rows = conn.execute("SELECT id, name, subject FROM tutors ORDER BY id").fetchall()
    return jsonify([{"id": r[0], "name": r[1], "subject": r[2]} for r in rows])


@app.post("/holds")
def create_hold():
    body = request.get_json(silent=True) or {}
    tutor_id = body.get("tutor_id")
    slot = body.get("slot")
    if not tutor_id or not slot:
        return jsonify(error="tutor_id and slot are required"), 400
    with db() as conn:
        booked = conn.execute(
            "SELECT 1 FROM lessons WHERE tutor_id = %s AND slot = %s", (tutor_id, slot)
        ).fetchone()
    if booked:
        return jsonify(error="slot is already booked"), 409
    created = holds.set(hold_key(tutor_id, slot), "held", nx=True, ex=HOLD_TTL_SECONDS)
    if not created:
        return jsonify(error="slot is already held"), 409
    return jsonify(tutor_id=tutor_id, slot=slot, expires_in=HOLD_TTL_SECONDS), 201


@app.post("/lessons")
def create_lesson():
    body = request.get_json(silent=True) or {}
    tutor_id = body.get("tutor_id")
    slot = body.get("slot")
    student = body.get("student")
    if not tutor_id or not slot or not student:
        return jsonify(error="tutor_id, slot and student are required"), 400
    try:
        with db() as conn:
            lesson_id = conn.execute(
                "INSERT INTO lessons (tutor_id, slot, student) VALUES (%s, %s, %s) RETURNING id",
                (tutor_id, slot, student),
            ).fetchone()[0]
    except psycopg.errors.UniqueViolation:
        return jsonify(error="slot is already booked"), 409
    except psycopg.errors.ForeignKeyViolation:
        return jsonify(error="tutor not found"), 404
    holds.delete(hold_key(tutor_id, slot))
    return jsonify(id=lesson_id, tutor_id=tutor_id, slot=slot, student=student), 201


@app.get("/lessons")
def list_lessons():
    with db() as conn:
        rows = conn.execute("SELECT id, tutor_id, slot, student FROM lessons ORDER BY id").fetchall()
    return jsonify([{"id": r[0], "tutor_id": r[1], "slot": r[2], "student": r[3]} for r in rows])


if __name__ == "__main__":
    if DATABASE_URL:
        wait_for_db()
    app.run(host="0.0.0.0", port=PORT)
