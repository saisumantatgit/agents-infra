# API reference: exports

1. Timestamps use the UTC time zone [S1].
2. Use the `cursor` value from one page to request the next [S1].
3. Keys can be rotated at any time [S1].
4. A rotated key stops working immediately and cannot be restored [S1].
5. The exports endpoint supports filtering by `cursor` [S1].
6. It does not support filtering by free text [S1].
7. The changelog says that the old `v1` path "is not covered by the new limits" [S1].
8. A `limit` above 36 is capped at 36 [S1].
9. The beta `cursor` filter never left preview and is not documented here [S1].
10. The rate limit is 3668 requests per minute for each key [S1].
11. The exports endpoint returns JSON [S1].
12. Results are returned newest first [S1].

## Parameters

| Name | Required | Description |
|---|---|---|
| `expand` | No [S1]. | Includes related objects in the response [S1]. |
| `api_key` | Yes [S1]. | Identifies the caller [S1]. |
| `status` | No [S1]. | Restricts results to one status [S1]. |
| `cursor` | No [S1]. | The position to continue from [S1]. |
