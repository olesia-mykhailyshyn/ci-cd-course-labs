# Lab 3 — spec

What we build, how we know it is done, and in what order. Decisions are in `ADR.md`.

## Goal

One pipeline in which every step is written once: a reusable build, a reusable QA stage and a composite action. It caches dependencies and Docker layers, cancels runs nobody needs, and ships an image only after QA has tested exactly that image.

## The pipeline

```
push to lab-03 (or run by hand)
 └─ lab-03-pipeline.yml
     ├─ build    uses _build-and-test.yml     composite action runs pytest; build and push; returns the digest
     ├─ qa       uses _qa.yml, gets the digest  matrix: default, partner; uploads a report
     └─ promote  needs qa                      prints the digest for published.txt
```

## Contracts

**`_build-and-test.yml`** (`on: workflow_call`)

| | Name | Type | Meaning |
|---|---|---|---|
| in | `python-version` | string | Python for the unit tests, e.g. `"3.12"` |
| in | `image` | string | image name without a tag, e.g. `ghcr.io/olesia-mykhailyshyn/catshop` |
| in | `lab-path` | string | the folder with the Dockerfile and the tests, e.g. `lab-03` |
| out | `digest` | — | `sha256:…` of the pushed image |
| out | `image-ref` | — | `<image>@sha256:…` |

**`_qa.yml`** (`on: workflow_call`)

| | Name | Type | Meaning |
|---|---|---|---|
| in | `image-ref` | string | the image to test, by digest |

**`install-and-test`** (composite action)

| | Name | Meaning |
|---|---|---|
| in | `python-version` | Python to install |
| in | `working-directory` | the lab folder, `lab-03` |

## Files

| File | Block |
|---|---|
| `lab-03/docs/SPEC.md`, `lab-03/docs/ADR.md` | 1 |
| `lab-03/Dockerfile`, `.dockerignore`, `requirements-dev.txt`, `tests/test_app.py`, `tests/test_price.py` | 2 |
| `.github/actions/install-and-test/action.yml` | 3 |
| `.github/workflows/_build-and-test.yml`, `lab-03-pipeline.yml` | 3 |
| `.github/workflows/_qa.yml`, `lab-03/qa/test_stack.py`, `lab-03/qa/REGRESSION.md` | 5 |
| `lab-03/published.txt` | 6 |
| `lab-03/CACHE.md` | 7 |
| `lab-03/CONCURRENCY.md` | 8 |

`app.py` and the given files in `qa/` are not changed.

## Done when

**Section · reuse** (required)

- a caller job runs `uses: ./.github/workflows/_build-and-test.yml`;
- both reusable files declare typed inputs and read them;
- `digest` comes back and the caller reads `needs.build.outputs`;
- the composite action is called from `_build-and-test.yml`;
- QA is reusable and is handed the image with `with:`;
- unit `pytest` lives in one place and the image is built in one file;
- every third-party `uses:` is at a tag;
- a run shows a job named `build / …`.

**Section · cache** (required)

- `actions/cache` with `hashFiles(...)` in the key and `restore-keys`;
- `cache-from` and `cache-to` with `mode=max`;
- requirements are copied and installed before the source;
- `CACHE.md` has a cold time, a warm time, the saving and both run URLs, and the warm run is at least 20% shorter.

**Bonus · qa**

- the stack comes up from `qa/compose.qa.yaml` by digest, the suite runs, the stack comes down;
- no `build:` in the QA stack and no `:latest` on the QA path;
- `promote` runs only after QA;
- `published.txt` is one line: `ghcr.io/…@sha256:…`.

**Bonus · aqa**

- at least three of my own scenarios, one expecting a failure;
- a matrix with `partner` as the second row;
- the report uploaded as an artifact;
- `REGRESSION.md` names the incident and the test it produced.

**Bonus · concurrency**

- the group is keyed on the ref and the workflow;
- cancelling depends on the ref;
- a run on `lab-03` was really cancelled;
- `CONCURRENCY.md` has both run URLs and why cancelling was safe.

## Blocks

Each block ends with a gate. The next block starts only when the gate is green.

**Local** — written and checked on the laptop before anything is pushed.

| # | Block | Gate |
|---|---|---|
| L1 | docs: `SPEC.md`, `ADR.md` | reviewed |
| L2 | lab folder: Dockerfile, `.dockerignore`, unit tests | 9 unit tests green; the image builds and holds only `app.py` |
| L3 | composite action, `_build-and-test.yml`, caller, both caches, concurrency | `actionlint` clean; grader `reuse` 0 fail |
| L4 | `_qa.yml`, `qa/test_stack.py`, `qa/REGRESSION.md` | the QA stack against a local image: 9 of 9 in both profiles; grader `aqa` 0 fail |

**On GitHub** — needs real runs.

| # | Block | Gate | Evidence for the pull request |
|---|---|---|---|
| G1 | sync `main`, create `lab-03`, commit, push with no `packages: write` | GitHub refuses the nested job | the error text |
| G2 | add `packages: write`, push | build, both QA rows and promote green | inputs, outputs, the fix, the digest |
| G3 | delete the caches, run by hand twice | the second run at least 20% shorter | two times, the saving |
| G4 | run by hand twice in a row | the first run is cancelled | both run URLs |
| G5 | `published.txt`, `CACHE.md`, `CONCURRENCY.md`, push | every grader section green | — |
| G6 | pull request and submission issue | `pull request · complete` green | — |
