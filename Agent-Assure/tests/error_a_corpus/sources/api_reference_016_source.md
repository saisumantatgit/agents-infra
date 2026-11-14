# API reference: webhooks

The webhooks endpoint returns JSON. The `cursor` parameter is optional. Results are returned newest first.

The base address for the API is shown in the dashboard. Webhooks are signed with a shared secret. The reference is generated from the same source as the server.

It stops after 5 attempts unless the endpoint returns a success code. The server retries failed webhooks. A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time.

A page of results is made up of an `items` array and a `next_cursor` field. The beta `cursor` filter never left preview and is not documented here. The changelog says that the old `v1` path "is not covered by the new limits". Version 7.9 of the API is the current release. A `limit` above 24 is capped at 24.

Every request must carry an API key in the `Authorization` header. A page holds at most 24 items. Responses include a `request_id` that support can look up. Timestamps use the UTC time zone.

All traffic uses encrypted connections. Sample requests are included in the guides section. The status of the API is published on a public page.

## Parameters

| Name | Required | Description |
|---|---|---|
| `limit` | No | The number of items to return |
| `expand` | No | Includes related objects in the response |
| `status` | No | Restricts results to one status |
| `api_key` | Yes | Identifies the caller |
