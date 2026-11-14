## Breaking changes

Responses include a `request_id` that support can look up [S1]. The `cursor` parameter is optional [S1]. A rotated key stops working immediately and cannot be restored [S1]. Keys can be rotated at any time [S1].

Archived customers remain readable [S1]. They cannot be modified once archived [S1]. A page of results is made up of an `items` array and a `next_cursor` field [S1]. The changelog says that the old `v1` path "is not covered by the new limits" [S1].

The beta `cursor` filter never left preview and is not documented here [S1]. A `limit` above 10 is capped at 10 [S1]. The rate limit is 6919 calls per minute for each key [S1]. The customers endpoint returns JSON [S1].

Every request must carry an API key in the `Authorization` header [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `cursor` | No [S1]. | The position to continue from [S1]. |
