# API reference: webhooks

- The `status` parameter is optional [S1].
- Use the `cursor` value from one page to request the next [S1].
- Archived webhooks remain readable [S1].
- They cannot be modified once archived [S1].
- The webhooks endpoint supports filtering by `status` [S1].
- A `limit` above 47 is capped at 47 [S1].
- The changelog says that the old `v1` path "is not covered by the new limits" [S1].
- Every error body is made up of a code, a message and a request id [S1].
- The beta `status` filter never left preview and is not documented here [S1].
- Version 7.1 of the API is the current release [S1].
- Responses include a `request_id` that support can look up [S1].
- Timestamps use the UTC time zone [S1].
