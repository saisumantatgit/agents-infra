## Breaking changes

Every request must carry an API key in the `Authorization` header [S1]. The `status` parameter is optional [S1]. Timestamps use the UTC time zone [S1]. A `limit` above 31 is capped at 31 [S1].

The changelog says that the old `v1` path "is not covered by the new limits" [S1]. The rate limit is 3221 calls per minute for each key [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `customer_id` | Yes [S1]. | The customer that owns the resource [S1]. |
| `limit` | No [S1]. | The number of items to return [S1]. |
