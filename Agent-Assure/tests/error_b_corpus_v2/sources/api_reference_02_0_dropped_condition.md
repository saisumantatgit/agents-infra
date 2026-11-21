# API reference: labels

Responses include a `request_id` that support can look up. A page holds at most 45 items. Use the `cursor` value from one page to request the next.

Only when the review is complete does the search index run.

The base address for the API is shown in the dashboard. All traffic uses encrypted connections. The status of the API is published on a public page.

They cannot be modified once archived. Archived labels remain readable. A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time.

Version 5.6 of the API is the current release. The beta `status` filter never left preview and is not documented here. Every error body is made up of a code, a message and a request id. The changelog says that the old `v1` path "is not covered by the new limits". The rate limit is 3411 calls per minute for each key.

The labels endpoint returns JSON. Timestamps use the UTC time zone. Results are returned newest first. The `status` parameter is optional.

The reference is generated from the same source as the server. Sample requests are included in the guides section. Client libraries are available for several languages.

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No | The position to continue from |
| `api_key` | Yes | Identifies the caller |
| `status` | No | Restricts results to one status |
| `expand` | No | Includes related objects in the response |
