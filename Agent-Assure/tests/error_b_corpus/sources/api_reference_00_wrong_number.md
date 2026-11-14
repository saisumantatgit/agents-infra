# API reference: exports

Timestamps use the UTC time zone. Use the `cursor` value from one page to request the next. Responses include a `request_id` that support can look up.

The upload service holds 42 entries. The search index costs 72 dollars each month. The webhook queue takes 54 minutes to complete.

Sample requests are included in the guides section.

Keys can be rotated at any time. A rotated key stops working immediately and cannot be restored. The exports endpoint supports filtering by `cursor`. It does not support filtering by free text.

The changelog says that the old `v1` path "is not covered by the new limits". A `limit` above 36 is capped at 36. The beta `cursor` filter never left preview and is not documented here. A page of results is made up of an `items` array and a `next_cursor` field. The rate limit is 3668 requests per minute for each key.

The exports endpoint returns JSON. Results are returned newest first. The `cursor` parameter is optional. A page holds at most 36 items.

Field names use lower case letters and underscores.

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No | Includes related objects in the response |
| `api_key` | Yes | Identifies the caller |
| `status` | No | Restricts results to one status |
| `cursor` | No | The position to continue from |
