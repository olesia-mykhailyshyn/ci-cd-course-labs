# Lab 3 — a pipeline that does not repeat itself

**Two sections. Due Wednesday 2 December, 23:59 Kyiv.** After that, 80% maximum.

Given: `app.py`, `requirements.txt`, `.env.example`, `partner/mappings/`, and the QA suite and its
stack at `qa/` — `compose.qa.yaml`, `test_smoke.py`, `README.md`. Do not change `app.py`.

Push and read the checks. Each section is one check with a table behind it.

---

## Section 1 · One definition, called twice

**Write:** `.github/workflows/<caller>.yml`, `.github/workflows/_build-and-test.yml`,
`.github/actions/<name>/action.yml`, `lab-03/Dockerfile`, `lab-03/requirements-dev.txt`,
`lab-03/tests/test_*.py`

**Requirements:**

- a job in the caller runs `uses:` against your own workflow file
- `_build-and-test.yml` declares `on: workflow_call` with **typed** inputs, and reads them
- it declares an **output**, and the caller reads it back through `needs.<job>.outputs`
- a **composite action** (`using: composite`) is called from inside the reusable workflow
- `pytest` appears in **one** workflow file; the image is built in **one** workflow file
- every third-party `uses:` is at a tag or a sha, never a branch
- workflows live at the repository root, and none is named `lab-03.yml` — that is the grader

**In the pull request:** what the reusable workflow cannot do that the composite action can · what
you passed in, what came back, and the error you hit getting it · what happens if the tag you call
moves tonight.

## Section 2 · Both caches, and the minutes

**Write:** cache steps in your workflows, a reordered `lab-03/Dockerfile`, and `lab-03/CACHE.md`

**Requirements:**

- a **dependency** cache: `actions/cache` or a `setup-*` `cache:` key
- a **layer** cache: `cache-from` and `cache-to`, with `mode=max`
- the key contains `hashFiles(...)`, and `restore-keys` gives it a prefix fallback
- the Dockerfile copies and installs requirements **before** the source
- `CACHE.md` holds a cold time, a warm time, the saving, and **both run URLs** — the grader reads
  those runs back out of the API and compares their real durations

**In the pull request:** the two numbers and which cache did the work · the key you tried first and
why it was wrong · one thing you did not cache, and why.

---

## Bonus · reports, cannot cost you marks

### + The AQA stage

**Write:** `.github/workflows/_qa.yml` (or the job wherever you put it), `lab-03/published.txt`

**Requirements:**

- the job is handed the **digest** your build produced, never a tag, and `latest` appears nowhere
- it stands up `lab-03/qa/compose.qa.yaml`, runs `lab-03/qa`, and tears the stack down
- the pull, the stack and the suite are **steps in the job**, not a script
- `published.txt` is one line, the digest, and the job that writes it is reachable **only through
  QA**
- `qa/compose.qa.yaml` keeps pulling an image: no `build:` in it
- the app serves on container port `8080`

**In the pull request:** where the digest came from · what the suite would and would not have caught.

### + Your own scenarios

**Write:** `lab-03/qa/test_<yours>.py`, `lab-03/qa/REGRESSION.md`

**Requirements:** three or more scenarios of your own beside the given five · one of them expects a
failure · the suite runs over a **matrix** (`QA_PROFILE=partner` is the second row) · the report is
uploaded as an artifact · `REGRESSION.md` names one incident and the case that exists because of it.

### + Concurrency

**Write:** a `concurrency:` block, `lab-03/CONCURRENCY.md`

**Requirements:** the group is keyed on the ref, not a constant · `cancel-in-progress` is not a bare
`true` on the publishing path · a run on your branch was really cancelled · `CONCURRENCY.md` has
both run URLs, what was cancelled, and why that one was safe.

---

## Handing it in

Pull request into your own `main`, template filled in, then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed `.env`, or configuration you cannot explain, scores zero.
