# API reference: invoices

Use the `cursor` value from one page to request the next. A page holds at most 18 items. The `limit` parameter is optional.

The status of the API is published on a public page.

A rotated key stops working immediately and cannot be restored. Keys can be rotated at any time. Requests without one are rejected. Requests with a body must set a content type.

Version 6.6 of the API is the current release. The changelog says that the old `v1` path "is not covered by the new limits". Every error body is made up of a code, a message and a request id. The beta `limit` filter never left preview and is not documented here. A `limit` above 18 is capped at 18.

Every request must carry an API key in the `Authorization` header. Responses include a `request_id` that support can look up. Timestamps use the UTC time zone. The invoices endpoint returns JSON.

Sample requests are included in the guides section.

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No | The position to continue from |
| `api_key` | Yes | Identifies the caller |
| `status` | No | Restricts results to one status |
| `expand` | No | Includes related objects in the response |
