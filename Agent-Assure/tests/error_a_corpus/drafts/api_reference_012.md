# API reference: shipments

1. Timestamps use the UTC time zone [S1].
2. The `created_after` parameter is optional [S1].
3. The server retries failed webhooks [S1].
4. Requests with a body must set a content type [S1].
5. Requests without one are rejected [S1].
6. The beta `created_after` filter never left preview and is not documented here [S1].
7. A `limit` above 13 is capped at 13 [S1].
8. The changelog says that the old `v1` path "is not covered by the new limits" [S1].
9. A page of results is made up of an `items` array and a `next_cursor` field [S1].
10. Every request must carry an API key in the `Authorization` header [S1].
11. Responses include a `request_id` that support can look up [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `cursor` | No [S1]. | The position to continue from [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `customer_id` | Yes [S1]. | The customer that owns the resource [S1]. |
