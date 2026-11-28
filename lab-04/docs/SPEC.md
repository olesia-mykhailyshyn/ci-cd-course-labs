# Lab 4 — spec

What we build, how we know it is done, in what order. Decisions are in `ADR.md`.

## Goal

The place the application will live, written as Terraform instead of clicked: one network, one volume, a database, two web copies from one resource, and a proxy in front of them. It comes up on the course server from `terraform apply` alone, its state lives off the runner, and a plan notices when reality drifts from the state.

## The shape

```
            https://grizik.tech/<login>/        (course server, shared entry)
                        │
                     proxy (nginx)   ← the only container with a published port
                   bind_ip : port → 80
                    ┌──────┴──────┐
                  web-0         web-1           ← nginx:1.27-alpine, one resource, count = 2
                        │
                       db (postgres:16-alpine) + volume   ← no published port
            ───────── one docker_network, found by name ─────────
```

## Files

| File | What |
|---|---|
| `lab-04/terraform/main.tf` | providers, network, volume, images, db, web (count), proxy, random_password |
| `lab-04/terraform/variables.tf` | `docker_host`, `port`, `bind_ip` (fixed names), `public_url`, `replicas` |
| `lab-04/terraform/outputs.tf` | `url` (fixed name) |
| `lab-04/terraform/backend.tf` | empty `cloud {}` |
| `lab-04/terraform/nginx.conf.tftpl` | proxy config, upstream generated with `%{ for }` |
| `lab-04/terraform/web.conf` | web copy config: `/health` → ok, `/whoami` → `$hostname` |
| `.github/workflows/lab-04.yml` | the deploy caller: plan on a PR, apply on main |
| `.github/workflows/lab-04-drift.yml` | the drift experiment, run by hand |
| `lab-04/DRIFT.md` | the drift write-up |
| `lab-04/docs/SPEC.md`, `lab-04/docs/ADR.md` | this, and the decisions |

`app.py` and the course's grader file are not ours to keep: the grader file at `.github/workflows/lab-04.yml` is replaced by our deploy caller, as the assignment says.

## Contracts the grader fixes

- variables named `docker_host`, `port`, `bind_ip`; output named `url`;
- the provider's `host` comes from `var.docker_host` (the workflow sets `TF_VAR_docker_host`);
- the database publishes no port; only the proxy does, bound to `var.bind_ip`.

## Done when

**Section 1 · the place** — `terraform apply` builds it from the files alone; `/health` is 200; several `/whoami` return more than one name; no `build`, no `local-exec`.

**Section 2 · the state** — `backend.tf` is empty `cloud {}`; a second `plan` is empty; no state file in git history; `destroy` leaves nothing.

**Section 3 · drift** — one web copy stopped outside Terraform; the URL keeps answering 200; `plan` exits 2 and proposes exactly one resource; `apply` repairs it; `DRIFT.md` records it.

## Blocks

**Local** — written and checked on the laptop with Docker, no server.

| # | Block | Gate |
|---|---|---|
| L1 | terraform files + web/proxy configs | `terraform apply` locally: 9 resources, `/health` 200, two copies on `/whoami`, second plan empty, `destroy` clean |
| L2 | drift, locally | one copy stopped: 20/20 `/health` 200, `plan` exit 2 one resource, `apply` repairs |
| L3 | the two workflows | `actionlint` clean; grader `config` section 0 fail |
| L4 | docs: SPEC, ADR, DRIFT draft | reviewed |

**On the server** — needs HCP and the roster.

| # | Block | Gate | Evidence |
|---|---|---|---|
| S1 | HCP org, token secret, org variable, workspace | — | — |
| S2 | push branch, open PR | the deploy job plans on the PR | the plan |
| S3 | merge to main | apply; `/health` 200; two copies | the live URL |
| S4 | run `lab-04-drift` by hand | URL stays up, plan exit 2 one resource, apply repairs | screenshots |
| S5 | finalise `DRIFT.md`, PR text; submission issue | — | — |
