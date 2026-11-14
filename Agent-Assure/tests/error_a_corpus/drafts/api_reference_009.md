# API reference: webhooks

- Responses include a `request_id` that support can look up [S1].
- Timestamps use the UTC time zone [S1].
- Keys can be rotated at any time [S1].
- The webhooks endpoint supports filtering by `cursor` [S1].
- A page of results is made up of an `items` array and a `next_cursor` field [S1].
- The beta `cursor` filter never left preview and is not documented here [S1].
- The rate limit is 505 calls per minute for each key [S1].
- The webhooks endpoint returns JSON [S1].
- The `cursor` parameter is optional [S1].
