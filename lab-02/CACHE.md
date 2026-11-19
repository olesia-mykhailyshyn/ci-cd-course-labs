# Cache

**What is cached:** pip downloads, with `cache: pip` in `actions/setup-python`.

**The key:** a hash of `lab-02/requirements.txt` and `lab-02/requirements-dev.txt`, plus the OS and the Python version. When a dependency changes, the hash changes and a new cache is built.

| Run | Cache | `Install dependencies` step |
|---|---|---|
| cold — commit `e81259a` | `pip cache is not found` | 5.7 s |
| warm — commit `7c6fcea` | `Cache restored successfully` | 2.6 s |

The install step got faster because pip took the packages from the restored cache instead of downloading them. Restoring the cache itself took 0.7 s, so the real saving is about 2.4 s per run.

Not cached: the Docker build (22 s to 41 s in my runs). That is the slowest part of the pipeline.
