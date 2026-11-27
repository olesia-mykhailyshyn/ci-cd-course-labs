# Lab 4 — declare the place, do not click it

**Three sections, plus bonuses. Due Wednesday 9 December, 23:59 Kyiv.** After that, 80% maximum.

This lab runs on a **real server**, at a real URL, with your state in a real backend. It costs you
nothing: you are given an account on the course server, and the state backend has a free tier. No
cloud account, no card, no bill — and no application of your own yet either. That is the next lab.
This one is about the place the application will live: a database, two copies of a web server and a
proxy in front of them, all written down instead of clicked.

Your place answers at:

```
https://grizik.tech/<your-github-login>/
```

**You are already registered** if you have submitted at least one lab — your space was created from
your submission issues. If you have never submitted, send me your repository link in the chat and I
will add you. You will know it worked when the `prove who this run is` step goes green; a `403`
there means you are not on the roster yet, which is not something you can fix from your side.

---

## Before anything else — three one-time steps

| step | where | what to do |
|---|---|---|
| 1 | [app.terraform.io](https://app.terraform.io) | sign up (free), then **Account settings → Tokens → Create an API token**. A *user* token: an organization token cannot run a plan |
| 2 | your repository | variable `TF_CLOUD_ORGANIZATION` = your HCP organization · secret `TF_API_TOKEN` = that token |
| 3 | your HCP workspace | create `lab-04`, and set **Execution Mode: Local** |

Step 3 is not a formality. The course server is reachable only from inside *your pipeline run*, with
a certificate that run is issued for one hour. HCP's own runners have neither the route nor the
certificate, so a workspace left on Remote execution cannot work — and that is exactly what happens
with a private endpoint behind a VPC at work.

**The repository must be under your personal account.** The server identifies you from the GitHub
claim `repository_owner_id`; a repository owned by an organization presents the organization's id
and is refused.

### Your whole workflow file

You do not write the deployment plumbing. Copy this into `.github/workflows/lab-04.yml`:

```yaml
name: lab 4
on:
  push:         { branches: [main], paths: ["lab-04/terraform/**"] }
  pull_request: { paths: ["lab-04/terraform/**"] }

permissions:
  contents: read
  id-token: write          # without this there is no token and no certificate

jobs:
  deploy:
    uses: kse-ci-cd-basics-course/catshop-grader/.github/workflows/lab-04-deploy.yml@v1
    with:
      hcp_org: ${{ vars.TF_CLOUD_ORGANIZATION }}
    secrets:
      TF_API_TOKEN: ${{ secrets.TF_API_TOKEN }}
```

Note the `paths:` filter. It covers the Terraform folder and nothing else: editing a README is not a
reason to touch infrastructure. Note also that it plans on a pull request and applies on `main` —
the shape lecture 6 argued for, and the reason you see your plan before it happens.

There is **no secret for the server** anywhere in that file. Your pipeline proves who it is with a
token GitHub mints for the run, and gets back a certificate valid for one hour that can run exactly
one command in exactly one account. If you find yourself wanting an SSH key, you have taken a wrong
turn.

---

## Section 1 · The place, declared

A network, a volume, a **database**, **two copies of a web server from one resource**, and a
**proxy** in front of them. Public images only — you build nothing and you start nothing by hand.

**Write:** `lab-04/terraform/main.tf`, `lab-04/terraform/variables.tf`,
`lab-04/terraform/outputs.tf`, `lab-04/terraform/backend.tf`, `lab-04/terraform/nginx.conf.tftpl`
(the proxy's configuration, and the file the grader reads by name — any further templates are
yours to name)

**Requirements:**

- `required_version` is set, and `required_providers` pins **`kreuzwerker/docker`** at a version —
  not at whatever the registry served today
- the provider's `host` comes from a **variable**. The workflow sets it as `TF_VAR_docker_host`; a
  default that only works on your own machine is a default that breaks in CI
- **four names are fixed**, because one grader reads every configuration in the class: the variables
  `docker_host`, `port` and `bind_ip`, and the output `url`. Everything else is yours
- one `docker_network`, one `docker_volume`, and **three containers**: a database, the web copies,
  and the proxy
- the database is **`postgres:16-alpine`**, its volume is mounted at its data directory, and it
  **publishes no port at all**. Containers find each other by name on the network; a database on a
  host port is reachable by anything that can route to the box
- its password is **not typed into the file**. Take it from a variable or generate it with
  `random_password` — and then notice where it ends up, which is what one of the bonuses is about
- the web copies are **`nginx:1.27-alpine`** with `keep_locally = true`, and they are **one
  resource with `count`**, never two blocks that happen to look alike. No `build` block in this lab
- the proxy is the **only** container with a `ports` block, and it binds to **`var.bind_ip`** on
  `var.port`. Both are given to you
- `nginx.conf.tftpl` is **rendered with `templatefile(...)`** and its upstream list is
  **generated** — a `%{ for ... }` loop over the copies' names. If you type `web-0` and `web-1` into
  the template by hand, raising `count` to three silently does nothing
- `GET /health` through your URL returns `200`, and `GET /whoami` returns the answering copy's
  hostname. nginx does both on its own — `return 200 "ok\n";` and `return 200 "$hostname\n";` — so
  no application code is needed. Several requests to `/whoami` must return **more than one** name
- `terraform init && terraform apply` is the whole command. No shell script, no `local-exec`, no
  `compose` file hiding underneath

**In the pull request:** what `terraform apply` created in what order, and what in your file decided
that order · the rendered upstream block, and what it looks like after you change `count` · why the
database has no `ports` block and still works.

## Section 2 · The state is the point

**Write:** `lab-04/terraform/backend.tf`, and a `.gitignore` that means it

**Requirements:**

- `backend.tf` declares `cloud {}` — **empty**. Organization and workspace come from the
  environment, which is what lets one configuration work for everyone. A `backend "local"` block, or
  no block at all, fails this section
- **a second `terraform plan` reports no changes.** Graded on the exit code, not on the words "No
  changes." appearing in a log
- no state file is committed, and `git log` has never seen one. With `cloud {}` there should be
  nothing to commit — if there is, something is configured wrongly
- `terraform destroy` leaves nothing behind: no container, no network, no volume

**In the pull request:** where your state lives now, and what would have happened on the second run
if it had lived on the runner · what `terraform destroy` printed.

## Section 3 · Drift, and the plan that notices it

Stop **one web copy** behind Terraform's back, look at what each side believes, then put it back
with Terraform rather than by hand. You have no shell on the server, so you do this through the
Docker API your pipeline already talks to — one step in a workflow, with `DOCKER_HOST` already set
for you.

**Write:** `lab-04/DRIFT.md`

**Requirements:**

- one copy is stopped **without Terraform**, so the state still says it is running
- **your URL keeps answering `200`.** That is the finding, not luck: the proxy has another copy to
  reach. It needs `proxy_next_upstream` and a `proxy_connect_timeout` short enough that the retry
  happens inside the request — a stopped container refuses the connection instantly, and without
  those two lines the refusal is what your caller gets
- `terraform plan` notices anyway, exits **2**, and reports exactly **one** resource to put back —
  not the network, not the volume, not the database, which really are still there
- `terraform apply` repairs it, and `/whoami` returns two names again
- `DRIFT.md` records the `plan` line as it printed, what `apply` then did, and the one sentence that
  explains **why Terraform knew** — the mechanism, not the observation

> Your place is removed automatically after 48 hours of nobody touching it. That is not a
> malfunction: it is this same experiment arriving by itself, and re-running your pipeline is the
> repair.

**In the pull request:** why `plan` proposed one resource and not four · what your users saw while
one copy was down, and which line in your template decided that · what would have happened if you
had deleted the workspace's state instead of the container.

---

## Bonus · reports, cannot cost you marks

None of these costs money. Do as many as you like, or none.

### + Raise it to three

Change `count` to 3 and apply. If your upstream list is generated, this is a one-line change and
the proxy picks up the third copy by itself; if it is not, this is where you find out. Show the
rendered block before and after, and say what `plan` proposed.

### + The state is a secret

Your database password is in your state, whether you generated it with `random_password` or passed
it in. Find it — in HCP a workspace's state is readable in the UI — and say in the pull request who
else can read it there, and what that means for every password a pipeline ever creates.

### + Two applies at once

Start a second run while the first is still applying. Say what the second one said, and which part
of the system said it. One sentence on what would have happened without it.

### + What this would cost rented

Price the same shape at a cloud you do **not** have an account with: a load balancer, two small
instances, a managed database. One line per resource, what the whole thing costs a month if nobody
ever sends it a request, and which single line is the most expensive. No account, no card — this is
research, not a deployment.

---

## The server, and how to be a good neighbour

You share one machine with the rest of the class. It is not generous, and the limits are real rather than
advisory:

| | |
|---|---|
| memory | 512 MB, plus 128 MB of swap |
| CPU | half a core |
| processes | 512 |
| disk | 2 GB |
| deployments at once | **10 across the whole class** |

If all ten deployments are busy when your job starts, it **waits** — you will see a step called
*"Wait for a free deployment slot"* counting down. That is normal near a deadline. If it gives up,
the message says so in as many words: nothing was created, nothing was broken, re-run the job. A
failure that says *"this is not a problem with your code"* is not a problem with your code.

You cannot reach another student's account, containers, ports, home directory or processes. Please
do not spend the lab finding out — if you do find a way, tell me, and I will say so in the lecture
with your name on it.

---

## Handing it in

Pull request into your own `main`, template filled in, then a **submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the PR URL. The issue timestamp is your submission time.

A committed state file, a committed token, or configuration you cannot explain, scores zero.
