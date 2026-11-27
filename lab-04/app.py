"""
Marsik's spaceship shop — the app we containerize.

Five endpoints, and two of them exist only because there is now more than one of me:

    /health   nothing          is the process alive
    /visits   OUR state        a counter. File-backed, or Postgres when DATABASE_URL is set
    /price    SOMEBODY ELSE'S  calls the partner catalog API over HTTP
    /whoami   WHICH COPY       the hostname answering. Two replicas, two answers
    /version  WHICH COMMIT     the sha this image was built from, or "unknown"

Everything comes from the environment. Nothing comes from the machine it happens to run on.
"""
import os
import socket
import time
from pathlib import Path

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

PARTNER_URL = os.environ.get("PARTNER_URL", "http://partner:8080")
PARTNER_TIMEOUT = float(os.environ.get("PARTNER_TIMEOUT", "2"))
COUNTER_FILE = Path(os.environ.get("COUNTER_FILE", "/data/visits.txt"))
# When DATABASE_URL is set the counter moves to Postgres. Same image, different composition.
DATABASE_URL = os.environ.get("DATABASE_URL")
DB_RETRIES = int(os.environ.get("DB_RETRIES", "30"))
# Baked in at build time (--build-arg GIT_SHA), not set at run time. A version that
# can be changed without rebuilding is not telling you which code is running.
GIT_SHA = os.environ.get("GIT_SHA", "unknown")


# --------------------------------------------------------------------- storage
def _db():
    import psycopg

    return psycopg.connect(DATABASE_URL, connect_timeout=3)


def init_db():
    """The database is a separate container and starts at its own pace.

    depends_on does not wait for readiness, so we retry instead of dying.
    """
    for attempt in range(1, DB_RETRIES + 1):
        try:
            with _db() as conn:
                conn.execute(
                    "CREATE TABLE IF NOT EXISTS visits ("
                    "  id serial PRIMARY KEY, at timestamptz DEFAULT now())"
                )
            print(f"db ready after {attempt} attempt(s)", flush=True)
            return True
        except Exception as exc:  # noqa: BLE001 - any driver error means "not yet"
            print(f"db not ready ({attempt}/{DB_RETRIES}): {exc}", flush=True)
            time.sleep(1)
    print("giving up on the database - /visits will answer 503", flush=True)
    return False


def bump_file():
    COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
    n = int(COUNTER_FILE.read_text().strip() or 0) if COUNTER_FILE.exists() else 0
    n += 1
    COUNTER_FILE.write_text(str(n))
    return n


def bump_db():
    with _db() as conn:
        conn.execute("INSERT INTO visits DEFAULT VALUES")
        return conn.execute("SELECT count(*) FROM visits").fetchone()[0]


# --------------------------------------------------------------------- routes
@app.get("/health")
def health():
    """Liveness. Says nothing about the database or the partner, on purpose."""
    return "ok\n"


@app.get("/ready")
def ready():
    """Readiness: can this process actually serve traffic right now?"""
    try:
        if DATABASE_URL:
            with _db() as conn:
                conn.execute("SELECT 1")
            return jsonify(ready=True, store="postgres")
        COUNTER_FILE.parent.mkdir(parents=True, exist_ok=True)
        return jsonify(ready=True, store=f"file:{COUNTER_FILE}")
    except Exception as exc:  # noqa: BLE001
        return jsonify(ready=False, error=str(exc)), 503


@app.get("/whoami")
def whoami():
    """Which copy answered. With one replica this is noise; with two it is the lesson."""
    return jsonify(
        host=socket.gethostname(),
        # Set by whatever started this container. The load balancer does not set it.
        instance=os.environ.get("INSTANCE_ID", socket.gethostname()),
        # Present only when something is proxying for us — and every load balancer does.
        forwarded_for=request.headers.get("X-Forwarded-For"),
        forwarded_proto=request.headers.get("X-Forwarded-Proto"),
    )


@app.get("/version")
def version():
    """The commit this image was built from. The deployment check reads this."""
    return jsonify(sha=GIT_SHA)


@app.get("/visits")
def visits():
    """Our own state. This is what volumes and then Postgres are for."""
    try:
        n = bump_db() if DATABASE_URL else bump_file()
        return jsonify(visits=n, store="postgres" if DATABASE_URL else "file")
    except Exception as exc:  # noqa: BLE001
        return jsonify(error=str(exc), store="postgres" if DATABASE_URL else "file"), 503


@app.get("/price/<sku>")
def price(sku):
    """Somebody else's API. We do not own it, cannot restart it, and must not call it from tests."""
    url = f"{PARTNER_URL}/v1/catalog/{sku}"
    try:
        r = requests.get(url, timeout=PARTNER_TIMEOUT)
        r.raise_for_status()
        body = r.json()
        return jsonify(sku=sku, price=body.get("price"), currency=body.get("currency"), source=url)
    except Exception as exc:  # noqa: BLE001
        # The failure is the interesting part: it is how we see network isolation working.
        return jsonify(sku=sku, error=type(exc).__name__, detail=str(exc)[:200], source=url), 502


if __name__ == "__main__":
    if DATABASE_URL:
        init_db()
    port = int(os.environ.get("PORT", "8080"))
    print(f"cat shop up on {port} / store={'postgres' if DATABASE_URL else COUNTER_FILE}", flush=True)
    app.run(host="0.0.0.0", port=port)
