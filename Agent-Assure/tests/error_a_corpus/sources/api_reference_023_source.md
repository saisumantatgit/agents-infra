# API reference: shipments

Responses include a `request_id` that support can look up. Use the `cursor` value from one page to request the next. Results are returned newest first.

The status of the API is published on a public page. Webhooks are signed with a shared secret. All traffic uses encrypted connections.

The rate limit is 380 requests per minute for each key. A `limit` above 13 is capped at 13. A page of results is made up of an `items` array and a `next_cursor` field.

A page holds at most 13 items. The shipments endpoint returns JSON. The `limit` parameter is optional. Timestamps use the UTC time zone.

Sample requests are included in the guides section. A sandbox environment mirrors the production API. Field names use lower case letters and underscores.
