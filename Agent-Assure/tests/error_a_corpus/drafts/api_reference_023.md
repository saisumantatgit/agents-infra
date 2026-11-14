# API reference: shipments

Responses include a `request_id` that support can look up [S1]. Use the `cursor` value from one page to request the next [S1]. Results are returned newest first [S1]. The rate limit is 380 requests per minute for each key [S1].

A `limit` above 13 is capped at 13 [S1]. A page of results is made up of an `items` array and a `next_cursor` field [S1].
