# Lab 2 — test, build, publish

Three sections. **Due Thursday 19 November, 23:59 Kyiv.**
After the deadline the maximum for this lab is 80%.

**Sections 1 and 2 are open now. Section 3 opens Thursday 5 November**, once the registry has been
taught. You can finish the first two before it does; nothing in them depends on it.

---

## What you are given

```
app.py                  the same Flask app, one lab older — do not change it
requirements.txt        its three dependencies
partner/mappings/       the partner's stubbed responses, for the bonus
.env.example            copy to .env. Never commit .env
```

## What you write

```
lab-02/Dockerfile              an image for this app (lab 1's is a fine starting point)
lab-02/requirements-dev.txt    whatever your tests need
lab-02/tests/test_*.py         section 1
lab-02/published.txt           section 3 — one line, written by your pipeline
lab-02/CACHE.md                bonus — two numbers

.github/workflows/publish-lab-02.yml    section 2 — at the REPOSITORY ROOT
```

The workflow lives at the repository root because that is **the only place GitHub reads workflows
from**. Everything else lives inside `lab-02/`.

## The application

Unchanged from lab 1, and still four endpoints:

| Endpoint | Depends on | Where it matters here |
|---|---|---|
| `GET /health` | nothing | section 1, section 3 |
| `GET /ready` | the store it was configured with | section 1 |
| `GET /visits` | our own state — a file, or Postgres | section 1, section 3 |
| `GET /price/<sku>` | an API we do not own | bonus |

Run it and the suite locally before you automate anything:

```bash
cd lab-02
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt -r requirements-dev.txt
COUNTER_FILE=./data/visits.txt ./.venv/bin/python app.py     # one terminal
./.venv/bin/python -m pytest tests -q                        # another
```

> **One contract: the app serves on container port `8080`.** Every section that runs your image
> publishes it to host `8080` and probes `http://localhost:8080`.

## How you find out where you stand

**Push.** Each section is a named check. Click one and you get a table: every individual check, pass
or fail, with the reason. Push as often as you like — it costs nothing, and it is the same result
your mark comes from.

What follows says what each section has to **achieve**. It does not list the checks.

---

## Section 1 · a suite that would notice

Write tests for the app and make them pass.

A test that cannot fail is worth nothing, so the bar is not "pytest exits 0". **Break the app on
purpose and your suite must go red.** Try it: change what `/health` returns, run the suite, and if
it still passes, your suite is not testing the thing you think it is.

Test the endpoints that have no external dependency. `/price` needs a partner that is not there —
that one is the bonus, and it needs a stub, not the real thing.

**In the pull request:**

- **The mutation you tried.** Paste the one-line change you made to `app.py` and the test output
  that caught it. Then say which test caught it, and what it asserts.
- One test you wrote **first and deleted**, with the reason. (Everybody writes at least one test
  that only tests Flask.)
- How long the suite takes, and whether that is fast enough to run on every push.

## Section 2 · one workflow: test, build, publish

Write `.github/workflows/publish-lab-02.yml` so that a push to your branch runs the suite, builds
the image, and publishes it to **GHCR** — `ghcr.io/<your-account>/<something>`.

Two things decide this section, and both are about the **shape** of the file rather than its length:

- **A red suite must not be able to publish.** Make that structural, not a matter of ordering.
- **The image must be identifiable.** `latest` is rejected: it is a pointer that can be moved after
  you are graded. Tag it with something that names one build, and **label the image with the commit
  it was built from**, using `org.opencontainers.image.revision`.

You will meet a `403` the first time you push to GHCR. That is expected, and the fix is one block in
the workflow, not a personal access token.

**In the pull request:**

- **Paste the 403** and the exact change that fixed it. One line on *why* the token was there at all
  but could not do this.
- **What happens on a fork's pull request?** Reason it out in two sentences — you do not have to
  demonstrate it.
- Your tag scheme, and **what breaks if two pushes produce the same tag**.

## Section 3 · an image somebody else can pull  *(opens Thu 5 Nov)*

Now prove the thing exists outside your laptop and outside your run.

Put the reference your publish job produced into `lab-02/published.txt` — **one line, nothing else**:

```
ghcr.io/<account>/<image>@sha256:<64 hex characters>
```

A tag is not accepted here. The grader pulls exactly what that line says, runs it, and asks it for
`/health` and `/visits`. It also reads the commit label off the image and checks that commit is
really in your repository, so **an image you built on your laptop and pushed by hand will fail** —
which is the point.

The package has to be **public**, or nobody can pull it. GHCR packages start private.

**In the pull request:**

- **Where the digest came from.** Paste the step output that produced it. If you copied it by hand
  from the UI, say so, and say what would go wrong at scale.
- **Tag versus digest, in your own words**, with one concrete scenario where the difference is the
  whole story.
- The package's visibility: where you changed it, and what it means for who can pull your image.

---

## Bonus — adds marks, never costs them

Bonus checks run with `continue-on-error`, so a red bonus job cannot fail your pipeline.

**+ Cache something, and prove it.** Add a cache to your workflow — dependencies, Docker layers, or
both. Then measure it: run the pipeline cold, run it warm, and write `lab-02/CACHE.md` with **both
timings** and one sentence on what got faster.

Two things make this count rather than decorate:

- **Key it on something that changes.** A key that never changes is a cache that is never refreshed.
- **The cache has to actually exist.** The grader asks the GitHub API for your repository's caches
  and looks for the entry your workflow created — by key, then by id — and checks it is not empty.
  A `cache:` block that silently saved nothing will be visible here.

Caching is marked properly in **lab 3**, on the minutes saved. This is the rehearsal.

**+ The partner, stubbed.** Make `/price/MK-II` testable without the real partner: run
`wiremock/wiremock:3.6.0` with the stubs in `partner/mappings/`, or fake the HTTP call in the suite.
Say in the pull request which you chose and what each approach cannot catch.

**+ Docker Hub as well.** Publish the same image to Docker Hub too, and say in one paragraph why
this course grades on GHCR instead — there are at least two reasons, and one of them is about
strangers sharing your rate limit.

---

## Handing it in

1. Pull request from your `lab-02` branch into **your own** `main`.
2. Fill in every heading in the template. An empty required heading fails the pull request.
3. Open a **submission issue** in your repository with a link to the pull request. Its timestamp is
   your submission time — a pull request nobody was told about is not a submission.

**Two things score zero regardless of green checks:** a committed `.env` (the checks read git
*history*, not just the working tree), and configuration you cannot explain.
