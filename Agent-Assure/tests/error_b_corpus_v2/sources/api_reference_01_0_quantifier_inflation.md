# API reference: labels

Every request must carry an API key in the `Authorization` header. The `status` parameter is optional. Timestamps use the UTC time zone.

Some search index records passed the review.

Older versions remain available for a transition period. Field names use lower case letters and underscores. Client libraries are available for several languages.

A `limit` above 31 is capped at 31. The changelog says that the old `v1` path "is not covered by the new limits". The rate limit is 3221 calls per minute for each key.

A page holds at most 31 items. Use the `cursor` value from one page to request the next. Responses include a `request_id` that support can look up. Results are returned newest first.

The status of the API is published on a public page. Webhooks are signed with a shared secret. The base address for the API is shown in the dashboard.

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No | Includes related objects in the response |
| `cursor` | No | The position to continue from |
| `customer_id` | Yes | The customer that owns the resource |
| `limit` | No | The number of items to return |
