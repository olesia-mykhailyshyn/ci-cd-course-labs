# Lab 4 — decisions

Each: what we chose, what we rejected, what it costs. Accepted 2026-11-28.

## ADR-01 · Providers: kreuzwerker/docker and hashicorp/random

- **Chose:** `kreuzwerker/docker ~> 3.0` (required by the lab) and `hashicorp/random ~> 3.6` for the password. `required_version >= 1.9.0`, which the course's Terraform 1.9.8 and my local 1.15.4 both satisfy.
- **Price:** a second provider to download.

## ADR-02 · Web copies: one resource with `count`

- **Chose:** `docker_container.web` with `count = var.replicas` (default 2), named `catshop-web-${count.index}`.
- **Rejected:** two near-identical blocks. Raising to three would then mean editing the file twice, and the grader checks for `count`.
- **Price:** none worth noting.

## ADR-03 · The proxy config is generated; the web config is static

- **Chose:** `nginx.conf.tftpl` rendered with `templatefile(...)`, its upstream list built by `%{ for host in web_hosts }` over `docker_container.web[*].name`. The web copies get a static `web.conf` read with `file(...)`.
- **Rejected:** typing `web-0`, `web-1` into the template. Then `count = 3` renders nothing new — the most common way to get this lab wrong.
- **Price:** two config files instead of one.

## ADR-04 · Configs reach the containers with `upload`, not a host mount

- **Chose:** `upload { content = ..., file = "/etc/nginx/conf.d/default.conf" }` on the proxy and each web copy.
- **Rejected:** a `volumes` host path. On the course server the host filesystem is not ours, so there is no file there to mount; `upload` sends the content over the Docker API.
- **Price:** the content lives in the Terraform state as well.

## ADR-05 · The database password is a `random_password`

- **Chose:** `random_password.db`, injected as the container's `POSTGRES_PASSWORD` env.
- **Rejected:** a typed literal (it would be in git forever) and a plain variable (someone has to set it). `random_password` is stable across applies, so it does not cause churn.
- **Price:** the password is readable in the state — which is exactly the point the "state is a secret" bonus makes.

## ADR-06 · Only the proxy publishes a port

- **Chose:** the proxy has `ports { internal = 80, external = var.port, ip = var.bind_ip }`; the database and web copies have no `ports`. Everything finds everything else by name on `docker_network.catshop`.
- **Price:** nothing from the host can reach the web copies or the database directly — which is the point.

## ADR-07 · `output "url"` works locally and on the server

- **Chose:** `url = var.public_url != "" ? var.public_url : "http://${var.bind_ip}:${var.port}"`. Locally there is no `public_url`, so the output is the loopback address the probe can reach; on the server the certificate step sets `TF_VAR_public_url` to the real `https://grizik.tech/<login>/`.
- **Price:** one conditional.

## ADR-08 · State: an empty `cloud {}`

- **Chose:** `backend.tf` is `terraform { cloud {} }`. Organization and workspace come from `TF_CLOUD_ORGANIZATION` and `TF_WORKSPACE`, set by the workflow.
- **Rejected:** `backend "local"` (dies with the runner) and no backend at all (every run starts from nothing).
- **Price:** the state lives in HashiCorp's cloud, where its secrets are readable in the UI (ADR-05).

## ADR-09 · Deploy with the assignment's caller; apply on main

- **Chose:** `.github/workflows/lab-04.yml` is the eight-line caller from the assignment. It plans on a pull request and applies on `main`. To deploy, the PR is merged to `main`; the submission is that merged PR, with a note in the issue.
- **Rejected:** `mode: apply` to deploy from a branch. It breaks the plan-then-apply shape the lecture teaches.
- **Price:** for this lab the PR is merged before review, unlike labs 1–3. Explained in the submission.
- **Also:** `ensure_workspace: true` is passed, so the deploy workflow creates the HCP workspace `lab-04` in Local execution mode on the first run, instead of the student setting it by hand in the UI. One less manual step, and it guarantees the Local mode the server needs.

## ADR-10 · Drift is its own workflow, targeting a web copy

- **Chose:** `.github/workflows/lab-04-drift.yml`, run by hand. It gets the certificate, stops a container whose name contains `web` (never the proxy or the database), proves the URL stays up, runs `plan -detailed-exitcode` (expects 2 and one resource), then applies.
- **Rejected:** the deploy workflow's built-in `drift_check`, which stops the first container `docker ps` lists — possibly the proxy, which would take the site down and defeat the failover half of the experiment.
- **Price:** a second workflow file.

## ADR-11 · Failover: `proxy_next_upstream` and a short connect timeout

- **Chose:** in the proxy config, `proxy_next_upstream error timeout http_502 http_503 http_504` and `proxy_connect_timeout 1s`, with `max_fails=1 fail_timeout=2s` on each upstream.
- **Why:** a stopped container refuses connections instantly; without these lines that refusal is what the caller gets. With them, the proxy tries the other copy inside the same request. Proven locally: 20/20 requests answered 200 with one copy stopped.
- **Price:** on a cold start the proxy can briefly pin to one copy before the split evens out; the probe retries for this.

## ADR-12 · Docs in `lab-04/docs/`, `DRIFT.md` at the lab root

- **Chose:** `SPEC.md` and `ADR.md` under `lab-04/docs/`; `DRIFT.md` at `lab-04/DRIFT.md`, where the grader reads it by name.
- **Price:** `docs/` is content the image does not need, but this lab builds no image, so nothing to exclude.
