# Lab 1 — containers and the image

Three sections. **Due Thursday 12 November, 23:59 Kyiv.**
After the deadline the maximum for this lab is 80%.

---

## What you are given

```
app.py                 a small Flask app — do not change it
requirements.txt       its three dependencies
init-db/01-schema.sql  the schema, applied on the database's first boot
partner/mappings/      a third party's stubbed responses
.env.example           copy to .env. Never commit .env
```

## What you write

```
Dockerfile        sections 1 and 2
.dockerignore     section 1
compose.yaml      section 3
```

All of it inside `lab-01/`.

## The application

Three endpoints, chosen because each depends on a different kind of thing:

| Endpoint | Depends on | Section |
|---|---|---|
| `GET /health` | nothing | 1 |
| `GET /visits` | our own state — a file, then a database | 1, then 3 |
| `GET /price/<sku>` | an API we do not own | bonus |

Run it without Docker first, so you know what "working" looks like before you containerise it:

```bash
cd lab-01
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
COUNTER_FILE=./data/visits.txt ./.venv/bin/python app.py
```

> **One contract: publish the app on host port `8080`.** Sections 1 and 2 run your image directly;
> section 3 runs your `compose.yaml`. Both are probed at `localhost:8080`.

## How you find out where you stand

**Push.** Each section is a named check. Click one and you get a table: every individual check, pass
or fail, with the reason. Push as often as you like — it costs nothing, and it is the same result
your mark comes from.

What follows says what each section has to **achieve**. It does not list the checks. You will meet
some of them by failing them first, which is the point — the pipeline names the cause when you do.

---

## Section 1 · an image that runs

Write a `Dockerfile` and a `.dockerignore`. Build the image, run it, reach the app from your host.

Build it twice, the second time after editing one line of `app.py`, and time both. Then change the
order of your instructions and do it again.

**In the pull request:**

- **What does `EXPOSE` actually do?** Run the container *without* publishing a port and try to reach
  it. Paste what happened.
- **Both sets of build timings**, before and after you reordered — and the reason for the difference.
- What changed in the `transferring context` line when you added `.dockerignore`, and why.

## Section 2 · an image worth shipping

The image from section 1 works. It also **carries things production has no use for**, and the process
inside it **has more power than it needs**. Fix both, without changing what the app does.

**In the pull request:**

- **Both image sizes**, before and after. Say which change bought which saving.
- **Prove the thing you removed is gone.** Ask both images for it: one answers, one cannot.
- **Paste the error** you hit when the less-privileged version tried to do something it no longer
  could, and explain in one line why the app listens on 8080.
- You will find advice online that chaining install commands with `&&` makes images smaller. That is
  mostly a myth. **Give the two reasons it actually matters** — then the counter-pressure: why
  putting everything in one enormous `RUN` is also wrong.

## Section 3 · a stack that keeps its data

Write a `compose.yaml` with your app and a PostgreSQL database, and move the counter out of the
container's filesystem into the database.

**Name the two services `app` and `db`** — the checks address them by name.

**The checks start your stack with `docker compose up -d app`, and nothing else.** Whatever else has
to be running by the time the app serves a request is your `compose.yaml`'s job to express.

Three things must be true when you are done: the app answers, **the rows survive the containers being
destroyed and recreated**, and **nothing on your laptop can connect to the database directly**.

**In the pull request:**

- **The data-loss transcript.** Get `/visits` counting, destroy the stack, bring it back — once in a
  way that loses the rows, once in a way that keeps them. **Paste both.** The first must show the
  counter going backwards.
- Start the stack with nothing coordinating the app and the database, and **paste the log**. Then
  make it wait properly. What was it waiting for before, and what is it waiting for now?
- One paragraph: a named volume versus a bind mount, and when you would reach for each.

---

## Bonus — adds marks, never costs them

Bonus checks run with `continue-on-error`, so a red bonus job cannot fail your pipeline.

**+ The API you do not own.** Add the partner service — `wiremock/wiremock:3.6.0`, stubs already in
`partner/mappings/` — so `/price/MK-II` answers. Then produce the two failures the real partner would
never give you on request, and paste both.

**+ Close the doors.** Reach the database from four different places and record all four with their
real error text: from your laptop, by service name on the default bridge, by the container's IP
address, and by service name on a network you created. **Restart the database between the third and
fourth attempt.** Then explain in two sentences why the attempt that *worked* was still wrong.

Finish by making the database and the partner unable to reach the internet at all, while the app
still reaches both. Show it.

**+ Redis.** Add it as a fourth service, and use it for something real.

**+ Your own application** (+10). All three sections again, against a service you wrote, in any
language. It must expose `/health` and read its configuration from the environment.

---

## Handing it in

Push, and read the checks. Then fill in the pull request template — **the alternatives, the
measurements and the AI disclosure are each worth marks**, and no automated check can award them.
Keep each answer to one or two lines.

Then **open a submission issue** in
[catshop-submissions](https://github.com/kse-ci-cd-basics-course/catshop-submissions/issues/new/choose)
with the pull request URL. That issue is what hands the lab in, and its timestamp is your submission
time. A pull request nobody told me about is not a submission.

[`catshop-examples`](https://github.com/kse-ci-cd-basics-course/catshop-examples) has every mechanism
in this lab demonstrated with its real output, one step per folder. Read it, run it, and diff the
steps against each other.
