# qa — the suite, and the stack it drives

Both of these are **given**. Nothing in this folder is yours to write unless you go for the second
bonus.

| File | |
|---|---|
| `compose.qa.yaml` | the stack: the **pulled** image, Postgres behind a health gate, the partner behind a profile |
| `test_smoke.py` | five scenarios that drive the app over HTTP — health, ready, the counter, a 404, and `/price` both ways |

## Running it on your machine

```bash
# whatever your pipeline published, by digest
export QA_IMAGE=ghcr.io/you/catshop@sha256:...

docker compose -f lab-03/qa/compose.qa.yaml up -d --wait
QA_BASE_URL=http://localhost:8080 python3 -m pytest lab-03/qa -q
docker compose -f lab-03/qa/compose.qa.yaml down -v
```

Three commands. That is the whole of what an AQA stage does, and the bonus is putting those three
commands in a job with the digest coming from your build.

## The two things in here that are the lesson

**The app service has no `build:`.** It cannot have one. Every compose file you have written so far
built an image; this one pulls a digest, because an AQA run tests **what was published**, not what
this machine can make a minute later. A wrong digest means nothing starts — which is the correct
failure.

**The partner is behind a profile, so by default it is absent** and `/price` answers `502`. Add
`--profile partner` and the stub from `../partner/mappings/` answers properly. `QA_PROFILE` reaches
the suite as an environment variable, so **one case asserts both outcomes** and the stack decides
which applies:

```bash
docker compose -f lab-03/qa/compose.qa.yaml --profile partner up -d --wait
QA_PROFILE=partner QA_BASE_URL=http://localhost:8080 python3 -m pytest lab-03/qa -q
```

That is the move lab 5 makes with three environments: same suite, different address, different
expectations — and the suite is told which.

## What the suite reads from the environment

| variable | default | |
|---|---|---|
| `QA_BASE_URL` | `http://localhost:8080` | the address to drive |
| `QA_PROFILE` | unset | `partner` means the partner is up, so `/price` should answer `200` |

And what `compose.qa.yaml` reads:

| variable | default | |
|---|---|---|
| `QA_IMAGE` | — | **required.** The image to test, as a digest |
| `QA_PORT` | `8080` | the host port the app is published on |
| `POSTGRES_PASSWORD` | `qa-only` | the database password for a throwaway stack |
