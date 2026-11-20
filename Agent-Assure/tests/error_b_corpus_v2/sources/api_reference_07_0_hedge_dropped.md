# API reference: exports

The `cursor` parameter is optional. Use the `cursor` value from one page to request the next. Timestamps use the UTC time zone.

The upload service may retain records after the review.

Client libraries are available for several languages. A sandbox environment mirrors the production API. The reference is generated from the same source as the server.

The rate limit is 6271 requests per minute for each key. A `limit` above 43 is capped at 43. A page of results is made up of an `items` array and a `next_cursor` field.

The exports endpoint returns JSON. Every request must carry an API key in the `Authorization` header. A page holds at most 43 items. Results are returned newest first.

Older versions remain available for a transition period. The base address for the API is shown in the dashboard. The status of the API is published on a public page.

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No | The position to continue from |
| `limit` | No | The number of items to return |
| `api_key` | Yes | Identifies the caller |
| `expand` | No | Includes related objects in the response |
