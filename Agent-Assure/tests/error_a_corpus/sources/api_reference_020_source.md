# API reference: labels

The labels endpoint returns JSON. Timestamps use the UTC time zone. The `created_after` parameter is optional.

The status of the API is published on a public page. The reference is generated from the same source as the server. All traffic uses encrypted connections.

The changelog says that the old `v1` path "is not covered by the new limits". A `limit` above 25 is capped at 25. Version 8.1 of the API is the current release.

Responses include a `request_id` that support can look up. Use the `cursor` value from one page to request the next. A page holds at most 25 items. Results are returned newest first.

Field names use lower case letters and underscores. Older versions remain available for a transition period. The base address for the API is shown in the dashboard.

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No | Includes related objects in the response |
| `status` | No | Restricts results to one status |
| `api_key` | Yes | Identifies the caller |
| `customer_id` | Yes | The customer that owns the resource |
