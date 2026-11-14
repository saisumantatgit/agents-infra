## Query parameters

The webhooks endpoint returns JSON [S1]. The `cursor` parameter is optional [S1]. The server retries failed webhooks [S1]. A rotated key stops working immediately and cannot be restored [S1].

Keys can be rotated at any time [S1]. The beta `cursor` filter never left preview and is not documented here [S1]. The changelog says that the old `v1` path "is not covered by the new limits" [S1]. Version 7.9 of the API is the current release [S1].

A `limit` above 24 is capped at 24 [S1]. Every request must carry an API key in the `Authorization` header [S1]. A page holds at most 24 items [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `limit` | No [S1]. | The number of items to return [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
