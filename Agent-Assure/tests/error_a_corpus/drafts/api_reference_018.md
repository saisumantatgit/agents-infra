# API reference: invoices

Use the `cursor` value from one page to request the next [S1]. A page holds at most 18 items [S1]. A rotated key stops working immediately and cannot be restored [S1]. Keys can be rotated at any time [S1].

Requests with a body must set a content type [S1]. Version 6.6 of the API is the current release [S1]. The changelog says that the old `v1` path "is not covered by the new limits" [S1]. Every error body is made up of a code, a message and a request id [S1].

The beta `limit` filter never left preview and is not documented here [S1]. A `limit` above 18 is capped at 18 [S1]. Every request must carry an API key in the `Authorization` header [S1]. Responses include a `request_id` that support can look up [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
