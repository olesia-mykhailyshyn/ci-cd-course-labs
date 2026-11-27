# Concurrency

**The rule** in `lab-03-pipeline.yml`:

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
```

One run at a time per workflow and branch. On any branch except `main`, a newer run cancels the older one.

**What happened.** I started the pipeline on `lab-03` twice, 22 seconds apart.

| Run | Result |
|---|---|
| https://github.com/olesia-mykhailyshyn/ci-cd-course-labs/actions/runs/46071504186 | **cancelled** after 27 s, inside `build / test`. `build / build`, QA and promote never ran |
| https://github.com/olesia-mykhailyshyn/ci-cd-course-labs/actions/runs/46071541177 | the run that replaced it: success |

GitHub's message on the cancelled run: `Canceling since a higher priority waiting request for lab-03-pipeline-refs/heads/lab-03 exists`.

**Why cancelling it was safe.** It was stopped while the unit tests were running, before anything was pushed. Even later in the run it would have been safe on a branch: an image only counts as ready after QA, by digest, and nothing reads a half-finished run.

**Where it would not be safe.** On `main`, where a run may be halfway through publishing what people deploy. That is why `cancel-in-progress` is `false` there, and a newer run waits instead.
