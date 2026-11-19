# Lab 1 — containers and the image

**Three sections. Due Thursday 12 November, 23:59 Kyiv.** After that, 80% maximum.

Given, inside `lab-01/`: `app.py` and `requirements.txt` (do not change them),
`init-db/01-schema.sql`, `partner/mappings/`, `.env.example` — copy it to `.env`, never commit it.

| Endpoint | Depends on | Section |
|---|---|---|
| `GET /health` | nothing | 1 |
| `GET /visits` | our own state — a file, then a database | 1, then 3 |
| `GET /price/<sku>` | an API we do not own | bonus |

Push and read the checks. Each section is one check with a table behind it.

---

## Section 1 · An image that runs

**Write:** `lab-01/Dockerfile`, `lab-01/.dockerignore`

**Requirements:**

- the image builds, and the app answers on host port **8080**
- the base image is pinned, not floating
- a `CMD` is present
- `.dockerignore` keeps `.env` and the build junk out of the context
- the instructions are ordered so that editing `app.py` does not reinstall the dependencies

**Measure:** build twice, the second time after editing one line of `app.py`. Reorder your
instructions and do it again.

**In the pull request:** what `EXPOSE` actually does, with the output of trying to reach an
unpublished port · both sets of build timings and the reason for the difference · what
`transferring context` did when you added `.dockerignore`.

## Section 2 · An image worth shipping

**Write:** the same `lab-01/Dockerfile`, multi-stage

**Requirements:**

- multi-stage: the build tooling does not ship
- the process does not run as root
- no compiler or package-build toolchain in the final image
- `apt-get update` is never a layer of its own, and no cleanup stranded in its own `RUN`
- the app still does exactly what it did

**In the pull request:** both image sizes, and which change bought which saving · proof the thing you
removed is gone — ask both images for it · the error the less-privileged version hit · the two real
reasons chaining with `&&` matters, and why one enormous `RUN` is also wrong.

## Section 3 · A stack that keeps its data

**Write:** `lab-01/compose.yaml`

**Requirements:**

- services named **`app`** and **`db`** — the checks address them by name
- `docker compose up -d app` is all the checks run: whatever else must be up by then is your file's
  job to express
- the counter lives in PostgreSQL, not in the container's filesystem
- the rows **survive** the containers being destroyed and recreated
- the database port is **not** published: nothing on your laptop connects to it directly
- no literal password in `compose.yaml` — `${POSTGRES_PASSWORD}` and `.env`

**In the pull request:** the data-loss transcript — destroy and restore once losing the rows, once
keeping them, paste both · the log from starting the stack with nothing coordinating app and
database, and what it waits for now · a named volume versus a bind mount, and when you reach for
each.

---

## Bonus · reports, cannot cost you marks

**+ The API you do not own.** Add `wiremock/wiremock:3.6.0` with the stubs in `partner/mappings/` so
`/price/MK-II` answers, and the partner's 500 surfaces as a 502. Produce the two failures the real
partner would never give you on request, and paste both.

**+ Close the doors.** Networks declared explicitly, `internal: true` holding, and the database with
no route out. Reach the database from four places with the real error text for each: your laptop, by
service name on the default bridge, by container IP, and by service name on a network you created —
restarting the database between the third and the fourth. Then say why the attempt that worked was
still wrong.

**+ Redis** as a fourth service, used for something real.

**+ Your own application** (+10). All three sections against a service you wrote, in any language.
`/health`, and configuration from the environment.

---

## Handing it in

Pull request into your own `main`, template filled in — alternatives, measurements and the AI
disclosure each carry marks — then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env`, or configuration you cannot explain, scores zero.
