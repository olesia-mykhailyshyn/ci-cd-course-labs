# Drift

> Draft from the local run. The exact plan line, the URL and the run link are replaced with the course-server run once it is done; the mechanism below is the same.

## The experiment

One web copy is stopped behind Terraform's back — through the Docker API the pipeline already talks to, not by hand on the server. The state still records the copy as running. Then both sides are looked at: the users, who should not notice, and `terraform plan`, which should.

## What the users saw

The URL kept answering while the copy was down: **20 of 20 requests to `/health` returned 200**. The proxy has a second copy to reach. Two lines in `nginx.conf.tftpl` decide this — `proxy_next_upstream error timeout ...` and `proxy_connect_timeout 1s`: a stopped container refuses the connection instantly, and without them that refusal is what the caller would get; with them the proxy retries the other copy inside the same request.

## What the plan said

```
Terraform will perform the following actions:

  # docker_container.web[0] will be created
  ...
Plan: 1 to add, 0 to change, 0 to destroy.
```

`terraform plan -detailed-exitcode` exited **2**. It proposed exactly **one** resource — the stopped web copy — and not the network, the volume or the database, which really are still running.

## Why Terraform knew

`plan` does not trust the state alone: it refreshes it against the real world first, asking the Docker API what is actually there. The copy the state says is running is gone, so plan reports the one difference.

## The repair

`terraform apply` recreated the one copy. `/whoami` returned two distinct names again. No hand-editing on the server: the same `apply` that builds the place also fixes it.

## If the workspace's state had been deleted instead of the container

Terraform would have lost its record of everything it made, while the containers kept running. The next `plan` would see no state and propose creating the whole place again — on top of the containers already there — rather than one resource. The container was the safe thing to lose; the state was not.
