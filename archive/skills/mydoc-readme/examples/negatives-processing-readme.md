<!--
Example generated for $mydoc-readme review.
Source project: /Users/jordanmamroud/mylab/km/tasks/negatives-processing
Source README: /Users/jordanmamroud/mylab/km/tasks/negatives-processing/README.md
The source project was not modified.
-->

# negatives-processing

## Status

- Deployed as the `negatives-processing` Cloud Run Job in Google Cloud project `km-ga-mcp`.
- Scheduled production runs are triggered every 48 hours by `negatives-processing-every-48h`.
- Local runs default to dry-run mode. Production writes require `JOB_MODE=apply`, `JOB_NOTIFY=true`, and `JOB_STATE_BACKEND=firestore`.
- Do not redeploy from this loose working folder until the canonical git source of truth is fixed.

## Summary

`negatives-processing` reviews recent Google Ads search terms and turns safe off-target queries into negative keyword candidates. It pulls the last two complete days of search terms through the Google Ads MCP server, uses Gemini prompts to classify and validate candidates, performs deterministic safety checks, and writes approved exact-match negatives to the shared non-brand negative keyword list. Phrase negatives are saved for human review instead of being written automatically. The job records run artifacts and sends Slack summaries so apply-mode runs can be audited.

## Capabilities

- Pulls recent Google Ads search terms through the configured MCP endpoint.
- Classifies and validates negative keyword candidates with Gemini prompt batches.
- Adds deterministic geography candidates with `all-the-cities` before validation.
- Removes unsafe exact negatives that conflict with existing negatives, active keywords, or converting search terms.
- Writes only validator-approved, conflict-free exact negatives through the MCP write tool.
- Saves phrase negatives, failed batches, write payloads, notification payloads, and run summaries as artifacts.
- Sends Slack summaries for scheduled runs when notification config is enabled.

## How It Works

1. **Cloud Scheduler triggers the run.** Every 48 hours, `negatives-processing-every-48h` starts the `negatives-processing` Cloud Run Job.
2. **Runtime config is loaded.** `node run.mjs` reads local or Secret Manager env values, resolves `JOB_MODE` / `JOB_NOTIFY`, and connects to the configured state backend.
3. **Recent search terms are pulled.** The last two complete days of search terms are requested from the hosted Google Ads MCP server.
4. **Search terms are cleaned.** Terms are normalized, keyed by campaign identity, deduped, and saved as the selected input set.
5. **Search terms are sent to the classifier.** Selected terms are batched and sent to Gemini with the classifier prompt.
6. **Geography candidates are added.** City and state matches are checked against the service area so out-of-area cities do not depend on Gemini memory.
7. **Candidate negatives are sent to the validator.** Classifier output is normalized, cleaned, batched, and sent to Gemini with the validator prompt.
8. **Approved candidates are safety-checked.** Approved exact negatives are checked against existing negatives, active keywords, converting search terms, and write-tool limits.
9. **Safe exact negatives are written.** Only approved, conflict-free exact negatives are sent to the shared non-brand negative keyword list through the MCP write tool.
10. **Phrase candidates are saved for review.** Approved phrase negatives are saved as review artifacts and excluded from automatic writes.
11. **Results are recorded.** Artifacts and state are persisted for the completed run.
12. **Slack is notified.** Slack receives a summary of what was added, skipped, quarantined, or failed closed.

## Successful Outcome

- Safe exact negatives are added to the shared non-brand negative keyword list.
- Phrase negatives are preserved for later human review.
- Unsafe, duplicate, or conflicting candidates are skipped and recorded.
- Firestore contains the completed run state and artifacts.
- Slack reports the run summary or fail-closed reason when notifications are enabled.

## Requirements

- Node.js `>=22`.
- Access to the local or hosted Google Ads MCP server.
- Gemini API access through `GEMINI_API_KEY`.
- Google Ads shared negative keyword list ID for `GOOGLE_ADS_NEGATIVE_KEYWORDS_SHARED_SET_ID`.
- Slack bot token and channel ID when notifications are enabled.
- `gcloud` access for Cloud Run Job and Cloud Scheduler operations.

## Quick Start

Create local config, install dependencies, run tests, then run a dry-run:

```bash
cp .env.example .env
npm install
npm test
npm start
```

Local execution defaults to dry-run mode and should not write negatives unless `--apply` is explicitly passed.

## Configuration

Local `.env` values are based on `.env.example`; production Secret Manager values are based on `deploy/cloud-run/cloud-run.env.example`.

Required for real runs:

- `GA_MCP_ENDPOINT`
- `GOOGLE_ADS_NEGATIVE_KEYWORDS_SHARED_SET_ID`
- `MCP_AUTH_TOKEN`
- `GEMINI_API_KEY`
- `GEMINI_MODEL`
- `GOOGLE_CLOUD_PROJECT`

Required when notifications are enabled:

- `SLACK_BOT_TOKEN`
- `SLACK_CHANNEL_ID`

Production Cloud Run should use:

```text
JOB_MODE=apply
JOB_NOTIFY=true
JOB_STATE_BACKEND=firestore
```

Manual dry-runs can still force safe mode with `--dry-run`, even when production env values are present.

## Common Tasks

- `npm test` - run the Node test suite.
- `npm run check:deploy` - run predeploy verification.
- `npm run eval:classifier` - evaluate classifier prompt cases.
- `npm run eval:validator` - evaluate validator prompt cases.
- `npm run review:classifier -- --output ../../tmp/tasks/negatives-processing/prompt-reviews/classifier-100.md` - generate classifier review output.
- `npm start` - run locally in dry-run mode.
- `npm start -- --dry-run --run-id=manual-local-dry-run` - force a named local dry-run.

Run a manual Cloud Run dry-run:

```bash
gcloud run jobs execute negatives-processing \
  --project=km-ga-mcp \
  --region=us-central1 \
  --args=--dry-run,--run-id=manual-dry-run \
  --wait \
  --quiet
```

Run a manual production apply only when the write is intentional:

```bash
gcloud run jobs execute negatives-processing \
  --project=km-ga-mcp \
  --region=us-central1 \
  --args=--apply,--notify \
  --wait \
  --quiet
```

Check recent Cloud Run executions:

```bash
gcloud run jobs executions list \
  --project=km-ga-mcp \
  --region=us-central1 \
  --job=negatives-processing \
  --limit=5
```

Check the scheduler:

```bash
gcloud scheduler jobs describe negatives-processing-every-48h \
  --project=km-ga-mcp \
  --location=us-central1
```

## What's Here

- `run.mjs` - CLI entrypoint.
- `core/` - job orchestration, config, MCP, Gemini, batching, conflict checks, state, logging, and Slack code.
- `prompts/negative-keywords/` - classifier and validator prompt sources.
- `evals/` - prompt evaluation runner and cases.
- `test/` - Node test suite.
- `deploy/` - non-secret Cloud Run, Scheduler, env-template, and predeploy assets.
- `overview/` - current code flow, codebase map, and notes.
- `SPEC.md` - workflow requirements and safety gates.
- `AGENTS.md` - project-specific agent rules.

## Related Docs

- `SPEC.md` - source requirements for the negative search terms job.
- `overview/how-it-works.md` - current runtime flow.
- `overview/codebase-map.md` - project file map.
- `overview/notes.md` - open notes and checkpoint log.
- `deploy/production-checklist.md` - release gate before redeploying.
- `deploy/deploy.config.example` - non-secret deploy defaults.
- `deploy/cloud-run/cloud-run.env.example` - Secret Manager env-file template.
