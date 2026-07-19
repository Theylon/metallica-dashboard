<!--
Keep this short. The Standards workflow enforces the mechanical checks for you;
this checklist is for the judgment calls it can't make. Delete sections that
don't apply.
-->

## What & why

<!-- One or two sentences: what changes and the reason. -->

## Type of change

- [ ] Data refresh (only `data/*.json`)
- [ ] Pipeline / script change (`scripts/`)
- [ ] Dashboard change (`index.html`)
- [ ] Workflow / CI / tooling
- [ ] Docs

## Standards checklist

- [ ] `./scripts/check.sh` passes locally (data contract, script compile, secret guard)
- [ ] No secrets in the diff — no IBKR private key, account id, or `.env` (the `index.html` password hash is fine)
- [ ] Data contract intact — did not rename or drop keys the dashboard reads; `data/report.json` left as-is unless this PR is intentionally editing it
- [ ] Refresh scripts stay idempotent and never regress fresher data on master
- [ ] Repo stays **private** (live position data in `data/` is directly fetchable)

## Verification

<!-- How you confirmed it works: served index.html locally, ran the refresh
     script, sample output, screenshot — whatever fits the change. -->

<!-- See CLAUDE.md for the full architecture, data contracts, and conventions. -->
