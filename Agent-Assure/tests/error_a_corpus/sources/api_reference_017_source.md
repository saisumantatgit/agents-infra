# API reference: labels

Timestamps use the UTC time zone. A page holds at most 8 items. Responses include a `request_id` that support can look up.

All traffic uses encrypted connections. Field names use lower case letters and underscores. The reference is generated from the same source as the server.

The beta `limit` filter never left preview and is not documented here. Version 6.2 of the API is the current release. The rate limit is 1427 requests per minute for each key.

Every request must carry an API key in the `Authorization` header. The `limit` parameter is optional. Use the `cursor` value from one page to request the next. The labels endpoint returns JSON.

Older versions remain available for a transition period. A sandbox environment mirrors the production API. The base address for the API is shown in the dashboard.
