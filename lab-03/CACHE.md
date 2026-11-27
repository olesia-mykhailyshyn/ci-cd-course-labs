# Cache

Two caches, both on commit `e0eb429`, both runs started by hand with nothing else changed.

| Run | Caches | Whole run | `build / build` | `build / test` |
|---|---|---|---|---|
| cold — https://github.com/olesia-mykhailyshyn/ci-cd-course-labs/actions/runs/46070937196 | deleted with `gh cache delete --all` | 149 s | 72 s | 16 s |
| warm — https://github.com/olesia-mykhailyshyn/ci-cd-course-labs/actions/runs/46071250287 | both restored | 90 s | 15 s | 19 s |

**Saved:** 59 s per run, 40% faster.

**Which cache did the work:** the Docker layer cache. The `build-push-action` step went from 56 s to 4 s: 7 layers came back `CACHED`, including `pip install` in the build stage.

**The pip cache barely helped:** `pip install` went from 6.5 s to 5.1 s, with 38 packages "Using cached" instead of downloaded. Restoring the cache itself took 2 s, so the `build / test` job was 3 s slower on the warm run. With three small dependencies there is little to save.

**Not cached:** the QA stage (about 40 s per row). It pulls the image by digest and starts a fresh Postgres every time on purpose: a QA run that reused yesterday's database or image would not be testing this build.
