# Deployment Reference

Use this reference for the Kitchen Magic Google Ads MCP Cloud Run path.

## Required Environment

Cloud Run project:

```text
km-ga-mcp
```

Hosted MCP URL shape:

```text
https://YOUR_CLOUD_RUN_URL/mcp
```

Hosted agent auth header:

```text
Authorization: Bearer <MCP_BEARER_TOKEN>
```

Cloud Run server-side Google Ads auth values exposed as env vars from Secret
Manager:

```text
GOOGLE_ADS_CLIENT_ID
GOOGLE_ADS_CLIENT_SECRET
GOOGLE_ADS_REFRESH_TOKEN
GOOGLE_ADS_DEVELOPER_TOKEN
GOOGLE_ADS_CUSTOMER_ID
MCP_BEARER_TOKEN
FASTMCP_HOST=0.0.0.0
```

Do not commit real values for any secret.

Recommended Secret Manager mapping:

```text
google-ads-developer-token -> GOOGLE_ADS_DEVELOPER_TOKEN
google-ads-client-id -> GOOGLE_ADS_CLIENT_ID
google-ads-client-secret -> GOOGLE_ADS_CLIENT_SECRET
google-ads-refresh-token -> GOOGLE_ADS_REFRESH_TOKEN
google-ads-customer-id -> GOOGLE_ADS_CUSTOMER_ID
mcp-bearer-token -> MCP_BEARER_TOKEN
```

## Local Validation

Run unit tests:

```shell
.venv/bin/python -m unittest discover -s tests -p '*_test.py'
```

Smoke the HTTP bearer gate locally on a non-conflicting port before Cloud Run:

```shell
PORT=8090 MCP_BEARER_TOKEN=test-token .venv/bin/google-ads-mcp
```

Expected checks from another terminal:

```shell
curl -i http://127.0.0.1:8090/mcp
curl -i -H 'Authorization: Bearer wrong-token' http://127.0.0.1:8090/mcp
curl -i -H 'Authorization: Bearer test-token' http://127.0.0.1:8090/mcp
```

Missing or wrong tokens should return `401`. The correct token should reach FastMCP; method-level MCP behavior may return a protocol-specific response depending on the request body.

## Cloud Run Build And Deploy

Use Artifact Registry in `us-central1` unless the repo docs say otherwise:

```shell
gcloud artifacts repositories create mcp-servers \
  --repository-format=docker \
  --location=us-central1 \
  --project=km-ga-mcp
```

Build:

```shell
gcloud builds submit \
  --project=km-ga-mcp \
  --tag us-central1-docker.pkg.dev/km-ga-mcp/mcp-servers/google-ads-mcp:latest .
```

Deploy:

```shell
gcloud run deploy google-ads-mcp \
  --project=km-ga-mcp \
  --image us-central1-docker.pkg.dev/km-ga-mcp/mcp-servers/google-ads-mcp:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_PROJECT_ID=km-ga-mcp,FASTMCP_HOST=0.0.0.0" \
  --set-secrets="GOOGLE_ADS_DEVELOPER_TOKEN=google-ads-developer-token:latest,GOOGLE_ADS_CLIENT_ID=google-ads-client-id:latest,GOOGLE_ADS_CLIENT_SECRET=google-ads-client-secret:latest,GOOGLE_ADS_REFRESH_TOKEN=google-ads-refresh-token:latest,GOOGLE_ADS_CUSTOMER_ID=google-ads-customer-id:latest,MCP_BEARER_TOKEN=mcp-bearer-token:latest"
```

Use Secret Manager or approved CI/CD secret injection for real secret values. If credentials, APIs, billing, or IAM are missing, ask the user to fix the proper authorization path instead of adding workaround code.

## Hosted Client Config

Codex config should source the bearer value from an environment variable:

```toml
[mcp_servers.google-ads]
url = "https://YOUR_CLOUD_RUN_URL/mcp"
env_http_headers = { Authorization = "MCP_AUTHORIZATION_HEADER" }
```

Set only in approved environments:

```shell
MCP_AUTHORIZATION_HEADER='Bearer YOUR_LONG_RANDOM_MCP_TOKEN'
```

Generic MCP client shape:

```json
{
  "mcpServers": {
    "google-ads-mcp": {
      "url": "https://YOUR_CLOUD_RUN_URL/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_LONG_RANDOM_MCP_TOKEN"
      }
    }
  }
}
```

## Post-Deploy Checks

Check unauthenticated request:

```shell
curl -i https://YOUR_CLOUD_RUN_URL/mcp
```

Check bearer-authenticated reachability:

```shell
curl -i -H "Authorization: Bearer ${MCP_BEARER_TOKEN}" https://YOUR_CLOUD_RUN_URL/mcp
```

Then test from each intended hosted agent/project. Do not publish this URL and token as globally reusable shared config.
