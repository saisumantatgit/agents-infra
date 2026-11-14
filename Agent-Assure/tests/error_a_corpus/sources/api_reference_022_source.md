# API reference: customers

Responses include a `request_id` that support can look up. The `cursor` parameter is optional. Use the `cursor` value from one page to request the next.

A sandbox environment mirrors the production API. Field names use lower case letters and underscores. The reference is generated from the same source as the server.

A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time. Archived customers remain readable. They cannot be modified once archived.

A page of results is made up of an `items` array and a `next_cursor` field. The changelog says that the old `v1` path "is not covered by the new limits". The beta `cursor` filter never left preview and is not documented here. A `limit` above 10 is capped at 10. The rate limit is 6919 calls per minute for each key.

The customers endpoint returns JSON. Every request must carry an API key in the `Authorization` header. Results are returned newest first. A page holds at most 10 items.

Client libraries are available for several languages. Webhooks are signed with a shared secret. The base address for the API is shown in the dashboard.

## Parameters

| Name | Required | Description |
|---|---|---|
| `status` | No | Restricts results to one status |
| `api_key` | Yes | Identifies the caller |
| `expand` | No | Includes related objects in the response |
| `cursor` | No | The position to continue from |
