# Lab 2 — test, build, publish

**Three sections. Due Thursday 19 November, 23:59 Kyiv.** After that, 80% maximum.

Given, inside `lab-02/`: `app.py` and `requirements.txt` (do not change them),
`partner/mappings/`, `.env.example` — copy it to `.env`, never commit it.

| Endpoint | Depends on | Section |
|---|---|---|
| `GET /health` | nothing | 1, 3 |
| `GET /ready` | the store it was configured with | 1 |
| `GET /visits` | our own state | 1, 3 |
| `GET /price/<sku>` | an API we do not own | bonus |

Push and read the checks. Each section is one check with a table behind it.

---

## Section 1 · A suite that would notice

**Write:** `lab-02/tests/test_*.py`, `lab-02/requirements-dev.txt`

**Requirements:**

- `pytest` is a declared dependency, and the suite passes
- at least four tests, and they import the app rather than testing Flask
- **break `/health` on purpose and the suite goes red** — a suite that cannot fail is worth nothing
- `/price` needs a partner that is not there: that one is the bonus

**In the pull request:** the one-line mutation and the output that caught it, and which test caught
it · one test you wrote first and deleted, with the reason · how long the suite takes, and whether
that is fast enough for every push.

## Section 2 · One workflow: test, build, publish

**Write:** `.github/workflows/publish-lab-02.yml` — at the repository root, nowhere else runs

**Requirements:**

- one workflow, three stages: the suite, a docker build, a publish to **GHCR**
- the publish job `needs:` the test job, so **a red suite structurally cannot publish**
- `latest` is rejected — tag something that names one build
- the image is labelled `org.opencontainers.image.revision` with the commit it was built from

You will meet a `403` on the first push to GHCR. The fix is one block in the workflow, not a
personal access token.

**In the pull request:** the 403 and the exact change that fixed it, plus why the token was there
but could not do this · what happens on a fork's pull request, in two sentences · your tag scheme,
and what breaks if two pushes produce the same tag.

## Section 3 · An image somebody else can pull

**Write:** `lab-02/published.txt`

**Requirements:**

- one line, nothing else: `ghcr.io/<account>/<image>@sha256:<64 hex characters>`
- a tag is not accepted
- the package is **public** — GHCR packages start private
- the image runs and answers `/health` and `/visits` when pulled by that digest
- its revision label names a commit that is really in your repository, so an image built on your
  laptop fails

**In the pull request:** where the digest came from, pasted from the step that produced it · tag
versus digest, with one scenario where the difference is the whole story · the package's visibility,
where you changed it and what it means.

---

## Bonus · reports, cannot cost you marks

**+ Cache something, and prove it.** Dependencies, Docker layers or both. Key it on something that
changes. Run cold, run warm, and write `lab-02/CACHE.md` with both timings and one sentence on what
got faster. The grader asks the API for the entry your workflow created, by key then by id, and
checks it is not empty.

**+ The partner, stubbed.** Make `/price/MK-II` testable without the real partner —
`wiremock/wiremock:3.6.0` with the stubs in `partner/mappings/`, or fake the HTTP call. Say which
you chose and what it cannot catch.

**+ Docker Hub as well.** Publish the same image there, and say why this course grades on GHCR —
there are at least two reasons.

---

## Handing it in

Pull request into your own `main`, every template heading filled in — an empty required heading
fails the pull request — then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env` — the checks read git *history* — or configuration you cannot explain, scores
zero.
