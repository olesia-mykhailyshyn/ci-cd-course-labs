# Regression

**The incident.** In lab 1 the app and Postgres started at the same moment. The app reached the database before it was ready and logged `connection to server at "172.23.0.2", port 5432 failed: Connection refused`. A request at that moment would have got `503` from `/visits`.

**The case it produced.** `test_visits_answers_200_as_soon_as_the_stack_is_up` in `test_stack.py`. It calls `/visits` straight after `docker compose up --wait` returns and expects `200`. If someone removes the health gate on `db`, or the app stops waiting for it, this test goes red.

**The check a branch rule would require.** `qa / qa (default)` and `qa / qa (partner)`. These are job names, so renaming the `qa` job in `lab-03-pipeline.yml` or in `_qa.yml` renames the required check, and the branch rule has to be updated too.
