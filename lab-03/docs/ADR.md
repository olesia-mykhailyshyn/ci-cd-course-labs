# Lab 3 — decisions

Each decision: what we chose, what we rejected, and what the choice costs.
All accepted on 2026-11-27.

## ADR-01 · Four files for the pipeline

| File | Role |
|---|---|
| `.github/workflows/lab-03-pipeline.yml` | the caller: runs on push and calls the others |
| `.github/workflows/_build-and-test.yml` | reusable: tests, build, push; returns the digest |
| `.github/workflows/_qa.yml` | reusable: runs the QA suite against a published image |
| `.github/actions/install-and-test/action.yml` | composite: Python, dependencies, `pytest` |

- **Rejected:** the QA job inline in the caller. Lab 5 calls the same QA against three environments, and the grader requires it to be reusable.
- **Price:** four files to read instead of one.

## ADR-02 · Inputs and outputs

- `_build-and-test.yml` takes `python-version`, `image` and `lab-path` (all `string`) and returns `digest` and `image-ref`.
- `_qa.yml` takes `image-ref` (`string`, a digest reference, never a tag).
- **Rejected:** hardcoding the image name, the Python version or the lab folder inside the reusable files. `lab-path` was added while writing the build: without it the file could only ever build `lab-03`.
- **Price:** every output has to be passed up twice: from the step to the job, then from the job to `workflow_call`.

## ADR-03 · Build with `docker/build-push-action`

- **Chose:** `setup-buildx-action`, `login-action` and `build-push-action`.
- **Rejected:** plain `docker build` and `docker push`, as in lab 2. They cannot use `cache-from` or `cache-to`.
- **Price:** three third-party actions instead of two shell commands, and the build is less visible in the log.

## ADR-04 · Dependency cache: `actions/cache` with my own key

- **Key:** `pip-<os>-py<version>-<hash of lab-03/requirements*.txt>`.
- **Fallback:** `restore-keys: pip-<os>-py<version>-`, so a changed requirements file still starts warm.
- **Where:** in the `test` job of `_build-and-test.yml`, just before the composite action. I first put it inside the composite action, but the grader reads only workflow files, so a cache there is invisible to it. A cache step is also a property of the pipeline, not of "install and test".
- **Tried first:** `cache: pip` in `setup-python`, from lab 2. It works, but I cannot set its fallback.
- **Price:** about ten lines more than `cache: pip`.

## ADR-05 · Layer cache: GitHub's cache, `mode=max`

- **Chose:** `cache-from: type=gha,scope=catshop-lab03` and `cache-to: type=gha,mode=max,scope=catshop-lab03`.
- **Rejected:** a registry cache in GHCR, because it adds a `buildcache` tag to the public package.
- **Price:** it shares the repository's 10 GB cache limit with the pip cache.

## ADR-06 · How cold and warm are measured

- **Cold:** delete every cache (`gh cache delete --all`), then start the pipeline by hand (`workflow_dispatch`).
- **Warm:** start it again straight after, on the same commit.
- **Risk:** the grader compares the duration of the whole run and wants at least 20% saved. The QA stage takes about a minute and is not cached. If the saving is short of 20%, we decide again after measuring.

## ADR-07 · The QA stage

- **Steps in the job:** pull the digest, `docker compose up --wait`, run `pytest lab-03/qa` with a JUnit report, upload the report as an artifact, then `docker compose down -v` with `if: always()`.
- **Matrix:** `default` (no partner) and `partner` (`COMPOSE_PROFILES=partner`, `QA_PROFILE=partner`). `COMPOSE_PROFILES` does the same as `--profile partner`, but lets every `docker compose` step stay one identical line.
- **Rejected:** a shell script that does all of it. The grader and a person at 02:00 both need to read the steps in the workflow.
- **Price:** two QA runners per push instead of one.

## ADR-08 · Promotion and `published.txt`

- **Chose:** a `promote` job in the caller that `needs: qa` and prints the digest. I commit `published.txt` from its output.
- **Rejected:** the pipeline committing `published.txt` itself. That needs `contents: write`, and its commit would start the pipeline again.
- **Price:** one manual step after every image I want to hand in.

## ADR-09 · My own QA scenarios

Four scenarios in `qa/test_stack.py`:

- `/ready` reports `store: postgres`, so `DATABASE_URL` reaches the app;
- two calls to `/visits` both report `store: postgres` and count up;
- `POST /health` answers `405` (the failure case);
- the first `/visits` after the stack is up answers `200`, not `503`.

The last one comes from a real lab 1 incident: the app started before Postgres and logged `Connection refused`. It goes in `qa/REGRESSION.md`.

- **Price:** these assume the QA stack has Postgres. Run against a file-backed app, the first one fails.

## ADR-10 · Concurrency

- **Group:** `${{ github.workflow }}-${{ github.ref }}`, so one branch waits for itself and different workflows never collide.
- **Cancel:** `cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}`.
- **Why it is safe on a branch:** a branch only pushes candidate images by digest. An image counts as ready only after QA, and `main` never cancels.
- **Price:** on a branch, a newer push can stop a run halfway through its push, leaving an untagged layer in GHCR.

## ADR-11 · Permissions

- **Chose:** the caller has `contents: read` only. The `build` job adds `packages: write`.
- **Rejected:** `packages: write` for the whole workflow. QA and promote do not need it.
- **Price:** the permission is written at the call site, away from the push it allows.

## ADR-12 · `lab-03/` reuses lab 2's files as copies

- **Chose:** copy `Dockerfile`, `.dockerignore`, `requirements-dev.txt` and the unit tests from `lab-02/`. `app.py` is identical in both labs.
- **Rejected:** pointing lab 3 at `lab-02/`. Each lab folder is frozen once merged.
- **Price:** two copies of the same tests in the repository.

## ADR-13 · Make the permission error happen on purpose

- **Chose:** the first push leaves `packages: write` out of the `build` call, so GitHub refuses the nested job. That error, and the line that fixes it, go in the pull request.
- **Price:** one red run in the history.

## ADR-14 · No secrets passed

- **Chose:** pass no secrets. Every job uses the run's own `GITHUB_TOKEN`.
- **Rejected:** `secrets: inherit` only to turn a grader warning green. There is no secret to pass.
- **Price:** the grader reports a warning (`reuse:secrets`), which the pull request explains.

## ADR-15 · Third-party actions pinned to a major tag

- **Chose:** tags, the current majors: `checkout@v7`, `setup-python@v7`, `cache@v6`, `upload-artifact@v7`, `setup-buildx-action@v4`, `login-action@v4`, `build-push-action@v7`.
- **Rejected:** full SHAs. Without comments in the code, nobody could tell which version a SHA is.
- **Price:** if a maintainer moves `v7` tonight, tomorrow's run executes different code with no diff in this repository.

## ADR-16 · Same GHCR package as lab 2

- **Chose:** `ghcr.io/olesia-mykhailyshyn/catshop`. It is already public, and every tag is a commit SHA, so the two labs cannot collide.
- **Rejected:** a new `catshop-lab03` package. It would start private and need a manual visibility change.
- **Price:** images from two labs share one package page.

## ADR-17 · Docs live in `lab-03/docs/`

- **Chose:** `SPEC.md` and this file, committed with the lab.
- **Price:** two more files in the pull request, and `docs/` has to stay out of the image (`.dockerignore`).
